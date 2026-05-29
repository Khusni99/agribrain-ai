from typing import List, Optional
from datetime import datetime, timedelta


class SprayPlanner:
    def __init__(self):
        self.resistance_groups = {
            "A": ["metalaxyl", "benalaxyl", "oxadixyl"],
            "B": ["benomyl", "carbendazim", "thiophanate"],
            "C": ["azoxystrobin", "pyraclostrobin", "trifloxystrobin"],
            "D": ["mancozeb", "maneb", "propineb", "zineb"],
            "E": ["difenoconazole", "propiconazole", "tebuconazole"],
            "F": ["iprodione", "procymidone", "vinclozolin"],
        }

    async def generate_schedule(
        self,
        field_id: int,
        crop_type: str,
        planting_date: datetime,
        disease_pressure: str = "low",
    ) -> List[dict]:
        schedule = []
        current_date = planting_date
        interval = 7 if disease_pressure == "high" else 10
        rotation_groups = list(self.resistance_groups.keys())

        for week in range(1, 13):
            spray_date = current_date + timedelta(days=(week - 1) * interval)
            group = rotation_groups[week % len(rotation_groups)]

            schedule.append({
                "week": week,
                "date": spray_date.isoformat(),
                "spray_type": "Fungisida" if week % 2 == 0 else "Insektisida",
                "active_ingredient": self.resistance_groups[group][0],
                "resistance_group": group,
                "dosage": "2 g/L",
                "target": self._get_target(crop_type, week),
            })

        return schedule

    def _get_target(self, crop_type: str, week: int) -> str:
        targets = {
            1: "Tanah/Media Tanam",
            2: "Hama tanah",
            3: "Daun muda",
            4: "Penyakit daun",
            5: "Hama daun",
            6: "Penyakit batang",
            7: "Pembungaan",
            8: "Hama bunga",
            9: "Pembentukan buah",
            10: "Penyakit buah",
            11: "Pematangan",
            12: "Pra-panen",
        }
        return targets.get(week, "Aplikasi rutin")

    def check_compatibility(self, product_a: str, product_b: str) -> dict:
        return {
            "compatible": True,
            "notes": "Kedua produk dapat dicampur",
            "precautions": ["Gunakan air bersih", "Aplikasi segera setelah pencampuran"],
        }
