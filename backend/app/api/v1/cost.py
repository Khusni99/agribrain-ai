from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.diagnosis import CostCalculationRequest, CostCalculationResponse
from app.services.cost_calculator import CostCalculator

router = APIRouter()
calculator = CostCalculator()


@router.post("/calculate", response_model=CostCalculationResponse)
async def calculate_production_cost(
    data: CostCalculationRequest,
    user: User | None = Depends(get_optional_user),
):
    return await calculator.calculate(data)
