import cv2
import os
import numpy as np
from tqdm import tqdm

IMG_SIZE = 224

RAW_DIR = "../../dataset/raw"
DATASET_DIR = r"C:\Users\kisho\Skin_Disease_AI\dataset\processed"


CLASSES = [
    "Eczema",   
    "Nevus",
    "Melanoma",
    "Ringworm",
    "Benign_Keratosis"
]

def preprocess_image(img_path):
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize
    image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))

    # Denoising
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Normalize
    image = image / 255.0

    return image


def create_dirs():
    for cls in CLASSES:
        os.makedirs(os.path.join(PROCESSED_DIR, cls), exist_ok=True)


def process_dataset():
    create_dirs()

    for cls in CLASSES:
        input_path = os.path.join(RAW_DIR, cls)
        output_path = os.path.join(PROCESSED_DIR, cls)

        for img_name in tqdm(os.listdir(input_path), desc=f"Processing {cls}"):
            img_path = os.path.join(input_path, img_name)

            try:
                image = preprocess_image(img_path)
                save_path = os.path.join(output_path, img_name)
                cv2.imwrite(save_path, (image * 255).astype(np.uint8))
            except:
                print(f"Error processing {img_path}")


if __name__ == "__main__":
    process_dataset()
