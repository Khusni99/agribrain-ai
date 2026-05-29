from typing import Optional
from app.config import settings


class AgronomistAgent:
    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> dict:
        return {
            "crops": {
                "chili": {
                    "diseases": ["anthracnose", "phytophthora", "fusarium", "leaf_curl"],
                    "growth_stages": ["seedling", "vegetative", "flowering", "fruiting", "maturity"],
                    "optimal_temp": (20, 32),
                    "optimal_ph": (5.5, 6.8),
                },
                "tomato": {
                    "diseases": ["early_blight", "late_blight", "fusarium", "bacterial_wilt"],
                    "growth_stages": ["seedling", "vegetative", "flowering", "fruiting", "maturity"],
                    "optimal_temp": (18, 28),
                    "optimal_ph": (6.0, 6.8),
                },
                "rice": {
                    "diseases": ["blast", "bacterial_leaf_blight", "brown_spot", "sheath_blight"],
                    "growth_stages": ["seedling", "tillering", "booting", "flowering", "grain_filling"],
                    "optimal_temp": (20, 35),
                    "optimal_ph": (5.0, 6.5),
                },
                "cabbage": {
                    "diseases": ["black_rot", "clubroot", "downy_mildew", "alternaria"],
                    "growth_stages": ["seedling", "vegetative", "head_formation", "maturity"],
                    "optimal_temp": (15, 25),
                    "optimal_ph": (6.0, 7.5),
                },
                "onion": {
                    "diseases": ["purple_blotch", "downy_mildew", "basal_rot", "thrips"],
                    "growth_stages": ["seedling", "vegetative", "bulb_formation", "maturity"],
                    "optimal_temp": (13, 24),
                    "optimal_ph": (6.0, 7.0),
                },
                "corn": {
                    "diseases": ["northern_leaf_blight", "rust", "stalk_rot", "ear_rot"],
                    "growth_stages": ["germination", "vegetative", "tasseling", "silking", "grain_fill"],
                    "optimal_temp": (18, 32),
                    "optimal_ph": (5.8, 7.0),
                },
            },
            "nutrients": {
                "nitrogen": {"deficiency_symptoms": ["yellowing lower leaves", "stunted growth", "pale green"], "role": "vegetative growth"},
                "phosphorus": {"deficiency_symptoms": ["purple leaves", "poor root", "delayed flowering"], "role": "root development"},
                "potassium": {"deficiency_symptoms": ["leaf edge burn", "weak stems", "poor fruit"], "role": "fruit quality"},
                "calcium": {"deficiency_symptoms": ["leaf tip burn", "blossom end rot", "stunted roots"], "role": "cell wall strength"},
                "magnesium": {"deficiency_symptoms": ["interveinal chlorosis", "leaf curling"], "role": "chlorophyll production"},
                "boron": {"deficiency_symptoms": ["poor fruit set", "cracked stems", "hollow fruit"], "role": "flower development"},
                "zinc": {"deficiency_symptoms": ["small leaves", "rosette pattern", "short internodes"], "role": "enzyme activation"},
                "iron": {"deficiency_symptoms": ["yellowing young leaves", "green veins"], "role": "chlorophyll synthesis"},
            },
        }

    async def _call_llm(self, prompt: str) -> str:
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
        return self._rule_based_response(prompt)

    def _system_prompt(self) -> str:
        return """Anda adalah AgriBrain AI, seorang agronomist digital berpengalaman yang membantu petani Indonesia.
Anda memiliki pengetahuan mendalam tentang budidaya tanaman, hama, penyakit, nutrisi, dan praktik pertanian terbaik.

Panduan:
1. Analisis gejala dengan teliti
2. Berikan diagnosis dengan tingkat kepercayaan
3. Rekomendasikan tindakan yang praktis dan aman
4. Hindari rekomendasi pestisida berbahaya tanpa data yang jelas
5. Pertimbangkan kondisi cuaca dan lingkungan
6. Berikan penjelasan langkah demi langkah
7. Tanyakan informasi tambahan jika diperlukan

Gunakan bahasa Indonesia yang mudah dipahami petani.
"""

    def _rule_based_response(self, query: str) -> str:
        query_lower = query.lower()
        if "daun" in query_lower and "kuning" in query_lower:
            return self._diagnose_yellow_leaves(query)
        if "bercak" in query_lower:
            return self._diagnose_spots(query)
        if "layu" in query_lower:
            return self._diagnose_wilt(query)
        if "buah" in query_lower and "busuk" in query_lower:
            return self._diagnose_fruit_rot(query)
        return self._general_diagnosis(query)

    def _diagnose_yellow_leaves(self, query: str) -> str:
        return """**Analisis Gejala: Daun Menguning**

**Kemungkinan Penyebab:**

1. **Defisiensi Nitrogen** (Confidence: 70%)
   - Gejala: Daun tua menguning merata, dimulai dari ujung
   - Tindakan: Aplikasi Urea 150-200 kg/ha atau KNO3 5-10 g/tanaman

2. **Kekurangan Air** (Confidence: 50%)
   - Gejala: Daun menguning dan menggulung
   - Tindakan: Irigasi segera, pertahankan kelembaban tanah

3. **Serangan Fusarium** (Confidence: 40%)
   - Gejala: Menguning dimulai dari daun bawah, disertai layu
   - Tindakan: Aplikasi fungisida sistemik, perbaiki drainase

**Rekomendasi:**
- Lakukan uji tanah untuk konfirmasi
- Semprot dengan pupuk daun yang mengandung N tinggi
- Pantau perkembangan dalam 3-5 hari

**Tingkat Keparahan:** Ringan-Sedang
**Tindakan:** Segera
"""

    def _diagnose_spots(self, query: str) -> str:
        return """**Analisis Gejala: Bercak pada Daun**

**Kemungkinan Penyebab:**

1. **Antraknosa** (Confidence: 80%)
   - Gejala: Bercak coklat kehitaman, bentuk tidak teratur
   - Tindakan: Aplikasi fungisida berbahan aktif mancozeb atau dithiocarbamate

2. **Bercak Daun Cercospora** (Confidence: 60%)
   - Gejala: Bercak kecil coklat dengan halo kuning
   - Tindakan: Semprot dengan fungisida tembaga

3. **Serangan Bakteri** (Confidence: 40%)
   - Gejala: Bercak basah dengan tepi kuning
   - Tindakan: Aplikasi bakterisida, hindari percikan air

**Rekomendasi:**
- Kurangi kelembaban dengan perbaikan sirkulasi udara
- Buang daun yang terinfeksi berat
- Rotasi fungisida untuk mencegah resistensi

**Tingkat Keparahan:** Sedang
**Tindakan:** 1-2 hari
"""

    def _diagnose_wilt(self, query: str) -> str:
        return """**Analisis Gejala: Layu**

**Kemungkinan Penyebab:**

1. **Layu Fusarium** (Confidence: 75%)
   - Gejala: Layu pada siang hari, membaik di malam hari
   - Tindakan: Aplikasi fungisida sistemik + perbaikan drainase

2. **Layu Bakteri** (Confidence: 65%)
   - Gejala: Layu mendadak, batang berlendir saat dipotong
   - Tindakan: Tidak ada obat kimia yang efektif, cabut dan musnahkan

3. **Kekurangan Air** (Confidence: 45%)
   - Gejala: Layu seragam, tanah kering
   - Tindakan: Irigasi segera

**Rekomendasi:**
- Periksa batang dengan memotong melintang
- Uji drainase tanah
- Isolasi tanaman sakit

**Tingkat Keparahan:** Berat
**Tindakan:** Segera
"""

    def _diagnose_fruit_rot(self, query: str) -> str:
        return """**Analisis Gejala: Busuk Buah**

**Kemungkinan Penyebab:**

1. **Antraknosa Buah** (Confidence: 85%)
   - Gejala: Bercak coklat melekuk pada buah
   - Tindakan: Semprot dengan azoxystrobin + difenoconazole

2. **Busuk Phytophthora** (Confidence: 60%)
   - Gejala: Busuk basah, bau asam
   - Tindakan: Aplikasi fungisida berbahan aktif metalaxyl

3. **Blossom End Rot** (Confidence: 50%)
   - Gejala: Busuk pada ujung buah
   - Tindakan: Aplikasi kalsium, atur kelembaban merata

**Rekomendasi:**
- Buang buah yang terinfeksi
- Perbaiki aerasi tanaman
- Atur jadwal irigasi

**Tingkat Keparahan:** Berat
**Tindakan:** Segera
"""

    def _general_diagnosis(self, query: str) -> str:
        return """**Terima kasih atas informasinya.**

Berdasarkan gejala yang Anda deskripsikan, saya memerlukan informasi tambahan untuk memberikan diagnosis yang lebih akurat:

1. **Jenis tanaman apa?** (cabe, tomat, bawang, dll)
2. **Berapa umur tanaman?** (hari setelah tanam)
3. **Bagian mana yang terkena?** (daun atas/bawah, buah, batang)
4. **Kondisi cuaca akhir-akhir ini?** (hujan, panas, lembab)
5. **Apakah sudah ada perlakuan?** (pupuk, pestisida yang sudah diaplikasikan)

Silakan berikan informasi tambahan untuk diagnosis yang lebih tepat.
"""

    async def diagnose(
        self,
        query: str,
        crop_type: Optional[str] = None,
        language: str = "id",
        user_id: Optional[int] = None,
        field_id: Optional[int] = None,
    ) -> dict:
        diagnosis_text = await self._call_llm(query)

        possible_causes = [
            {"cause": "Defisiensi Nitrogen", "confidence": 70, "action": "Aplikasi Urea 150-200 kg/ha"},
            {"cause": "Kekurangan Air", "confidence": 50, "action": "Irigasi segera"},
            {"cause": "Fusarium Wilt", "confidence": 40, "action": "Fungisida sistemik"},
        ]

        return {
            "diagnosis": diagnosis_text,
            "possible_causes": possible_causes,
            "recommended_actions": [
                "Lakukan inspeksi lapangan secara detail",
                "Ambil sampel tanah dan daun untuk uji laboratorium",
                "Aplikasi perlakuan sesuai penyebab utama",
                "Pantau perkembangan setiap hari",
            ],
            "fertilizer_recommendations": [
                {"type": "NPK 16-16-16", "dosage": "200 kg/ha", "timing": "Setiap 2 minggu"},
                {"type": "Urea", "dosage": "100 kg/ha", "timing": "3-4 MST"},
            ],
            "spray_recommendations": [
                {"product": "Antracol 70 WP", "active_ingredient": "Propineb", "dosage": "2 g/L"},
            ],
            "confidence_score": 0.75,
            "follow_up_questions": [
                "Sudah berapa lama gejala muncul?",
                "Apakah ada tanaman lain yang terkena?",
                "Bagaimana kondisi drainase lahan?",
            ],
        }
