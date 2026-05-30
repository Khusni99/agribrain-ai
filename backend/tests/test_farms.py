import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.models.farm import Farm, Field
from app.models.crop import Crop
from app.core.security import hash_password
from sqlalchemy import select, delete


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await session.execute(delete(Field))
        await session.execute(delete(Farm))
        await session.execute(delete(Crop))
        await session.execute(delete(User).where(User.username == "testuser"))
        await session.commit()

        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hash_password("testpass"),
            full_name="Test User",
        )
        session.add(user)
        await session.flush()

        crop = Crop(name="Cabai Merah", growing_days=90)
        session.add(crop)
        await session.flush()

        farm = Farm(name="Test Farm", user_id=user.id)
        session.add(farm)
        await session.flush()

        field = Field(name="Petak A", farm_id=farm.id, crop_type="Cabai Merah")
        session.add(field)
        await session.commit()
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def token(client):
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass",
    })
    return response.json()["access_token"]


@pytest.fixture
async def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_farm(client, auth_headers):
    response = await client.post("/api/v1/farms/", json={
        "name": "Lahan Baru",
        "location": "Brebes, Jawa Tengah",
        "area_hectare": 2.5,
        "soil_type": "Lempung",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lahan Baru"
    assert data["area_hectare"] == 2.5
    assert "id" in data


@pytest.mark.asyncio
async def test_list_farms(client, auth_headers):
    response = await client.get("/api/v1/farms/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "name" in data[0]
    assert "fields_count" in data[0]


@pytest.mark.asyncio
async def test_get_farm(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.get(f"/api/v1/farms/{farm_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Farm"


@pytest.mark.asyncio
async def test_update_farm(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.put(f"/api/v1/farms/{farm_id}", json={
        "name": "Lahan Diupdate",
        "area_hectare": 3.0,
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Lahan Diupdate"
    assert data["area_hectare"] == 3.0


@pytest.mark.asyncio
async def test_delete_farm(client, auth_headers):
    resp = await client.post("/api/v1/farms/", json={"name": "Temp Farm"}, headers=auth_headers)
    farm_id = resp.json()["id"]

    response = await client.delete(f"/api/v1/farms/{farm_id}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_field(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.post(f"/api/v1/farms/{farm_id}/fields", json={
        "farm_id": farm_id,
        "name": "Petak B",
        "area_hectare": 1.0,
        "crop_type": "Tomat",
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Petak B"


@pytest.mark.asyncio
async def test_list_fields(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_update_field(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.put(f"/api/v1/farms/fields/{field_id}", json={
        "name": "Petak A Updated",
        "status": "inactive",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Petak A Updated"
    assert response.json()["status"] == "inactive"


@pytest.mark.asyncio
async def test_create_crop_cycle(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.post(f"/api/v1/farms/{farm_id}/crop-cycles", json={
        "field_id": field_id,
        "crop_id": 1,
        "start_date": "2026-01-01T00:00:00Z",
        "expected_harvest_date": "2026-04-01T00:00:00Z",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_harvest_record(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.post("/api/v1/farms/harvest-records", json={
        "field_id": field_id,
        "harvest_date": "2026-04-01T00:00:00Z",
        "quantity_kg": 500.0,
        "average_price": 10000.0,
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["quantity_kg"] == 500.0


@pytest.mark.asyncio
async def test_farm_dashboard(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.get(f"/api/v1/farms/{farm_id}/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_fields" in data
    assert "active_crop_cycles" in data
    assert "upcoming_tasks" in data
    assert "recent_activities" in data
    assert "crop_progress" in data


@pytest.mark.asyncio
async def test_farm_timeline(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.get(f"/api/v1/farms/{farm_id}/timeline", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_farm_reminders(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]

    response = await client.get(f"/api/v1/farms/{farm_id}/reminders", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    response = await client.get("/api/v1/farms/")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_nonexistent_farm(client, auth_headers):
    response = await client.get("/api/v1/farms/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_spray_record(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.post("/api/v1/farms/spray-records", json={
        "field_id": field_id,
        "product_name": "Antracol",
        "target_pest": "Jamur",
        "dosage": 2.0,
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["product_name"] == "Antracol"


@pytest.mark.asyncio
async def test_create_fertilizer_record(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.post("/api/v1/farms/fertilizer-records", json={
        "field_id": field_id,
        "fertilizer_name": "Urea",
        "dosage_per_hectare": 200.0,
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["fertilizer_name"] == "Urea"


@pytest.mark.asyncio
async def test_create_disease_record(client, auth_headers):
    resp = await client.get("/api/v1/farms/", headers=auth_headers)
    farm_id = resp.json()[0]["id"]
    fields_resp = await client.get(f"/api/v1/farms/{farm_id}/fields", headers=auth_headers)
    field_id = fields_resp.json()[0]["id"]

    response = await client.post("/api/v1/farms/disease-records", json={
        "field_id": field_id,
        "crop_id": 1,
        "disease_name": "Layu Bakteri",
        "severity_percentage": 30.0,
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["disease_name"] == "Layu Bakteri"
