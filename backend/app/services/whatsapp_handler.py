from datetime import datetime, timezone, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.farm import Farm, Field
from app.models.crop import CropCycle
from app.models.notification import NotificationLog, ReminderPreference, WhatsAppSession
from app.services.ai_context_builder import AIContextBuilder
from app.services.recommendation_engine import RecommendationEngine
from app.services.crop_health import CropHealthCalculator
from app.services.whatsapp_provider import get_provider


class WhatsAppCommandHandler:
    def __init__(self):
        self.context_builder = AIContextBuilder()
        self.recommendation_engine = RecommendationEngine()
        self.health_service = CropHealthCalculator()

    async def handle_message(self, db: AsyncSession, phone_number: str, message: str) -> str:
        session_result = await db.execute(
            select(WhatsAppSession).where(
                WhatsAppSession.phone_number == phone_number,
                WhatsAppSession.is_verified == True,
            )
        )
        session = session_result.scalar_one_or_none()
        if not session:
            return "Maaf, nomor Anda belum terdaftar. Silakan daftar melalui aplikasi AgriBrain AI terlebih dahulu."

        user_id = session.user_id
        msg = message.strip().lower()

        if msg == "/lahan":
            return await self._list_farms(db, user_id)
        elif msg == "/petak":
            return await self._list_fields(db, user_id)
        elif msg.startswith("/petak "):
            farm_name = message[7:].strip()
            return await self._list_fields_for_farm(db, user_id, farm_name)
        elif msg == "/rekomendasi":
            return await self._get_recommendations(db, user_id)
        elif msg == "/cuaca":
            return await self._get_weather(db, user_id)
        elif msg == "/jadwal":
            return await self._get_schedule(db, user_id)
        elif msg == "/kesehatan":
            return await self._get_health(db, user_id)
        elif msg.startswith("/"):
            return f"Perintah tidak dikenal: {msg}\n\nPerintah yang tersedia:\n/lahan - Daftar lahan\n/petak - Daftar petak\n/petak [nama] - Petak di lahan tertentu\n/rekomendasi - Rekomendasi hari ini\n/cuaca - Info cuaca\n/jadwal - Jadwal kegiatan\n/kesehatan - Kesehatan tanaman"
        else:
            return await self._ask_advisor(db, user_id, message)

    async def _list_farms(self, db: AsyncSession, user_id: int) -> str:
        result = await db.execute(
            select(Farm).where(Farm.user_id == user_id)
        )
        farms = result.scalars().all()
        if not farms:
            return "Anda belum memiliki lahan. Buat lahan baru melalui aplikasi AgriBrain AI."

        lines = ["🌾 *DAFTAR LAHAN*"]
        for f in farms:
            lines.append(f"  • {f.name}")
        lines.append(f"\nTotal: {len(farms)} lahan")
        return "\n".join(lines)

    async def _list_fields(self, db: AsyncSession, user_id: int) -> str:
        result = await db.execute(
            select(Field)
            .join(Farm)
            .where(Farm.user_id == user_id)
        )
        fields = result.scalars().all()
        if not fields:
            return "Belum ada petak terdaftar."

        lines = ["🧑‍🌾 *DAFTAR PETAK*"]
        for f in fields:
            status = "✅" if f.status == "active" else "⛔"
            crop = f" - {f.crop_type}" if f.crop_type else ""
            lines.append(f"  {status} {f.name}{crop}")
        lines.append(f"\nTotal: {len(fields)} petak")
        return "\n".join(lines)

    async def _list_fields_for_farm(self, db: AsyncSession, user_id: int, farm_name: str) -> str:
        farm_result = await db.execute(
            select(Farm).where(Farm.user_id == user_id, Farm.name.ilike(f"%{farm_name}%"))
        )
        farm = farm_result.scalar_one_or_none()
        if not farm:
            return f"Lahan '{farm_name}' tidak ditemukan."

        result = await db.execute(
            select(Field).where(Field.farm_id == farm.id)
        )
        fields = result.scalars().all()
        if not fields:
            return f"Lahan {farm.name} belum memiliki petak."

        lines = [f"🧑‍🌾 *PETAK DI {farm.name.upper()}*"]
        for f in fields:
            status = "✅" if f.status == "active" else "⛔"
            crop = f" - {f.crop_type}" if f.crop_type else ""
            area = f" ({f.area_hectare} Ha)" if f.area_hectare else ""
            lines.append(f"  {status} {f.name}{crop}{area}")
        return "\n".join(lines)

    async def _get_recommendations(self, db: AsyncSession, user_id: int) -> str:
        result = await db.execute(
            select(Farm).where(Farm.user_id == user_id)
        )
        farms = result.scalars().all()
        if not farms:
            return "Tidak ada lahan. Buat lahan di aplikasi terlebih dahulu."

        today = date.today()
        lines = ["📋 *REKOMENDASI HARI INI*"]

        for farm in farms:
            fields_result = await db.execute(
                select(Field).where(Field.farm_id == farm.id)
            )
            fields = fields_result.scalars().all()
            for field in fields:
                cycles_result = await db.execute(
                    select(CropCycle).where(
                        CropCycle.field_id == field.id,
                        CropCycle.status == "active",
                    )
                )
                cycles = cycles_result.scalars().all()
                for cycle in cycles:
                    recs = await self.recommendation_engine.generate_recommendations(
                        db, cycle, field, farm
                    )
                    for r in recs:
                        if r.priority == "high" or r.timing == "today":
                            icon = "🔴" if r.priority == "high" else "🟡"
                            lines.append(f"\n{icon} *{farm.name} - {field.name}*")
                            lines.append(f"   {r.title}")
                            lines.append(f"   {r.reasoning[:100]}...")

        if len(lines) == 1:
            lines.append("Tidak ada rekomendasi hari ini.")
        return "\n".join(lines)

    async def _get_weather(self, db: AsyncSession, user_id: int) -> str:
        result = await db.execute(
            select(Farm).where(Farm.user_id == user_id)
        )
        farms = result.scalars().all()
        if not farms:
            return "Tidak ada data cuaca (belum ada lahan)."

        lines = ["🌤 *INFO CUACA*"]
        for farm in farms:
            if farm.latitude and farm.longitude:
                lines.append(f"\n📍 {farm.name}")
                lines.append(f"   {farm.latitude}, {farm.longitude}")
                lines.append("   (Integrasi cuaca penuh akan datang)")
            else:
                lines.append(f"\n📍 {farm.name}: Koordinat belum diatur")
        return "\n".join(lines)

    async def _get_schedule(self, db: AsyncSession, user_id: int) -> str:
        result = await db.execute(
            select(Farm).where(Farm.user_id == user_id)
        )
        farms = result.scalars().all()
        if not farms:
            return "Tidak ada jadwal."

        lines = ["📅 *JADWAL KEGIATAN*"]
        today = date.today()
        found = False

        for farm in farms:
            fields_result = await db.execute(
                select(Field).where(Field.farm_id == farm.id)
            )
            fields = fields_result.scalars().all()
            for field in fields:
                cycles_result = await db.execute(
                    select(CropCycle).where(
                        CropCycle.field_id == field.id,
                        CropCycle.status == "active",
                    )
                )
                cycles = cycles_result.scalars().all()
                for cycle in cycles:
                    recs = await self.recommendation_engine.generate_recommendations(
                        db, cycle, field, farm
                    )
                    for r in recs:
                        if r.timing:
                            found = True
                            icon = "🔴" if r.priority == "high" else "🟢"
                            lines.append(f"\n{icon} *{farm.name} - {field.name}*")
                            lines.append(f"   {r.title}")
                            lines.append(f"   🕐 {r.timing}")

        if not found:
            lines.append("Tidak ada jadwal mendatang.")
        return "\n".join(lines)

    async def _get_health(self, db: AsyncSession, user_id: int) -> str:
        result = await db.execute(
            select(Farm).where(Farm.user_id == user_id)
        )
        farms = result.scalars().all()
        if not farms:
            return "Tidak ada data kesehatan."

        lines = ["❤️ *KESEHATAN TANAMAN*"]
        for farm in farms:
            fields_result = await db.execute(
                select(Field).where(Field.farm_id == farm.id)
            )
            fields = fields_result.scalars().all()
            for field in fields:
                cycles_result = await db.execute(
                    select(CropCycle).where(
                        CropCycle.field_id == field.id,
                        CropCycle.status == "active",
                    )
                )
                cycles = cycles_result.scalars().all()
                for cycle in cycles:
                    health = await self.health_service.calculate_health_score(
                        db, cycle, field, farm
                    )
                    score = health["health_score"]
                    emoji = "✅" if score >= 70 else ("⚠️" if score >= 40 else "🚨")
                    lines.append(f"\n{emoji} *{farm.name} - {field.name}*")
                    lines.append(f"   Skor: {score}/100")
                    lines.append(f"   Status: {health['status']}")

        if len(lines) == 1:
            lines.append("Tidak ada tanaman aktif.")
        return "\n".join(lines)

    async def _ask_advisor(self, db: AsyncSession, user_id: int, question: str) -> str:
        result = await db.execute(
            select(Farm).where(Farm.user_id == user_id)
        )
        farms = result.scalars().all()
        if not farms:
            return "Maaf, Anda belum memiliki lahan. Silakan buat lahan melalui aplikasi AgriBrain AI terlebih dahulu."

        lines = [f"🤖 *PERTANYAAN ANDA:*"]
        lines.append(f"{question}")
        lines.append(f"\n*JAWABAN:*")

        for farm in farms[:1]:
            context = await self.context_builder.build_farm_context(db, farm.id)
            field_ids = [f["field"]["id"] for f in context.get("fields", [])]
            cycle_contexts = []
            for fid in field_ids:
                cycles_result = await db.execute(
                    select(CropCycle).where(
                        CropCycle.field_id == fid,
                        CropCycle.status == "active",
                    )
                )
                cycles = cycles_result.scalars().all()
                for c in cycles:
                    ctx = await self.context_builder.build_crop_cycle_context(db, c.id)
                    if ctx:
                        cycle_contexts.append(ctx)

            if cycle_contexts:
                latest = cycle_contexts[0]
                crop = latest.get("crop", {}).get("name", "Tanaman")
                age = latest.get("crop_age_days", 0)
                total_days = latest.get("crop", {}).get("growing_days", 90)
                progress = min(100, int(age / total_days * 100)) if total_days > 0 else 0
                lines.append(f"\n🌱 {crop} - Hari ke-{age} ({progress}%)")
                lines.append(f"📊 Status: {latest.get('crop_cycle', {}).get('status', 'aktif')}")

            if "pupuk" in question.lower() or "fertilizer" in question.lower():
                for ctx in cycle_contexts:
                    fert = ctx.get("fertilizer_history", [])
                    if fert:
                        last = fert[-1]
                        lines.append(f"\nPemupukan terakhir: {last.get('fertilizer_type', '-')} ({last.get('dosage_kg', '-')} kg)")
                    else:
                        lines.append("\nBelum ada catatan pemupukan.")
            elif "hama" in question.lower() or "penyakit" in question.lower() or "disease" in question.lower():
                for ctx in cycle_contexts:
                    diseases = ctx.get("disease_history", [])
                    if diseases:
                        last = diseases[-1]
                        lines.append(f"\nPenyakit terakhir: {last.get('disease_name', '-')} (Severitas: {last.get('severity', '-')})")
                    else:
                        lines.append("\nTidak ada laporan penyakit.")
            elif "panen" in question.lower() or "harvest" in question.lower():
                for ctx in cycle_contexts:
                    harvest = ctx.get("harvest_history", [])
                    if harvest:
                        total = sum(h.get("quantity_kg", 0) for h in harvest)
                        lines.append(f"\nTotal panen: {total} kg")
                    else:
                        expected = latest.get("crop_cycle", {}).get("expected_harvest_date", "Belum diatur")
                        lines.append(f"\nTarget panen: {expected}")
            else:
                age = cycle_contexts[0].get("crop_age_days", 0) if cycle_contexts else 0
                if age < 30:
                    lines.append("\nFase pertumbuhan awal. Fokus pada pemupukan dasar dan penyiraman rutin.")
                elif age < 60:
                    lines.append("\nFase pertumbuhan vegetatif. Perhatikan kebutuhan pupuk N dan pengendalian gulma.")
                elif age < 80:
                    lines.append("\nFase generatif. Perhatikan kebutuhan air dan proteksi dari hama.")
                else:
                    lines.append("\nMendekati panen. Pantau kematangan dan siapkan alat panen.")

        return "\n".join(lines)


