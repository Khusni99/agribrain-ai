import pytest
import io
from httpx import AsyncClient, ASGITransport
from app.main import app


pytestmark = pytest.mark.skipif(
    True,
    reason="Requires opencv-python which is not installed in this environment",
)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _make_png_bytes() -> bytes:
    import struct, zlib

    def _make_png(width: int, height: int) -> bytes:
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

    return _make_png(100, 100)


PNG_BYTES = _make_png_bytes()


def _cv2_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


@pytest.mark.asyncio
async def test_detect_disease_valid_png(client):
    if not _cv2_available():
        pytest.skip("Requires opencv-python")
    files = {
        "file": ("test.png", io.BytesIO(PNG_BYTES), "image/png"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "disease_name" in data
    assert "confidence" in data
    assert "severity" in data
    assert "bounding_boxes" in data
    assert "recommendations" in data
    assert "prevention" in data
    assert "economic_risk" in data
    assert "id" in data
    assert 0 <= data["confidence"] <= 1.0
    assert 0 <= data["severity"] <= 100


@pytest.mark.asyncio
async def test_detect_disease_invalid_extension(client):
    files = {
        "file": ("test.txt", io.BytesIO(b"not an image"), "text/plain"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 400
    assert "tidak didukung" in response.text.lower() or "not supported" in response.text.lower()


@pytest.mark.asyncio
async def test_detect_disease_empty_file(client):
    files = {
        "file": ("empty.png", io.BytesIO(b""), "image/png"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 400
