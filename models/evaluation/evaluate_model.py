import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------------- CONFIG ----------------
IMG_SIZE = 224
BATCH_SIZE = 8

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATASET_DIR = os.path.join(BASE_DIR, "dataset", "processed")
MODEL_PATH = os.path.join(BASE_DIR, "models", "efficientnet", "efficientnet_model.h5")

CLASSES = [
    "Eczema",   
    "Nevus",
    "Melanoma",
    "Ringworm",
    "Benign_Keratosis"    
]

# ---------------- LOAD MODEL ----------------
model = tf.keras.models.load_model(MODEL_PATH)

# ---------------- DATA LOADER ----------------
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

test_data = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# ---------------- PREDICTION ----------------
y_true = test_data.classes
y_pred_probs = model.predict(test_data)
y_pred = np.argmax(y_pred_probs, axis=1)

# ---------------- CLASSIFICATION REPORT ----------------
print("\nClassification Report:\n")
print(classification_report(y_true, y_pred, target_names=CLASSES))

# ---------------- CONFUSION MATRIX ----------------
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d",
            xticklabels=CLASSES,
            yticklabels=CLASSES,
            cmap="Blues")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")
plt.show()
