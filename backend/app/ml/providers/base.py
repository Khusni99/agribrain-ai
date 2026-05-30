from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional
import numpy as np


@dataclass
class DetectionResult:
    disease_name: str
    confidence: float
    severity: float
    bounding_boxes: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    prevention: list[str] = field(default_factory=list)
    economic_risk: dict = field(default_factory=dict)
    raw_raw: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


class BaseVisionProvider(ABC):
    @abstractmethod
    async def detect(self, image: np.ndarray) -> DetectionResult:
        ...

    @abstractmethod
    async def load_model(self) -> bool:
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        ...
