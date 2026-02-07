import json
import os
from datetime import datetime

# -----------------------------
# Data File
# -----------------------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "appointments.json")

# -----------------------------
# Doctors
# -----------------------------
DOCTORS = [
    {"id": 1, "name": "Dr. Kumar", "hospital": "City Hospital"},
    {"id": 2, "name": "Dr. Anjali", "hospital": "Skin Care Clinic"},
    {"id": 3, "name": "Dr. Mehta", "hospital": "Dermatology Center"},
    {"id": 4, "name": "Dr. Singh", "hospital": "Health First Hospital"},
    {"id": 5, "name": "Dr. Rao", "hospital": "Wellness Hospital"}
]

TIMES = ["10:00 AM", "11:30 AM", "02:00 PM", "04:00 PM"]

# -----------------------------
# Disease Knowledge Base
# -----------------------------
DISEASE_INFO = {

    "Eczema":
        "Eczema is a skin condition causing dryness, itching, and inflammation. "
        "It may be triggered by allergens, stress, or irritants.",

    "Melanoma":
        "Melanoma is a serious form of skin cancer that develops from pigment cells. "
        "Early detection is very important.",

    "Ringworm":
        "Ringworm is a contagious fungal infection causing circular rashes.",

    "Nevus":
        "Nevus is a mole — usually harmless but should be monitored for changes.",

    "Benign_Keratosis":
        "Benign keratosis is a non-cancerous skin growth common with aging."
}

PRECAUTIONS = {

    "Eczema":
        [
            "Keep skin moisturized",
            "Avoid harsh soaps",
            "Use fragrance-free products",
            "Avoid scratching"
        ],

    "Melanoma":
        [
            "Avoid direct sun exposure",
            "Use sunscreen SPF 50+",
            "Check mole changes",
            "Consult dermatologist immediately"
        ],

    "Ringworm":
        [
            "Keep area dry",
            "Do not share towels",
            "Use antifungal creams",
            "Wash clothes separately"
        ],

    "Nevus":
        [
            "Monitor size and color",
            "Avoid excessive sun",
            "Dermatology check yearly"
        ],

    "Benign_Keratosis":
        [
            "Avoid irritation",
            "Do not scratch",
            "Medical removal if needed"
        ]
}

# -----------------------------
# Session (demo single-user)
# -----------------------------
SESSION = {
    "step": "idle",
    "doctor": None
}

# -----------------------------
# Utilities
# -----------------------------
def load_appointments():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_appointments(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# Chatbot Logic
# -----------------------------
def chatbot_response(disease, message, username="Guest"):
    global SESSION
    msg = message.lower().strip()

    # ---------- CANCEL USER APPOINTMENT ----------
    if "cancel" in msg:

        appointments = load_appointments()
        user_appts = [a for a in appointments if a.get("booked_by")==username]

        if not user_appts:
            return "❌ You have no appointments to cancel."

        last_user_appt = user_appts[-1]
        appointments.remove(last_user_appt)
        save_appointments(appointments)

        SESSION["step"] = "idle"
        SESSION["doctor"] = None

        return (
            "🗑️ Appointment Cancelled\n\n"
            f"Doctor: {last_user_appt['doctor']}\n"
            f"Time: {last_user_appt['time']}\n"
            f"Booked By: {username}"
        )

    # ---------- GREETING ----------
    if msg in ["hi","hello","start","restart"]:

        SESSION["step"] = "idle"
        SESSION["doctor"] = None

        return (
            f"Hello {username} 👋\n\n"
            f"Detected condition: **{disease}**\n\n"
            "How can I help you?\n"
            "1️⃣ About the condition\n"
            "2️⃣ Precautions\n"
            "3️⃣ Book dermatologist appointment\n"
            "Type **cancel** to cancel appointment"
        )

    # ---------- DOCTOR STEP ----------
    if SESSION["step"] == "doctor":
        if msg.isdigit():
            doctor = next((d for d in DOCTORS if d["id"] == int(msg)), None)
            if doctor:
                SESSION["doctor"] = doctor
                SESSION["step"] = "time"

                return (
                    f"Selected {doctor['name']} — {doctor['hospital']}\n\n"
                    "Available time slots:\n" +
                    "\n".join(TIMES)
                )

        return "⚠️ Please enter valid doctor number."

    # ---------- TIME STEP ----------
    if SESSION["step"] == "time":

        for t in TIMES:
            if msg.replace(" ","") == t.lower().replace(" ",""):

                appt = {
                    "doctor": SESSION["doctor"]["name"],
                    "hospital": SESSION["doctor"]["hospital"],
                    "disease": disease,
                    "time": t,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "booked_by": username
                }

                data = load_appointments()
                data.append(appt)
                save_appointments(data)

                SESSION["step"] = "idle"
                SESSION["doctor"] = None

                return (
                    "✅ Appointment Confirmed\n\n"
                    f"Doctor: {appt['doctor']}\n"
                    f"Hospital: {appt['hospital']}\n"
                    f"Time: {appt['time']}\n"
                    f"Booked By: {username}"
                )

        return "⚠️ Invalid time slot."

    # ---------- ABOUT DISEASE ----------
    if msg == "1":
        info = DISEASE_INFO.get(disease,"No info available")
        return f"🩺 About {disease}:\n\n{info}"

    # ---------- PRECAUTIONS ----------
    if msg == "2":
        tips = PRECAUTIONS.get(disease,["Consult dermatologist"])
        return "🧴 Precautions:\n\n" + "\n".join([f"• {t}" for t in tips])

    # ---------- BOOK ----------
    if msg == "3":
        SESSION["step"] = "doctor"
        return "Select Doctor:\n" + "\n".join(
            [f"{d['id']}. {d['name']} — {d['hospital']}" for d in DOCTORS]
        )

    return "Reply 1 / 2 / 3 or type cancel"
