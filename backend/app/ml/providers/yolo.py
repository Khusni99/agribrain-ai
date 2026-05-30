from typing import Optional
import numpy as np
from app.ml.providers.base import BaseVisionProvider, DetectionResult


class YOLOVisionProvider(BaseVisionProvider):
    def __init__(self, model_path: Optional[str] = None):
        self._model_path = model_path
        self._model = None
        self._loaded = False

    @property
    def model_name(self) -> str:
        return "yolo-vision-v1"

    @property
    def is_ready(self) -> bool:
        return self._loaded

    async def load_model(self) -> bool:
        if not self._model_path:
            return False
        try:
            import torch
            self._model = torch.hub.load("ultralytics/yolov5", "custom", path=self._model_path)
            self._loaded = True
            return True
        except (ImportError, Exception):
            self._loaded = False
            return False

    async def detect(self, image: np.ndarray) -> DetectionResult:
        if not self._loaded:
            raise RuntimeError(
                "YOLO model not loaded. Call load_model() first "
                "and ensure model_path points to a valid .pt file."
            )
        results = self._model(image)
        detections = results.pandas().xyxy[0]

        if detections.empty:
            return DetectionResult(
                disease_name="healthy",
                confidence=0.95,
                severity=0.0,
                bounding_boxes=[],
                recommendations=["Tanaman dalam kondisi sehat. Pertahankan perawatan rutin."],
                prevention=["Lanjutkan pemupukan dan penyiraman sesuai jadwal"],
                economic_risk={
                    "estimated_yield_loss_percent": 0,
                    "estimated_revenue_loss_per_hectare": 0,
                    "currency": "IDR",
                    "risk_level": "RENDAH",
                },
            )

        top = detections.iloc[0]
        boxes = []
        for _, row in detections.iterrows():
            boxes.append({
                "x1": int(row["xmin"]),
                "y1": int(row["ymin"]),
                "x2": int(row["xmax"]),
                "y2": int(row["ymax"]),
                "confidence": round(row["confidence"], 2),
                "label": row["name"],
            })

        return DetectionResult(
            disease_name=top["name"],
            confidence=round(top["confidence"], 2),
            severity=round(float(top["confidence"]) * 100, 1),
            bounding_boxes=boxes,
            recommendations=[
                "Rekomendasi akan tersedia setelah model YOLO terintegrasi dengan basis pengetahuan"
            ],
            prevention=[
                "Data pencegahan akan tersedia setelah integrasi basis pengetahuan lengkap"
            ],
            economic_risk={
                "estimated_yield_loss_percent": 0,
                "estimated_revenue_loss_per_hectare": 0,
                "currency": "IDR",
                "risk_level": "BELUM_DIHITUNG",
            },
        )
