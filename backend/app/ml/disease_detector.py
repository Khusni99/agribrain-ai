from typing import Optional
import numpy as np
from app.ml.providers.base import BaseVisionProvider, DetectionResult
from app.ml.providers.mock import MockVisionProvider
from app.ml.providers.yolo import YOLOVisionProvider
from app.ml.schemas import DetectionResponse, BoundingBox, EconomicRisk


def _image_processing():
    from app.ml.utils import image_processing
    return image_processing


DISEASE_LABELS = [
    "anthracnose",
    "bacterial_wilt",
    "fusarium_wilt",
    "leaf_curl_virus",
    "thrips_damage",
    "mite_damage",
    "magnesium_deficiency",
    "calcium_deficiency",
    "nitrogen_deficiency",
]


class DiseaseDetector:
    def __init__(self, provider: Optional[BaseVisionProvider] = None):
        self._provider = provider or MockVisionProvider()
        self._loaded = False

    @property
    def provider(self) -> BaseVisionProvider:
        return self._provider

    @provider.setter
    def provider(self, new_provider: BaseVisionProvider) -> None:
        self._provider = new_provider
        self._loaded = False

    async def load_model(self) -> bool:
        return await self._provider.load_model()

    async def detect(self, image_bytes: bytes) -> DetectionResponse:
        ip = _image_processing()
        try:
            img = ip.preprocess_image(image_bytes, target_size=(640, 640))
            img_enhanced = ip.enhance_image(img)
            img_rgb = (img_enhanced * 255).astype(np.uint8)
        except Exception:
            raise ValueError("Gagal memproses gambar. Pastikan file adalah gambar yang valid.")

        if not self._loaded:
            self._loaded = await self.load_model()

        result = await self._provider.detect(img_rgb)

        height, width = img_rgb.shape[:2]

        return DetectionResponse(
            disease_name=result.disease_name,
            confidence=result.confidence,
            severity=result.severity,
            bounding_boxes=[
                BoundingBox(**box) for box in result.bounding_boxes
            ],
            recommendations=result.recommendations,
            prevention=result.prevention,
            economic_risk=EconomicRisk(**result.economic_risk),
            detection_provider=self._provider.model_name,
            processed_image_width=width,
            processed_image_height=height,
        )
