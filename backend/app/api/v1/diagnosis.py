from fastapi import APIRouter, Depends, UploadFile, File
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.diagnosis import (
    DiagnosisRequest, DiagnosisResponse,
    DiseaseDetectionResponse,
    FertilizerRequest, FertilizerResponse,
)
from app.agents.agronomist import AgronomistAgent
from app.ml.disease_detector import DiseaseDetector
from app.services.fertilizer import FertilizerService

router = APIRouter()
agronomist = AgronomistAgent()
disease_detector = DiseaseDetector()
fertilizer_service = FertilizerService()


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


@router.post("/detect-disease", response_model=DiseaseDetectionResponse)
async def detect_disease(
    file: UploadFile = File(...),
    user: User | None = Depends(get_optional_user),
):
    image_bytes = await file.read()
    result = await disease_detector.detect(image_bytes)
    return result


@router.post("/fertilizer-recommend", response_model=FertilizerResponse)
async def recommend_fertilizer(
    data: FertilizerRequest,
    user: User | None = Depends(get_optional_user),
):
    result = await fertilizer_service.recommend(data)
    return result
