import sys
import os
import sqlite3
import base64
import cv2
import numpy as np
import tensorflow as tf

from fastapi import FastAPI, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext


from explainability.gradcam import generate_gradcam
from chatbot.medical_bot import chatbot_response
# -------- DATABASE PATH --------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "users.db")

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- PATH FIX ----------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ---------------- APP ----------------
app = FastAPI(title="AI Skin Disease Diagnosis API")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- PASSWORD HASHER ----------------
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- CONFIG ----------------
IMG_SIZE = 224
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "models", "efficientnet", "efficientnet_model.h5")

CLASSES = [
    "Benign_Keratosis",
    "Eczema",
    "Melanoma",
    "Nevus",
    "Ringworm"
]

# ---------------- LOAD MODEL ----------------
model = tf.keras.models.load_model(MODEL_PATH)

# ---------------- IMAGE UTILS ----------------
def decode_image(image_bytes):
    img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def preprocess_image(img):
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0
    return np.expand_dims(img, axis=0)

# ---------------- SKIN CHECK ----------------
def is_skin_image(image_rgb, min_ratio=0.18):
    img = cv2.GaussianBlur(image_rgb, (5, 5), 0)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)

    mask = cv2.inRange(
        ycrcb,
        np.array([0,140,85]),
        np.array([255,175,135])
    )

    return cv2.countNonZero(mask) / (image_rgb.shape[0]*image_rgb.shape[1]) >= min_ratio

# ---------------- HEATMAP ----------------
def overlay_heatmap(heatmap, image):
    heatmap = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    image = np.uint8(image[0] * 255)
    overlay = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)

    _, buf = cv2.imencode(".jpg", overlay)
    return base64.b64encode(buf).decode()

# ---------------- PREDICT ----------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    img_bytes = await file.read()
    original = decode_image(img_bytes)

    if not is_skin_image(original):
        return {"status":"rejected","message":"Not a skin image"}

    image = preprocess_image(original)
    preds = model.predict(image)[0]

    top = preds.argsort()[-3:][::-1]

    top_predictions = [
        {"disease":CLASSES[i],"confidence":round(float(preds[i])*100,2)}
        for i in top
    ]

    heatmap = generate_gradcam(model, image, int(top[0]))
    gradcam_img = overlay_heatmap(heatmap, image)

    return {
        "status":"ok",
        "top_predictions": top_predictions,
        "gradcam": gradcam_img
    }

# ---------------- CHAT ----------------
class ChatRequest(BaseModel):
    disease: str
    message: str
    username: str

@app.post("/chat")
async def chat(req: ChatRequest):
    reply = chatbot_response(req.disease, req.message, req.username)
    return {"reply": reply}

# ---------------- LOGIN ----------------
class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginData):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT password FROM users WHERE username=?", (data.username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "User not found"}

    if pwd.verify(data.password, row[0]):
        return {
            "access_token": "demo_token",
            "username": data.username
        }

    return {"error": "Invalid password"}


# ---------------- PROFILE ----------------
@app.get("/me")
def get_profile(username: str = Header(None)):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, full_name, email, role, phone, family_doctor
        FROM users
        WHERE username=?
    """, (username,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error":"User not found"}

    return {
        "id": row[0],
        "username": row[1],
        "full_name": row[2],
        "email": row[3],
        "role": row[4],
        "phone": row[5],
        "family_doctor": row[6]
    }
