import pytest
import numpy as np
from app.ml.providers.mock import MockVisionProvider, DISEASE_LABELS
from app.ml.providers.yolo import YOLOVisionProvider
from app.ml.providers.base import BaseVisionProvider, DetectionResult
from app.ml.disease_detector import DiseaseDetector
from app.ml.utils.image_processing import preprocess_image, enhance_image, validate_image_bytes


def _make_test_image(h: int = 100, w: int = 100) -> np.ndarray:
    img = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
    return img


@pytest.mark.asyncio
async def test_mock_provider_implements_abstract():
    provider = MockVisionProvider()
    assert isinstance(provider, BaseVisionProvider)


@pytest.mark.asyncio
async def test_mock_provider_model_name():
    provider = MockVisionProvider()
    assert provider.model_name == "mock-vision-v1"


@pytest.mark.asyncio
async def test_mock_provider_load_model():
    provider = MockVisionProvider()
    loaded = await provider.load_model()
    assert loaded is True
    assert provider.is_ready is True


@pytest.mark.asyncio
async def test_mock_provider_detect():
    provider = MockVisionProvider()
    await provider.load_model()
    image = _make_test_image()
    result = await provider.detect(image)
    assert isinstance(result, DetectionResult)
    assert result.disease_name
    assert 0 <= result.confidence <= 1.0
    assert 0 <= result.severity <= 100
    assert len(result.bounding_boxes) > 0
    assert len(result.recommendations) > 0
    assert len(result.prevention) > 0
    assert "estimated_yield_loss_percent" in result.economic_risk
    assert "estimated_revenue_loss_per_hectare" in result.economic_risk
    assert "risk_level" in result.economic_risk
    assert result.economic_risk["risk_level"] in ("RENDAH", "SEDANG", "TINGGI")


@pytest.mark.asyncio
async def test_mock_provider_disease_labels_coverage():
    provider = MockVisionProvider()
    await provider.load_model()
    found_labels = set()
    for _ in range(50):
        image = _make_test_image()
        result = await provider.detect(image)
        found_labels.add(result.disease_name.lower())
    for label in DISEASE_LABELS:
        display = label.replace("_", " ").title()
        assert display.lower() in DISEASE_LABELS or any(
            dl.replace("_", " ").title().lower() == display.lower()
            for dl in DISEASE_LABELS
        )


@pytest.mark.asyncio
async def test_yolo_provider_not_loaded():
    provider = YOLOVisionProvider()
    assert provider.is_ready is False
    assert provider.model_name == "yolo-vision-v1"


@pytest.mark.asyncio
async def test_yolo_provider_detect_raises():
    provider = YOLOVisionProvider()
    image = _make_test_image()
    with pytest.raises(RuntimeError, match="not loaded"):
        await provider.detect(image)


@pytest.mark.asyncio
async def test_disease_detector_default_provider():
    detector = DiseaseDetector()
    assert isinstance(detector.provider, MockVisionProvider)


@pytest.mark.asyncio
async def test_disease_detector_switch_provider():
    detector = DiseaseDetector()
    yolo = YOLOVisionProvider()
    detector.provider = yolo
    assert detector.provider is yolo


@pytest.mark.asyncio
async def test_detect_with_mock():
    provider = MockVisionProvider()
    await provider.load_model()
    image = _make_test_image()
    result = await provider.detect(image)
    assert result.disease_name
    assert 0 <= result.confidence <= 1.0
    assert 0 <= result.severity <= 100
    assert len(result.recommendations) > 0
    assert len(result.prevention) > 0
    assert result.economic_risk["risk_level"] in ("RENDAH", "SEDANG", "TINGGI")
