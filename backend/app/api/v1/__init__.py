from fastapi import APIRouter
from app.api.v1 import auth, farms, diagnosis, weather, cost, marketplace, users, ai, whatsapp, notifications

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(farms.router, prefix="/farms", tags=["Farms"])
router.include_router(diagnosis.router, prefix="/diagnosis", tags=["Diagnosis"])
router.include_router(weather.router, prefix="/weather", tags=["Weather"])
router.include_router(cost.router, prefix="/cost", tags=["Cost Calculator"])
router.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
router.include_router(ai.router, prefix="/ai", tags=["AI Advisor"])
router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
