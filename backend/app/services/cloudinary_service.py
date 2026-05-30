import io
import logging
from typing import Optional

import cloudinary
import cloudinary.uploader
from app.config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return all([
        settings.CLOUDINARY_CLOUD_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ])


def configure():
    if not is_configured():
        logger.warning("Cloudinary not configured — skipping cloud upload")
        return
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_image(
    file_bytes: bytes,
    public_id: Optional[str] = None,
    folder: str = "detections",
) -> Optional[str]:
    if not is_configured():
        return None
    configure()
    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(file_bytes),
            public_id=public_id,
            folder=folder,
            overwrite=True,
            resource_type="image",
        )
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None
