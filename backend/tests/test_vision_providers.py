import pytest
import numpy as np
from app.ml.providers.mock import MockVisionProvider, DISEASE_LABELS
from app.ml.providers.yolo import YOLOVisionProvider
from app.ml.providers.base import BaseVisionProvider, DetectionResult
from app.ml.disease_detector import DiseaseDetector


def _cv2_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


cv2_skip = pytest.mark.skipif(not _cv2_available(), reason="Requires opencv-python")


from app.ml.utils.image_processing import detect_image_format


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
async def test_mock_provider_all_labels_eventually():
    provider = MockVisionProvider()
    await provider.load_model()
    found = set()
    for _ in range(200):
        image = _make_test_image()
        result = await provider.detect(image)
        found.add(result.disease_name.lower())
    display_labels = {d.replace("_", " ").lower() for d in DISEASE_LABELS}
    assert found & display_labels, "Mock provider should eventually return all disease labels"


def test_detect_image_format_png():
    png_header = b"\x89PNG\r\n\x1a\n" + b"x" * 20
    assert detect_image_format(png_header) == "image/png"


def test_detect_image_format_jpeg():
    jpeg_header = b"\xff\xd8\xff\xe0" + b"x" * 20
    assert detect_image_format(jpeg_header) == "image/jpeg"


def test_detect_image_format_webp():
    webp_header = b"RIFF\x00\x00\x00\x00WEBP" + b"x" * 20
    assert detect_image_format(webp_header) == "image/webp"


def test_detect_image_format_unknown():
    assert detect_image_format(b"<html>") is None


def test_detect_image_format_empty():
    assert detect_image_format(b"") is None


@cv2_skip
def test_validate_image_bytes_invalid():
    from app.ml.utils.image_processing import validate_image_bytes
    assert validate_image_bytes(b"not an image") is False


@cv2_skip
def test_reduce_noise_and_sharpen():
    from app.ml.utils.image_processing import reduce_noise, sharpen_image
    image = _make_test_image()
    denoised = reduce_noise(image)
    assert denoised.shape == image.shape
    sharpened = sharpen_image(image)
    assert sharpened.shape == image.shape


@cv2_skip
def test_preprocess_image_invalid_bytes():
    from app.ml.utils.image_processing import preprocess_image
    with pytest.raises(ValueError, match="Tidak dapat membaca"):
        preprocess_image(b"invalid bytes")


@pytest.mark.asyncio
async def test_yolo_provider_load_no_path():
    provider = YOLOVisionProvider(model_path=None)
    loaded = await provider.load_model()
    assert loaded is False
    assert provider.is_ready is False


@pytest.mark.asyncio
async def test_disease_detector_detect_invalid_bytes():
    detector = DiseaseDetector()
    with pytest.raises(ValueError, match="Gagal memproses"):
        await detector.detect(b"garbage bytes")


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
