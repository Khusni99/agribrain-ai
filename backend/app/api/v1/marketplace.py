from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.marketplace import Product, MarketPrice, ProductStatus
from app.schemas.marketplace import ProductCreate, ProductResponse

router = APIRouter()


@router.get("/products")
async def list_products(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).where(Product.status == ProductStatus.AVAILABLE)
    if category:
        query = query.where(Product.category == category)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    product = Product(**data.model_dump(), user_id=user.id)
    db.add(product)
    await db.flush()
    return ProductResponse.model_validate(product)


@router.get("/prices")
async def get_market_prices(
    commodity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MarketPrice)
    if commodity:
        query = query.where(MarketPrice.commodity == commodity)
    query = query.order_by(MarketPrice.recorded_at.desc()).limit(50)
    result = await db.execute(query)
    return result.scalars().all()
