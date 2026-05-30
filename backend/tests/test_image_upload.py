import pytest
import io
import struct
import zlib
from httpx import AsyncClient, ASGITransport
from app.main import app


def _cv2_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _cv2_available(),
    reason="Requires opencv-python which is not installed in this environment",
)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


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
async def test_detect_disease_valid_png(client):
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


@pytest.mark.asyncio
async def test_detect_disease_fake_bytes_png_extension(client):
    files = {
        "file": ("fake.png", io.BytesIO(b"<html>not an image</html>"), "image/png"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 400
    assert "tidak dikenali" in response.text.lower()


@pytest.mark.asyncio
async def test_detect_disease_exact_max_size(client):
    data = b"x" * (10 * 1024 * 1024)
    files = {
        "file": ("large.png", io.BytesIO(data), "image/png"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_detect_disease_valid_jpeg_bytes(client):
    jpeg_soi = b"\xff\xd8\xff\xe0"
    files = {
        "file": ("test.jpg", io.BytesIO(jpeg_soi + b"x" * 100), "image/jpeg"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 400
    assert "tidak dikenali" in response.text.lower() or "rusak" in response.text.lower()


@pytest.mark.asyncio
async def test_detect_disease_webp_magic_bytes(client):
    webp_header = b"RIFF\x00\x00\x00\x00WEBP"
    files = {
        "file": ("test.webp", io.BytesIO(webp_header + b"x" * 100), "image/webp"),
    }
    response = await client.post("/api/v1/diagnosis/detect-disease", files=files)
    assert response.status_code == 400
    assert "rusak" in response.text.lower() or "gagal" in response.text.lower()


@pytest.mark.asyncio
async def test_list_detections(client):
    response = await client.get("/api/v1/diagnosis/detections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
