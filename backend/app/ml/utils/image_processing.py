import cv2
import numpy as np
from typing import Tuple


def preprocess_image(image_bytes: bytes, target_size: Tuple[int, int] = (640, 640)) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, target_size)
    img = img.astype(np.float32) / 255.0
    return img


def extract_leaf_segments(image: np.ndarray) -> list:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (30, 20, 20), (85, 255, 255))
    kernel = np.ones((5, 5), np.uint8)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def calculate_disease_area(image: np.ndarray, mask: np.ndarray) -> float:
    total_pixels = image.shape[0] * image.shape[1]
    disease_pixels = np.count_nonzero(mask)
    return (disease_pixels / total_pixels) * 100


def enhance_image(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
