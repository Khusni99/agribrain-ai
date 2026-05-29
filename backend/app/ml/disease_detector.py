from typing import Optional


class DiseaseDetector:
    def __init__(self):
        self.model_loaded = False
        self.disease_classes = [
            "anthracnose",
            "phytophthora",
            "fusarium_wilt",
            "bacterial_wilt",
            "leaf_curl_virus",
            "powdery_mildew",
            "downy_mildew",
            "thrips_damage",
            "mite_damage",
            "caterpillar_damage",
            "nitrogen_deficiency",
            "phosphorus_deficiency",
            "potassium_deficiency",
            "healthy",
        ]

    async def load_model(self):
        if not self.model_loaded:
            try:
                import torch
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.model_loaded = True
            except ImportError:
                self.model_loaded = False

    async def detect(self, image_bytes: bytes) -> dict:
        await self.load_model()
        return self._simulate_detection(image_bytes)

    def _simulate_detection(self, image_bytes: bytes) -> dict:
        import random
        idx = random.randint(0, len(self.disease_classes) - 1)
        disease = self.disease_classes[idx]
        severity = round(random.uniform(10, 90), 1)
        confidence = round(random.uniform(0.7, 0.99), 2)

        treatments = {
            "anthracnose": [
                "Semprot fungisida berbahan aktif azoxystrobin 2 ml/L",
                "Buang bagian tanaman yang terinfeksi berat",
                "Perbaiki sirkulasi udara antar tanaman",
            ],
            "phytophthora": [
                "Aplikasi fungisida sistemik metalaxyl 2 g/L",
                "Perbaiki drainase lahan",
                "Kurangi intensitas irigasi",
            ],
            "fusarium_wilt": [
                "Aplikasi fungisida benomyl 1 g/L",
                "Cabut dan musnahkan tanaman yang terinfeksi berat",
                "Lakukan solarisasi tanah sebelum tanam berikutnya",
            ],
            "bacterial_wilt": [
                "Tidak ada pengobatan kimia yang efektif",
                "Cabut dan musnahkan tanaman sakit",
                "Lakukan rotasi tanaman dengan non-solanaceae",
            ],
            "leaf_curl_virus": [
                "Kendalikan vektor (kutu kebul) dengan insektisida",
                "Aplikasi imidacloprid 1 ml/L",
                "Gunakan mulsa plastik perak untuk mengusir vektor",
            ],
            "powdery_mildew": [
                "Semprot fungisida berbahan aktif sulfur 3 g/L",
                "Tingkatkan sirkulasi udara",
                "Kurangi kelembaban dengan pengaturan irigasi",
            ],
            "downy_mildew": [
                "Aplikasi fungisida berbahan aktif mancozeb 2 g/L",
                "Hindari irigasi overhead pada sore hari",
                "Tingkatkan jarak tanam",
            ],
        }

        return {
            "disease_name": disease.replace("_", " ").title(),
            "severity_percentage": severity,
            "confidence_score": confidence,
            "treatment_recommendations": treatments.get(disease, ["Konsultasikan dengan agronomis lapangan"]),
            "economic_impact": {
                "estimated_yield_loss_percent": round(severity * 0.6, 1),
                "estimated_revenue_loss_per_hectare": round(severity * 50000, -3),
            },
        }