class ReminderScheduler:
    def __init__(self):
        self.whatsapp_handler = WhatsAppCommandHandler()

    async def check_and_send_reminders(self, db: AsyncSession):
        from app.models.crop import CropCycle

        today = date.today()
        prefs_result = await db.execute(
            select(ReminderPreference).where(ReminderPreference.whatsapp_enabled == True)
        )
        prefs = prefs_result.scalars().all()

        for pref in prefs:
            user_id = pref.user_id
            session_result = await db.execute(
                select(WhatsAppSession).where(
                    WhatsAppSession.user_id == user_id,
                    WhatsAppSession.is_verified == True,
                )
            )
            session = session_result.scalar_one_or_none()
            if not session:
                continue

            farms_result = await db.execute(
                select(Farm).where(Farm.user_id == user_id)
            )
            farms = farms_result.scalars().all()

            for farm in farms:
                fields_result = await db.execute(
                    select(Field).where(Field.farm_id == farm.id)
                )
                fields = fields_result.scalars().all()

                for field in fields:
                    cycles_result = await db.execute(
                        select(CropCycle).where(
                            CropCycle.field_id == field.id,
                            CropCycle.status == "active",
                        )
                    )
                    cycles = cycles_result.scalars().all()

                    for cycle in cycles:
                        recs = await self._generate_recs(db, cycle, field, farm)
                        await self._process_recs_as_reminders(
                            db, pref, session, recs, user_id, farm, field, today
                        )

    async def _generate_recs(self, db, cycle, field, farm) -> list:
        engine = RecommendationEngine()
        return await engine.generate_recommendations(db, cycle, field, farm)

    async def _process_recs_as_reminders(self, db, pref, session, recs, user_id, farm, field, today):

        for rec in recs:
            if rec.timing == "today" or (rec.timing and "hari" in rec.timing):
                log_result = await db.execute(
                    select(NotificationLog).where(
                        NotificationLog.user_id == user_id,
                        NotificationLog.notification_type == rec.type,
                        NotificationLog.title == rec.title,
                        NotificationLog.sent_at >= func.now() - timedelta(hours=24),
                    )
                )
                existing = log_result.scalar_one_or_none()
                if existing:
                    continue

                header = f"🌾 *{farm.name} - {field.name}*\n"
                body = f"📌 *{rec.title}*\n{rec.description}\n\n{rec.reasoning}"
                if rec.dosage:
                    body += f"\nDosis: {rec.dosage}"
                message = header + body

                provider = get_provider()
                result = await provider.send_message(session.phone_number, message)

                log = NotificationLog(
                    user_id=user_id,
                    phone_number=session.phone_number,
                    notification_type=rec.type,
                    title=rec.title,
                    message=message,
                    data={"farm_name": farm.name, "field_name": field.name, "priority": rec.priority},
                    status=result.get("status", "sent"),
                    provider_message_id=result.get("message_id"),
                )
                db.add(log)
