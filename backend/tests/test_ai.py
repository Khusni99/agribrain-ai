import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.models.farm import Farm, Field
from app.models.crop import Crop, CropCycle
from app.models.disease import DiseaseRecord
from app.models.fertilizer import FertilizerRecommendation
from app.models.spray import SpraySchedule
from app.models.harvest import HarvestRecord
from app.models.weather import WeatherData
from app.core.security import hash_password
from sqlalchemy import select, delete
from datetime import datetime, timezone


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await session.execute(delete(WeatherData))
        await session.execute(delete(HarvestRecord))
        await session.execute(delete(SpraySchedule))
        await session.execute(delete(FertilizerRecommendation))
        await session.execute(delete(DiseaseRecord))
        await session.execute(delete(CropCycle))
        await session.execute(delete(Field))
        await session.execute(delete(Crop))
        await session.execute(delete(Farm))
        await session.execute(delete(User).where(User.username == "aitest"))
        await session.commit()

        user = User(
            email="ai@test.com",
            username="aitest",
            hashed_password=hash_password("testpass"),
            full_name="AI Test User",
        )
        session.add(user)
        await session.flush()

        crop = Crop(name="Cabai Merah", growing_days=90)
        session.add(crop)
        await session.flush()

        farm = Farm(name="AI Test Farm", user_id=user.id, latitude=-7.5, longitude=110.5)
        session.add(farm)
        await session.flush()

        field = Field(name="Petak AI", farm_id=farm.id, crop_type="Cabai Merah", area_hectare=1.0)
        session.add(field)
        await session.flush()

        cycle = CropCycle(
            field_id=field.id, crop_id=crop.id,
            start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            expected_harvest_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
            status="active",
        )
        session.add(cycle)

        fert = FertilizerRecommendation(
            field_id=field.id, crop_cycle_id=cycle.id,
            fertilizer_name="Urea", dosage_per_hectare=200.0,
            growth_stage="vegetatif",
        )
        session.add(fert)

        spray = SpraySchedule(
            field_id=field.id, crop_cycle_id=cycle.id,
            product_name="Antracol", is_applied=True,
        )
        session.add(spray)

        disease = DiseaseRecord(
            field_id=field.id, crop_id=crop.id,
            disease_name="Layu Bakteri", severity_percentage=25.0,
        )
        session.add(disease)

        harvest = HarvestRecord(
            field_id=field.id, crop_cycle_id=cycle.id,
            harvest_date=datetime(2026, 3, 15, tzinfo=timezone.utc),
            quantity_kg=500.0, average_price=10000.0,
        )
        session.add(harvest)

        weather = WeatherData(
            latitude=-7.5, longitude=110.5,
            temperature=28.0, humidity=75.0,
            rainfall_mm=5.0, condition="Cerah Berawan",
        )
        session.add(weather)
        await session.commit()
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    response = await client.post("/api/v1/auth/login", json={
        "username": "aitest",
        "password": "testpass",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_farm_advisor(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.post("/api/v1/ai/farm-advisor", json={
        "farm_id": farm_id,
        "query": "Apa kondisi lahan saya?",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "advice" in data
    assert "field_health" in data
    assert "recommendations" in data
    assert "risks" in data
    assert data["field_health"]["health_score"] > 0
    assert data["field_health"]["status"] in ("sehat", "waspada", "kritis")


@pytest.mark.asyncio
async def test_farm_advisor_no_fields(client, auth_headers):
    # Create empty farm
    resp = await client.post("/api/v1/farms/", json={"name": "Empty Farm"}, headers=auth_headers)
    empty_farm_id = resp.json()["id"]

    response = await client.post("/api/v1/ai/farm-advisor", json={
        "farm_id": empty_farm_id,
    }, headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_recommendations(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.post("/api/v1/ai/recommendations", json={
        "farm_id": farm_id,
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "today" in data
    assert "this_week" in data
    assert "urgent" in data
    assert "all" in data


@pytest.mark.asyncio
async def test_get_recommendations_filtered(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.post("/api/v1/ai/recommendations", json={
        "farm_id": farm_id,
        "types": ["fertilizer", "harvest"],
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    for item in data["all"]:
        assert item["type"] in ("fertilizer", "harvest")


@pytest.mark.asyncio
async def test_field_health(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.get(f"/api/v1/ai/field-health/{field_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["field_id"] == field_id
    assert 0 <= data["health_score"] <= 100
    assert "disease_risk" in data
    assert "nutrient_risk" in data
    assert "yield_forecast" in data
    assert data["disease_risk"]["level"] in ("RENDAH", "SEDANG", "TINGGI")


@pytest.mark.asyncio
async def test_crop_risk(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    # Create a crop cycle explicitly for this test
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    cycle_resp = await client.post(f"/api/v1/farms/{farm_id}/crop-cycles", json={
        "field_id": field_id,
        "crop_id": 1,
        "start_date": "2026-01-01T00:00:00Z",
        "expected_harvest_date": "2026-04-01T00:00:00Z",
    }, headers=auth_headers)
    cycle_id = cycle_resp.json()["id"]

    response = await client.get(f"/api/v1/ai/crop-risk/{cycle_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "disease_risk" in data
    assert "nutrient_deficiency_risk" in data
    assert "yield_reduction_risk" in data
    assert "overall_risk_score" in data
    assert "overall_risk_level" in data
    assert 0 <= data["overall_risk_score"] <= 100


@pytest.mark.asyncio
async def test_field_health_not_found(client, auth_headers):
    response = await client.get("/api/v1/ai/field-health/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_crop_risk_not_found(client, auth_headers):
    response = await client.get("/api/v1/ai/crop-risk/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_ai(client):
    response = await client.post("/api/v1/ai/farm-advisor", json={"farm_id": 1})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_recommendation_engine(client, auth_headers):
    from app.services.crop_health import CropHealthCalculator
    calc = CropHealthCalculator()

    context = {
        "field": {"id": 1, "name": "Test Field", "crop_type": "Cabai Merah", "area_hectare": 1.0},
        "crop_age_days": 30,
        "active_crop_cycle": {"crop_name": "Cabai Merah", "crop_growing_days": 90, "status": "active"},
        "disease_history": [],
        "fertilizer_history": [],
        "spray_history": [],
        "harvest_history": [],
        "weather": {"current": {"temperature": 28, "humidity": 70, "rainfall": 5}},
    }

    health = await calc.calculate_field_health(context)
    assert health.health_score < 100
    assert health.status in ("sehat", "waspada", "kritis")

    risks = await calc.assess_risks(context)
    assert risks.overall_risk_score >= 0
    assert risks.overall_risk_level in ("RENDAH", "SEDANG", "TINGGI")
