from typing import Tuple, Optional
import struct


def _cv2():
    import cv2
    return cv2


MAGIC_BYTES: dict[bytes, str] = {
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"RIFF": "image/webp",
}


def detect_image_format(image_bytes: bytes) -> Optional[str]:
    for magic, mime in MAGIC_BYTES.items():
        if image_bytes[:len(magic)] == magic:
            return mime
    if len(image_bytes) > 3 and image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if len(image_bytes) > 4 and image_bytes[:4] == b"RIFF":
        return "image/webp"
    return None


def validate_image_bytes(image_bytes: bytes) -> bool:
    import numpy as np
    cv2 = _cv2()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img is not None


def get_image_dimensions(image_bytes: bytes) -> Optional[Tuple[int, int]]:
    import numpy as np
    cv2 = _cv2()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    return img.shape[1], img.shape[0]


def preprocess_image(image_bytes: bytes, target_size: Tuple[int, int] = (640, 640)):
    import numpy as np
    cv2 = _cv2()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Tidak dapat membaca gambar. Format mungkin tidak didukung atau file rusak.")
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    img = img.astype(np.float32) / 255.0
    return img


def reduce_noise(image):
    cv2 = _cv2()
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def sharpen_image(image):
    import numpy as np
    cv2 = _cv2()
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)


def extract_leaf_segments(image):
    cv2 = _cv2()
    import numpy as np
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (30, 20, 20), (85, 255, 255))
    kernel = np.ones((5, 5), np.uint8)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def calculate_disease_area(image, mask) -> float:
    import numpy as np
    total_pixels = image.shape[0] * image.shape[1]
    disease_pixels = np.count_nonzero(mask)
    return (disease_pixels / total_pixels) * 100


def enhance_image(image):
    import numpy as np
    cv2 = _cv2()
    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)
    denoised = reduce_noise(image)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    return sharpen_image(enhanced)


def normalize_image(image):
    import numpy as np
    return image.astype(np.float32) / 255.0