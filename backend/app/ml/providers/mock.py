import random
from typing import Optional
import numpy as np
from app.ml.providers.base import BaseVisionProvider, DetectionResult


DISEASE_LABELS = [
    "anthracnose",
    "bacterial wilt",
    "fusarium wilt",
    "leaf curl virus",
    "thrips damage",
    "mite damage",
    "magnesium deficiency",
    "calcium deficiency",
    "nitrogen deficiency",
]

TREATMENTS = {
    "anthracnose": [
        "Semprot fungisida berbahan aktif azoxystrobin 2 ml/L air",
        "Buang bagian tanaman yang terinfeksi berat",
        "Perbaiki sirkulasi udara antar tanaman",
    ],
    "bacterial wilt": [
        "Tidak ada pengobatan kimia yang efektif",
        "Cabut dan musnahkan tanaman sakit beserta akar",
        "Lakukan rotasi tanaman dengan non-solanaceae minimal 2 musim",
    ],
    "fusarium wilt": [
        "Aplikasi fungisida benomyl 1 g/L air, kocor ke pangkal batang",
        "Cabut dan musnahkan tanaman yang terinfeksi berat",
        "Lakukan solarisasi tanah sebelum tanam berikutnya",
    ],
    "leaf curl virus": [
        "Kendalikan vektor (kutu kebul) dengan insektisida berbahan aktif imidacloprid 1 ml/L",
        "Gunakan mulsa plastik perak untuk mengusir vektor",
        "Cabut tanaman yang terinfeksi berat untuk mengurangi sumber inokulum",
    ],
    "thrips damage": [
        "Aplikasi insektisida berbahan aktif spinosad 0.5 ml/L",
        "Pasang perangkap kuning (sticky trap) di sekitar tanaman",
        "Lakukan penyemprotan pada pagi atau sore hari",
    ],
    "mite damage": [
        "Aplikasi akarisida berbahan aktif abamektin 1 ml/L",
        "Hindari penggunaan pestisida broad-spectrum yang membunuh predator alami",
        "Jaga kelembaban tanaman dengan penyiraman rutin",
    ],
    "magnesium deficiency": [
        "Aplikasi pupuk MgSO4 (kieserite) 10-20 g/tanaman",
        "Semprot daun dengan larutan MgSO4 2-3 g/L",
        "Seimbangkan pemupukan K dan Mg",
    ],
    "calcium deficiency": [
        "Aplikasi kalsium nitrat atau dolomit 2-3 ton/ha",
        "Semprot daun dengan CaCl2 2 g/L saat fase pertumbuhan aktif",
        "Jaga kelembaban tanah tetap stabil",
    ],
    "nitrogen deficiency": [
        "Aplikasi pupuk urea 100-150 kg/ha atau ZA 200-250 kg/ha",
        "Semprot daun dengan urea 5 g/L sebagai pupuk cair",
        "Perbaiki drainase untuk mencegah pencucian nitrogen",
    ],
}

PREVENTION = {
    "anthracnose": [
        "Gunakan benih bersertifikat yang tahan penyakit",
        "Lakukan rotasi tanaman dengan famili berbeda",
        "Jaga kebersihan lahan dari sisa-sisa tanaman sakit",
    ],
    "bacterial wilt": [
        "Gunakan benih tahan layu bakteri",
        "Lakukan rotasi tanaman minimal 3 tahun",
        "Sterilisasi alat tanam dengan desinfektan",
    ],
    "fusarium wilt": [
        "Gunakan varietas tahan Fusarium",
        "Perbaiki drainase tanah",
        "Lakukan pencangkulan tanah untuk mengurangi inokulum di tanah",
    ],
    "leaf curl virus": [
        "Gunakan bibit bebas virus",
        "Pasang screen house atau net anti-serangga",
        "Lakukan pengendalian vektor sejak awal tanam",
    ],
    "thrips damage": [
        "Gunakan mulsa plastik untuk menekan populasi thrips",
        "Lakukan monitoring rutin dengan perangkap kuning",
        "Tanam tanaman perangkap di sekitar lahan",
    ],
    "mite damage": [
        "Lakukan pengairan yang cukup untuk menjaga kelembaban",
        "Konservasi musuh alami seperti kumbang Coccinellidae",
        "Hindari stres pada tanaman dengan pemupukan berimbang",
    ],
    "magnesium deficiency": [
        "Lakukan analisis tanah sebelum tanam",
        "Aplikasi dolomit atau kapur magnesium pada tanah masam",
        "Seimbangkan pemupukan K:Mg dengan rasio 2:1",
    ],
    "calcium deficiency": [
        "Lakukan pengapuran pada tanah masam",
        "Hindari pemupukan N berlebihan yang mengganggu serapan Ca",
        "Pastikan kelembaban tanah konsisten",
    ],
    "nitrogen deficiency": [
        "Lakukan pemupukan berimbang sesuai kebutuhan tanaman",
        "Gunakan pupuk slow-release untuk mengurangi pencucian",
        "Lakukan analisis jaringan tanaman secara periodik",
    ],
}


class MockVisionProvider(BaseVisionProvider):
    def __init__(self):
        self._loaded = False

    @property
    def model_name(self) -> str:
        return "mock-vision-v1"

    @property
    def is_ready(self) -> bool:
        return self._loaded

    async def load_model(self) -> bool:
        self._loaded = True
        return True

    async def detect(self, image: np.ndarray) -> DetectionResult:
        idx = random.randint(0, len(DISEASE_LABELS) - 1)
        disease_key = DISEASE_LABELS[idx]
        display_name = disease_key.replace("_", " ").title()
        severity = round(random.uniform(10, 90), 1)
        confidence = round(random.uniform(0.7, 0.99), 2)

        h, w = image.shape[:2]
        bx, by = random.randint(0, w // 2), random.randint(0, h // 2)
        bw, bh = random.randint(w // 4, w // 2), random.randint(h // 4, h // 2)

        boxes = [
            {
                "x1": bx,
                "y1": by,
                "x2": min(bx + bw, w),
                "y2": min(by + bh, h),
                "confidence": round(random.uniform(0.7, 0.95), 2),
                "label": display_name,
            }
        ]

        yield_loss = round(severity * 0.6, 1)
        revenue_loss = round(severity * 50000, -3)

        return DetectionResult(
            disease_name=display_name,
            confidence=confidence,
            severity=severity,
            bounding_boxes=boxes,
            recommendations=TREATMENTS.get(disease_key, [
                "Konsultasikan dengan agronomis lapangan"
            ]),
            prevention=PREVENTION.get(disease_key, [
                "Terapkan praktik budidaya yang baik (Good Agricultural Practices)"
            ]),
            economic_risk={
                "estimated_yield_loss_percent": yield_loss,
                "estimated_revenue_loss_per_hectare": revenue_loss,
                "currency": "IDR",
                "risk_level": "RENDAH" if severity < 30 else "SEDANG" if severity < 60 else "TINGGI",
            },
        )
