from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.ai import RecommendationItem, RecommendationListResponse


class RecommendationEngine:
    FERTILIZER_SCHEDULE = [
        {"days": 14, "label": "Pupuk Dasar", "type": "NPK 16-16-16 + Urea", "dosage": "NPK 200 kg/ha + Urea 100 kg/ha"},
        {"days": 30, "label": "Pupuk Susulan I", "type": "NPK 16-16-16", "dosage": "150 kg/ha"},
        {"days": 45, "label": "Pupuk Susulan II", "type": "KNO3 + MKP", "dosage": "KNO3 40 kg/ha + MKP 15 kg/ha"},
        {"days": 60, "label": "Pupuk Tambahan", "type": "KNO3", "dosage": "30 kg/ha"},
    ]

    SPRAY_INTERVAL_DAYS = 10

    async def generate_all(
        self, context: dict, db: AsyncSession | None = None
    ) -> RecommendationListResponse:
        items = []
        items.extend(await self._fertilizer_recs(context))
        items.extend(await self._spray_recs(context))
        items.extend(await self._irrigation_recs(context))
        items.extend(await self._harvest_recs(context))

        today = [i for i in items if i.priority == "urgent" or (
            i.timing and self._is_today(i.timing)
        )]
        this_week = [i for i in items if i not in today and (
            i.timing and self._is_this_week(i.timing)
        )]
        urgent = [i for i in items if i.priority == "urgent"]

        return RecommendationListResponse(
            today=today[:5],
            this_week=this_week[:5],
            urgent=urgent[:5],
            all=items,
        )

    async def generate_for_types(
        self, context: dict, types: list[str], db: AsyncSession | None = None
    ) -> RecommendationListResponse:
        all_recs = await self.generate_all(context, db)
        filtered = [r for r in all_recs.all if r.type in types]
        return RecommendationListResponse(
            today=[r for r in filtered if r in all_recs.today],
            this_week=[r for r in filtered if r in all_recs.this_week],
            urgent=[r for r in filtered if r in all_recs.urgent],
            all=filtered,
        )

    async def _fertilizer_recs(self, context: dict) -> list[RecommendationItem]:
        items = []
        age = context.get("crop_age_days", 0)
        history = context.get("fertilizer_history", [])
        applied_fertilizers = {h["fertilizer_name"] for h in history}

        for s in self.FERTILIZER_SCHEDULE:
            days_remaining = s["days"] - age
            if 0 <= days_remaining <= 3:
                priority = "urgent"
            elif 0 < days_remaining <= 7:
                priority = "high"
            else:
                continue

            already_applied = any(
                f"{s['days']} hari" in h.get("growth_stage", "")
                for h in history
            )
            if already_applied:
                continue

            items.append(RecommendationItem(
                type="fertilizer",
                title=s["label"],
                description=f"Aplikasi {s['type']} ({s['dosage']})",
                priority=priority,
                timing=f"Hari ke-{s['days']} (sisa {days_remaining} hari)",
                dosage=s["dosage"],
                method="Tabur/Kocor",
                reasoning=f"Tanaman berumur {age} hari. {s['label']} diperlukan pada hari ke-{s['days']} untuk pertumbuhan optimal.",
            ))

        if not items and age > 0:
            last_fert = max(
                (int(h.get("id", 0)) for h in history),
                default=0,
            )
            days_since_last = age - 14
            if days_since_last > 21 and not any(
                "pupuk dasar" in h.get("growth_stage", "").lower()
                for h in history
            ):
                items.append(RecommendationItem(
                    type="fertilizer",
                    title="Peringatan Pemupukan",
                    description=f"Sudah {days_since_last} hari sejak tanam tanpa pemupukan tercatat",
                    priority="high",
                    reasoning="Riwayat pemupukan tidak ditemukan. Segera lakukan pemupukan dasar.",
                ))

        return items

    async def _spray_recs(self, context: dict) -> list[RecommendationItem]:
        items = []
        age = context.get("crop_age_days", 0)
        disease_history = context.get("disease_history", [])
        spray_history = context.get("spray_history", [])
        weather = context.get("weather", {})

        recent_disease = [d for d in disease_history if d.get("severity", 0) > 20]
        if recent_disease:
            worst = max(recent_disease, key=lambda d: d.get("severity_percentage", 0))
            items.append(RecommendationItem(
                type="spray",
                title=f"Semprot {worst['disease_name']}",
                description=f"Penanganan {worst['disease_name']} (severitas {worst.get('severity_percentage', 0)}%)",
                priority="urgent",
                dosage="Sesuai label produk",
                method="Semprot merata ke seluruh bagian tanaman",
                reasoning=f"Penyakit {worst['disease_name']} terdeteksi dengan tingkat keparahan {worst.get('severity_percentage', 0)}%. Segera lakukan tindakan pengendalian.",
            ))

        current_weather = weather.get("current", {})
        humidity = current_weather.get("humidity", 0)
        rainfall = current_weather.get("rainfall", 0)

        if humidity > 80 and rainfall > 5:
            items.append(RecommendationItem(
                type="spray",
                title="Semprot Fungisida Preventif",
                description="Kelembaban tinggi meningkatkan risiko penyakit jamur",
                priority="high",
                dosage="2 g/L",
                method="Semprot preventif",
                reasoning=f"Kelembaban {humidity}% dan curah hujan {rainfall}mm menciptakan kondisi ideal untuk perkembangan penyakit jamur.",
            ))

        if age > 0 and age % self.SPRAY_INTERVAL_DAYS == 0:
            items.append(RecommendationItem(
                type="spray",
                title="Semprot Rutin",
                description=f"Penyemprotan rutin minggu ke-{age // 7}",
                priority="medium",
                dosage="Sesuai jadwal",
                method="Semprot bergilir",
                reasoning=f"Jadwal penyemprotan rutin pada hari ke-{age}.",
            ))

        return items

    async def _irrigation_recs(self, context: dict) -> list[RecommendationItem]:
        items = []
        weather = context.get("weather", {})
        current = weather.get("current", {})
        rainfall = current.get("rainfall", 0)
        humidity = current.get("humidity", 0)
        age = context.get("crop_age_days", 0)

        if rainfall < 5 and humidity < 70:
            items.append(RecommendationItem(
                type="irrigation",
                title="Irigasi Diperlukan",
                description="Curah hujan rendah, lakukan irigasi tambahan",
                priority="high",
                timing="Segera",
                dosage="5-10 mm setara 50.000-100.000 L/ha",
                method="Irigasi tetes atau leb",
                reasoning=f"Curah hujan {rainfall}mm dan kelembaban {humidity}% di bawah optimal. Tanaman membutuhkan irigasi tambahan.",
            ))
        elif 5 <= rainfall < 15:
            items.append(RecommendationItem(
                type="irrigation",
                title="Pantau Kelembaban",
                description="Curah hujan cukup, pantau kelembaban tanah",
                priority="medium",
                reasoning=f"Curah hujan {rainfall}mm mencukupi, namun tetap pantau kondisi tanah.",
            ))

        if age > 50 and age < 80:
            items.append(RecommendationItem(
                type="irrigation",
                title="Irigasi Fase Pembuahan",
                description="Fase pembuahan membutuhkan air yang konsisten",
                priority="medium",
                timing=f"Hari ke-{age}",
                dosage="7-10 mm/hari",
                method="Irigasi tetes",
                reasoning=f"Tanaman memasuki fase pembuahan pada hari ke-{age}. Ketersediaan air yang konsisten penting untuk kualitas buah.",
            ))

        return items

    async def _harvest_recs(self, context: dict) -> list[RecommendationItem]:
        items = []
        cycle = context.get("active_crop_cycle") or context.get("crop_cycle", {})
        age = context.get("crop_age_days", 0)
        growing_days = cycle.get("crop_growing_days", 90) if isinstance(cycle, dict) else 90
        expected = cycle.get("expected_harvest_date") if isinstance(cycle, dict) else None

        if expected:
            try:
                harvest_date = datetime.fromisoformat(expected.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                days_to_harvest = (harvest_date.date() - now.date()).days

                if days_to_harvest <= 0:
                    items.append(RecommendationItem(
                        type="harvest",
                        title="Siap Panen!",
                        description="Tanaman sudah mencapai waktu panen yang dijadwalkan",
                        priority="urgent",
                        timing="Sekarang",
                        reasoning=f"Jadwal panen adalah {expected}. Segera lakukan pemanenan untuk hasil optimal.",
                    ))
                elif days_to_harvest <= 7:
                    items.append(RecommendationItem(
                        type="harvest",
                        title=f"Panen dalam {days_to_harvest} Hari",
                        description="Persiapkan alat dan tenaga panen",
                        priority="high",
                        timing=f"{days_to_harvest} hari lagi",
                        reasoning=f"Jadwal panen {expected}. Sisa {days_to_harvest} hari. Siapkan peralatan panen.",
                    ))
                elif days_to_harvest <= 14:
                    items.append(RecommendationItem(
                        type="harvest",
                        title=f"Pra-Panen: {days_to_harvest} Hari",
                        description="Hentikan aplikasi pestisida, siapkan panen",
                        priority="medium",
                        reasoning=f"Memasuki masa pra-panen {days_to_harvest} hari sebelum jadwal.",
                    ))
            except (ValueError, TypeError):
                pass

        if growing_days > 0 and age >= growing_days * 0.9:
            items.append(RecommendationItem(
                type="harvest",
                title="Periksa Kematangan",
                description=f"Tanaman sudah mencapai {age} hari ({age/growing_days*100:.0f}% dari masa tanam)",
                priority="medium",
                reasoning=f"Tanaman berumur {age} hari dari perkiraan {growing_days} hari. Periksa tanda-tanda kematangan panen.",
            ))

        return items

    def _is_today(self, timing: str) -> bool:
        return "sekarang" in timing.lower() or "sisa 0 hari" in timing.lower() or "segera" in timing.lower()

    def _is_this_week(self, timing: str) -> bool:
        return "hari" in timing.lower() and any(
            str(d) in timing for d in range(1, 8)
        )
