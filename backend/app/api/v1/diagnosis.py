import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.models.detection import DiseaseDetection
from app.schemas.diagnosis import (
    DiagnosisRequest, DiagnosisResponse,
    DiseaseDetectionResponse, DiseaseDetectionCreateResponse,
    FertilizerRequest, FertilizerResponse,
)
from app.agents.agronomist import AgronomistAgent
from app.ml.disease_detector import DiseaseDetector
from app.ml.schemas import DetectionResponse as MLDetectionResponse
from app.ml.utils.image_processing import detect_image_format, validate_image_bytes
from app.services.fertilizer import FertilizerService
from app.services.cloudinary_service import upload_image

router = APIRouter()
agronomist = AgronomistAgent()
disease_detector = DiseaseDetector()
fertilizer_service = FertilizerService()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_image_upload(file: UploadFile) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=400,
            detail=f"Format gambar tidak didukung: {ext}. Gunakan: {allowed}",
        )

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File harus berupa gambar (image/*)",
        )


@router.post("/ask", response_model=DiagnosisResponse)
async def diagnose(
    data: DiagnosisRequest,
    user: User | None = Depends(get_optional_user),
):
    result = await agronomist.diagnose(
        query=data.query,
        crop_type=data.crop_type,
        language=data.language,
        user_id=user.id if user else None,
        field_id=data.field_id,
    )
    return result


@router.post("/detect-disease", response_model=DiseaseDetectionCreateResponse)
async def detect_disease(
    file: UploadFile = File(...),
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    validate_image_upload(file)

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Ukuran file terlalu besar. Maksimal {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    if not image_bytes:
        raise HTTPException(status_code=400, detail="File kosong")

    detected_mime = detect_image_format(image_bytes)
    if detected_mime is None:
        raise HTTPException(
            status_code=400,
            detail="File tidak dikenali sebagai gambar. Unggah file PNG, JPG, atau WebP yang valid.",
        )

    if not validate_image_bytes(image_bytes):
        raise HTTPException(
            status_code=400,
            detail="Gambar rusak atau tidak dapat dibaca. Unggah ulang gambar yang valid.",
        )

    result: MLDetectionResponse = await disease_detector.detect(image_bytes)

    upload_dir = "uploads/detections"
    os.makedirs(upload_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{os.path.splitext(file.filename or '.jpg')[1]}"
    image_path = os.path.join(upload_dir, unique_name)
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    cloudinary_url = await upload_image(image_bytes)

    detection_record = DiseaseDetection(
        user_id=user.id if user else None,
        image_path=image_path,
        cloudinary_url=cloudinary_url,
        original_filename=file.filename,
        file_size_bytes=len(image_bytes),
        content_type=file.content_type,
        disease_name=result.disease_name,
        confidence=result.confidence,
        severity=result.severity,
        bounding_boxes=[b.model_dump() for b in result.bounding_boxes],
        recommendations=result.recommendations,
        prevention=result.prevention,
        economic_risk=result.economic_risk.model_dump(),
        detection_provider=result.detection_provider,
    )
    db.add(detection_record)
    await db.flush()
    await db.refresh(detection_record)

    return DiseaseDetectionCreateResponse(
        id=detection_record.id,
        disease_name=result.disease_name,
        confidence=result.confidence,
        severity=result.severity,
        bounding_boxes=result.bounding_boxes,
        recommendations=result.recommendations,
        prevention=result.prevention,
        economic_risk=result.economic_risk,
        detection_provider=result.detection_provider,
        processed_image_width=result.processed_image_width,
        processed_image_height=result.processed_image_height,
        image_url=cloudinary_url,
        created_at=detection_record.created_at,
    )


@router.get("/detections", response_model=list[DiseaseDetectionCreateResponse])
async def list_detections(
    limit: int = 20,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    query = select(DiseaseDetection).order_by(DiseaseDetection.created_at.desc()).limit(limit)
    if user:
        query = query.where(DiseaseDetection.user_id == user.id)
    result = await db.execute(query)
    records = result.scalars().all()
    return [
        DiseaseDetectionCreateResponse(
            id=r.id,
            disease_name=r.disease_name,
            confidence=r.confidence,
            severity=r.severity,
            bounding_boxes=r.bounding_boxes or [],
            recommendations=r.recommendations or [],
            prevention=r.prevention or [],
            economic_risk=r.economic_risk or {},
            detection_provider=r.detection_provider,
            image_url=r.cloudinary_url,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/detections/{detection_id}", response_model=DiseaseDetectionCreateResponse)
async def get_detection(
    detection_id: int,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(DiseaseDetection).where(DiseaseDetection.id == detection_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Detection not found")
    return DiseaseDetectionCreateResponse(
        id=record.id,
        disease_name=record.disease_name,
        confidence=record.confidence,
        severity=record.severity,
        bounding_boxes=record.bounding_boxes or [],
        recommendations=record.recommendations or [],
        prevention=record.prevention or [],
        economic_risk=record.economic_risk or {},
        detection_provider=record.detection_provider,
        image_url=record.cloudinary_url,
        created_at=record.created_at,
    )


@router.post("/fertilizer-recommend", response_model=FertilizerResponse)
async def recommend_fertilizer(
    data: FertilizerRequest,
    user: User | None = Depends(get_optional_user),
):
    result = await fertilizer_service.recommend(data)
    return result
