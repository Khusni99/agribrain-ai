import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.models.farm import Farm, Field
from app.models.crop import Crop, CropCycle
from app.models.notification import WhatsAppSession, NotificationLog, ReminderPreference
from app.core.security import hash_password
from app.dependencies import get_current_user
from sqlalchemy import select, delete
from datetime import datetime, timezone, date

TEST_USER_EMAIL = "test_whatsapp@example.com"
TEST_USER_PASS = "testpass123"
TEST_USERNAME = "testwhatsapp"


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await session.execute(delete(NotificationLog))
        await session.execute(delete(ReminderPreference))
        await session.execute(delete(WhatsAppSession))
        await session.execute(delete(CropCycle))
        await session.execute(delete(Field))
        await session.execute(delete(Farm))
        await session.execute(delete(User).where(User.username == TEST_USERNAME))
        await session.commit()


async def _create_test_user(db) -> User:
    from app.core.security import hash_password
    user = User(
        email=TEST_USER_EMAIL,
        username=TEST_USERNAME,
        hashed_password=hash_password(TEST_USER_PASS),
        full_name="Test User",
        phone="+6281234567890",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _get_token(client) -> str:
    resp = await client.post("/api/v1/auth/login", json={
        "username": TEST_USERNAME,
        "password": TEST_USER_PASS,
    })
    return resp.json()["access_token"]


@pytest.mark.anyio
async def test_whatsapp_register():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.post(
            "/api/v1/whatsapp/register",
            json={"phone_number": "+6281234567890"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "registered"
        assert data["phone_number"] == "+6281234567890"
        assert data["is_verified"] is True


@pytest.mark.anyio
async def test_whatsapp_register_duplicate():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        session = WhatsAppSession(user_id=user.id, phone_number="+6281234567890", is_verified=True, provider="mock")
        db.add(session)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.post(
            "/api/v1/whatsapp/register",
            json={"phone_number": "+6281234567890"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "exists"


@pytest.mark.anyio
async def test_whatsapp_session():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        session = WhatsAppSession(user_id=user.id, phone_number="+6281234567890", is_verified=True, provider="mock")
        db.add(session)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.get(
            "/api/v1/whatsapp/session",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["registered"] is True
        assert data["phone_number"] == "+6281234567890"


@pytest.mark.anyio
async def test_webhook_verify():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/whatsapp/webhook",
            params={"hub.mode": "subscribe", "hub.verify_token": "agribrain_verify_2024", "hub.challenge": "12345"},
        )
        assert resp.status_code == 200
        assert resp.text == "12345"


@pytest.mark.anyio
async def test_webhook_verify_fail():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/whatsapp/webhook",
            params={"hub.mode": "subscribe", "hub.verify_token": "wrong_token", "hub.challenge": "12345"},
        )
        assert resp.status_code == 403


@pytest.mark.anyio
async def test_webhook_unregistered_number():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/whatsapp/webhook",
            json={"From": "+6289999999999", "Body": "/lahan"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "belum terdaftar" in data["reply"]


@pytest.mark.anyio
async def test_webhook_lahan_command():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        session = WhatsAppSession(user_id=user.id, phone_number="+6281234567890", is_verified=True, provider="mock")
        db.add(session)
        farm = Farm(user_id=user.id, name="Lahan Sejahtera", location="Jakarta")
        db.add(farm)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/whatsapp/webhook",
            json={"From": "+6281234567890", "Body": "/lahan"},
        )
        assert resp.status_code == 200
        assert "DAFTAR LAHAN" in resp.json()["reply"]
        assert "Lahan Sejahtera" in resp.json()["reply"]


@pytest.mark.anyio
async def test_webhook_petak_command():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        session = WhatsAppSession(user_id=user.id, phone_number="+6281234567890", is_verified=True, provider="mock")
        db.add(session)
        farm = Farm(user_id=user.id, name="Lahan Sejahtera")
        db.add(farm)
        await db.flush()
        field = Field(farm_id=farm.id, name="Petak A", crop_type="Padi")
        db.add(field)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/whatsapp/webhook",
            json={"From": "+6281234567890", "Body": "/petak"},
        )
        assert resp.status_code == 200
        assert "DAFTAR PETAK" in resp.json()["reply"]
        assert "Petak A" in resp.json()["reply"]


@pytest.mark.anyio
async def test_webhook_unknown_command():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        session = WhatsAppSession(user_id=user.id, phone_number="+6281234567890", is_verified=True, provider="mock")
        db.add(session)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/whatsapp/webhook",
            json={"From": "+6281234567890", "Body": "/unknown"},
        )
        assert resp.status_code == 200
        assert "Perintah tidak dikenal" in resp.json()["reply"]


@pytest.mark.anyio
async def test_webhook_free_text():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        session = WhatsAppSession(user_id=user.id, phone_number="+6281234567890", is_verified=True, provider="mock")
        db.add(session)
        farm = Farm(user_id=user.id, name="Lahan Sejahtera")
        db.add(farm)
        await db.flush()
        field = Field(farm_id=farm.id, name="Petak A", crop_type="Padi")
        db.add(field)
        await db.flush()
        crop = Crop(name="Padi", growing_days=120)
        db.add(crop)
        await db.flush()
        cycle = CropCycle(field_id=field.id, crop_id=crop.id, start_date=datetime.now(timezone.utc), status="active")
        db.add(cycle)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/whatsapp/webhook",
            json={"From": "+6281234567890", "Body": "Apa yang harus saya lakukan?"},
        )
        assert resp.status_code == 200
        assert "PERTANYAAN ANDA" in resp.json()["reply"]


@pytest.mark.anyio
async def test_reminder_preferences():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.get(
            "/api/v1/notifications/preferences",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["whatsapp_enabled"] is True
        assert data["fertilizer_reminder"] is True

        resp2 = await client.put(
            "/api/v1/notifications/preferences",
            json={"whatsapp_enabled": False, "fertilizer_reminder": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["whatsapp_enabled"] is False
        assert data2["fertilizer_reminder"] is False


@pytest.mark.anyio
async def test_notification_log():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        log = NotificationLog(
            user_id=user.id,
            phone_number="+6281234567890",
            notification_type="fertilizer",
            title="Pengingat Pemupukan",
            message="Waktunya pemupukan di Petak A",
            status="sent",
        )
        db.add(log)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.get(
            "/api/v1/notifications/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["notification_type"] == "fertilizer"
        assert data[0]["title"] == "Pengingat Pemupukan"


@pytest.mark.anyio
async def test_notification_unread():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        log = NotificationLog(
            user_id=user.id,
            phone_number="+6281234567890",
            notification_type="harvest",
            title="Pengingat Panen",
            message="Panen dalam 3 hari",
            status="sent",
        )
        db.add(log)
        await db.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.get(
            "/api/v1/notifications/unread",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["unread_count"] >= 1


@pytest.mark.anyio
async def test_mark_notification_read():
    async with async_session_factory() as db:
        user = await _create_test_user(db)
        log = NotificationLog(
            user_id=user.id,
            phone_number="+6281234567890",
            notification_type="spray",
            title="Pengingat Semprot",
            message="Waktunya penyemprotan",
            status="sent",
        )
        db.add(log)
        await db.commit()
        notif_id = log.id
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _get_token(client)
        resp = await client.put(
            f"/api/v1/notifications/{notif_id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "read"


@pytest.mark.anyio
async def test_mock_provider_send():
    from app.services.whatsapp_provider import get_provider
    provider = get_provider("mock")
    result = await provider.send_message("+6281234567890", "Test message")
    assert result["status"] == "sent"
    assert "message_id" in result


@pytest.mark.anyio
async def test_mock_provider_verify():
    from app.services.whatsapp_provider import get_provider
    provider = get_provider("mock")
    assert await provider.verify_number("+6281234567890") is True
    assert await provider.verify_number("123") is False
