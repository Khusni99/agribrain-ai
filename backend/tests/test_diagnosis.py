import pytest
import struct
import zlib
from app.agents.agronomist import AgronomistAgent
from app.ml.disease_detector import DiseaseDetector
from app.ml.schemas import DetectionResponse


def _cv2_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


def _make_png_bytes(width: int = 100, height: int = 100) -> bytes:
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b""
    for y in range(height):
        raw += b"\x00" + b"\x00\xff\x00" * width
    compressed = zlib.compress(raw)
    return signature + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", compressed) + _chunk(b"IEND", b"")


PNG_BYTES = _make_png_bytes()


@pytest.mark.asyncio
async def test_agronomist_diagnose():
    agent = AgronomistAgent()
    result = await agent.diagnose(
        query="Daun cabai menguning bagian bawah",
        crop_type="chili",
    )
    assert "diagnosis" in result
    assert "possible_causes" in result
    assert "recommended_actions" in result
    assert "confidence_score" in result
    assert len(result["follow_up_questions"]) > 0


@pytest.mark.asyncio
async def test_yellow_leaves_diagnosis():
    agent = AgronomistAgent()
    result = await agent.diagnose("Daun tanaman menguning dan pertumbuhan terhambat")
    assert result["confidence_score"] > 0


@pytest.mark.asyncio
async def test_spots_diagnosis():
    agent = AgronomistAgent()
    result = await agent.diagnose("Ada bercak coklat pada daun tomat")
    assert result["confidence_score"] > 0


@pytest.mark.asyncio
@pytest.mark.skipif(not _cv2_available(), reason="Requires opencv-python")
async def test_disease_detector_returns_detection_response():
    detector = DiseaseDetector()
    result = await detector.detect(PNG_BYTES)
    assert isinstance(result, DetectionResponse)
    assert result.disease_name
    assert 0 <= result.confidence <= 1.0
    assert 0 <= result.severity <= 100
    assert len(result.bounding_boxes) > 0
    assert len(result.recommendations) > 0
    assert len(result.prevention) > 0
    assert result.economic_risk.risk_level in ("RENDAH", "SEDANG", "TINGGI")


@pytest.mark.asyncio
async def test_disease_detector_invalid_bytes():
    detector = DiseaseDetector()
    with pytest.raises(ValueError, match="Gagal memproses"):
        await detector.detect(b"invalid")


@pytest.mark.asyncio
async def test_disease_detector_empty_bytes():
    detector = DiseaseDetector()
    with pytest.raises(ValueError, match="Gagal memproses"):
        await detector.detect(b"")


@pytest.mark.asyncio
async def test_disease_detector_provider_switch():
    from app.ml.providers.yolo import YOLOVisionProvider
    detector = DiseaseDetector()
    yolo = YOLOVisionProvider()
    detector.provider = yolo
    assert detector.provider is yolo
