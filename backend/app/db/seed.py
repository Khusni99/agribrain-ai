import asyncio
from sqlalchemy import select
from app.database import async_session_factory
from app.models.crop import Crop
from app.models.marketplace import MarketPrice, ProductStatus
from app.models.user import User
from app.core.security import hash_password


CROPS = [
    {"name": "Cabai Merah", "variety": "Cabai Besar", "category": "hortikultura", "growing_days": 90, "optimal_temp_min": 20.0, "optimal_temp_max": 32.0, "optimal_ph_min": 5.5, "optimal_ph_max": 6.8, "water_requirement_mm": 600.0, "description": "Cabai merah besar, cocok untuk dataran rendah hingga menengah"},
    {"name": "Cabai Rawit", "variety": "Rawit Merah", "category": "hortikultura", "growing_days": 95, "optimal_temp_min": 20.0, "optimal_temp_max": 32.0, "optimal_ph_min": 5.5, "optimal_ph_max": 6.8, "water_requirement_mm": 550.0, "description": "Cabai rawit dengan pedas tinggi, varietas unggul"},
    {"name": "Tomat", "variety": "Tomat Ceri", "category": "hortikultura", "growing_days": 80, "optimal_temp_min": 18.0, "optimal_temp_max": 28.0, "optimal_ph_min": 6.0, "optimal_ph_max": 6.8, "water_requirement_mm": 500.0, "description": "Tomat ceri manis, permintaan pasar tinggi"},
    {"name": "Tomat", "variety": "Tomat Beef", "category": "hortikultura", "growing_days": 85, "optimal_temp_min": 18.0, "optimal_temp_max": 28.0, "optimal_ph_min": 6.0, "optimal_ph_max": 6.8, "water_requirement_mm": 500.0, "description": "Tomat beef besar, cocok untuk restoran"},
    {"name": "Padi", "variety": "IR 64", "category": "pangan", "growing_days": 110, "optimal_temp_min": 20.0, "optimal_temp_max": 35.0, "optimal_ph_min": 5.0, "optimal_ph_max": 6.5, "water_requirement_mm": 1200.0, "description": "Padi IR 64, umur genjah, produksi tinggi"},
    {"name": "Padi", "variety": "Ciherang", "category": "pangan", "growing_days": 115, "optimal_temp_min": 20.0, "optimal_temp_max": 35.0, "optimal_ph_min": 5.0, "optimal_ph_max": 6.5, "water_requirement_mm": 1200.0, "description": "Padi Ciherang, tahan hama, hasil optimal"},
    {"name": "Kubis", "variety": "Kubis Putih", "category": "hortikultura", "growing_days": 85, "optimal_temp_min": 15.0, "optimal_temp_max": 25.0, "optimal_ph_min": 6.0, "optimal_ph_max": 7.5, "water_requirement_mm": 450.0, "description": "Kubis putih besar, cocok dataran tinggi"},
    {"name": "Kubis", "variety": "Kubis Ungu", "category": "hortikultura", "growing_days": 90, "optimal_temp_min": 15.0, "optimal_temp_max": 25.0, "optimal_ph_min": 6.0, "optimal_ph_max": 7.5, "water_requirement_mm": 450.0, "description": "Kubis ungu kaya antioksidan, nilai jual tinggi"},
    {"name": "Bawang Merah", "variety": "Bima Brebes", "category": "hortikultura", "growing_days": 70, "optimal_temp_min": 13.0, "optimal_temp_max": 24.0, "optimal_ph_min": 6.0, "optimal_ph_max": 7.0, "water_requirement_mm": 350.0, "description": "Bawang merah varietas Bima, umur pendek"},
    {"name": "Bawang Merah", "variety": "Tajuk", "category": "hortikultura", "growing_days": 75, "optimal_temp_min": 13.0, "optimal_temp_max": 24.0, "optimal_ph_min": 6.0, "optimal_ph_max": 7.0, "water_requirement_mm": 350.0, "description": "Bawang merah Tajuk, cocok untuk dataran rendah"},
    {"name": "Jagung", "variety": "Jagung Hibrida", "category": "pangan", "growing_days": 95, "optimal_temp_min": 18.0, "optimal_temp_max": 32.0, "optimal_ph_min": 5.8, "optimal_ph_max": 7.0, "water_requirement_mm": 500.0, "description": "Jagung hibrida produktivitas tinggi"},
    {"name": "Jagung", "variety": "Jagung Manis", "category": "pangan", "growing_days": 75, "optimal_temp_min": 18.0, "optimal_temp_max": 32.0, "optimal_ph_min": 5.8, "optimal_ph_max": 7.0, "water_requirement_mm": 450.0, "description": "Jagung manis, umur pendek, permintaan tinggi"},
    {"name": "Terong", "variety": "Terong Ungu", "category": "hortikultura", "growing_days": 80, "optimal_temp_min": 20.0, "optimal_temp_max": 30.0, "optimal_ph_min": 5.5, "optimal_ph_max": 6.8, "water_requirement_mm": 400.0, "description": "Terong ungu panjang, varietas unggul"},
    {"name": "Kangkung", "variety": "Kangkung Darat", "category": "hortikultura", "growing_days": 30, "optimal_temp_min": 20.0, "optimal_temp_max": 35.0, "optimal_ph_min": 5.5, "optimal_ph_max": 7.0, "water_requirement_mm": 300.0, "description": "Kangkung darat, umur sangat pendek 30 hari"},
    {"name": "Bayam", "variety": "Bayam Hijau", "category": "hortikultura", "growing_days": 25, "optimal_temp_min": 18.0, "optimal_temp_max": 30.0, "optimal_ph_min": 6.0, "optimal_ph_max": 7.5, "water_requirement_mm": 250.0, "description": "Bayam hijau, umur pendek 25 hari panen"},
]

MARKET_PRICES = [
    {"commodity": "Cabai Merah", "location": "Jakarta", "min_price": 25000, "max_price": 45000, "avg_price": 35000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Cabai Rawit", "location": "Jakarta", "min_price": 35000, "max_price": 65000, "avg_price": 50000, "trend": "naik", "source": "Kementan"},
    {"commodity": "Bawang Merah", "location": "Jakarta", "min_price": 18000, "max_price": 30000, "avg_price": 24000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Tomat", "location": "Jakarta", "min_price": 8000, "max_price": 15000, "avg_price": 11000, "trend": "turun", "source": "Kementan"},
    {"commodity": "Padi", "location": "Karawang", "min_price": 5000, "max_price": 7000, "avg_price": 6000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Jagung", "location": "Jakarta", "min_price": 4000, "max_price": 6000, "avg_price": 5000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Kubis", "location": "Jakarta", "min_price": 5000, "max_price": 10000, "avg_price": 7000, "trend": "turun", "source": "Kementan"},
    {"commodity": "Terong", "location": "Jakarta", "min_price": 6000, "max_price": 12000, "avg_price": 9000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Kangkung", "location": "Jakarta", "min_price": 3000, "max_price": 6000, "avg_price": 4500, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Bayam", "location": "Jakarta", "min_price": 4000, "max_price": 7000, "avg_price": 5500, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Cabai Merah", "location": "Surabaya", "min_price": 22000, "max_price": 40000, "avg_price": 31000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Bawang Merah", "location": "Brebes", "min_price": 15000, "max_price": 25000, "avg_price": 20000, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Padi", "location": "Indramayu", "min_price": 4800, "max_price": 6500, "avg_price": 5600, "trend": "naik", "source": "Kementan"},
    {"commodity": "Jagung", "location": "Kediri", "min_price": 3800, "max_price": 5500, "avg_price": 4600, "trend": "stabil", "source": "Kementan"},
    {"commodity": "Tomat", "location": "Bandung", "min_price": 7000, "max_price": 14000, "avg_price": 10000, "trend": "stabil", "source": "Kementan"},
]

FERTILIZER_REFERENCES = [
    {"name": "Urea", "type": "N", "n_pct": 46.0, "p_pct": 0.0, "k_pct": 0.0, "is_organic": False, "usage": "Pupuk dasar dan susulan"},
    {"name": "NPK 16-16-16", "type": "NPK", "n_pct": 16.0, "p_pct": 16.0, "k_pct": 16.0, "is_organic": False, "usage": "Pupuk utama tanaman"},
    {"name": "NPK 15-15-15", "type": "NPK", "n_pct": 15.0, "p_pct": 15.0, "k_pct": 15.0, "is_organic": False, "usage": "Pupuk utama alternatif"},
    {"name": "ZA", "type": "N", "n_pct": 21.0, "p_pct": 0.0, "k_pct": 0.0, "is_organic": False, "usage": "Pupuk nitrogen tambahan"},
    {"name": "KNO3", "type": "NK", "n_pct": 13.0, "p_pct": 0.0, "k_pct": 46.0, "is_organic": False, "usage": "Pupuk buah dan bunga"},
    {"name": "MKP", "type": "PK", "n_pct": 0.0, "p_pct": 52.0, "k_pct": 34.0, "is_organic": False, "usage": "Pupuk pembungaan dan pembuahan"},
    {"name": "KCl", "type": "K", "n_pct": 0.0, "p_pct": 0.0, "k_pct": 60.0, "is_organic": False, "usage": "Pupuk kalium tinggi"},
    {"name": "Pupuk Kandang Sapi", "type": "Organik", "n_pct": 0.5, "p_pct": 0.2, "k_pct": 0.5, "is_organic": True, "usage": "Pupuk organik dasar"},
    {"name": "Pupuk Kandang Ayam", "type": "Organik", "n_pct": 1.0, "p_pct": 0.8, "k_pct": 0.4, "is_organic": True, "usage": "Pupuk organik cepat serap"},
    {"name": "Kompos", "type": "Organik", "n_pct": 1.5, "p_pct": 0.5, "k_pct": 1.0, "is_organic": True, "usage": "Pupuk organik perbaikan tanah"},
    {"name": "Pupuk Hayati", "type": "Organik", "n_pct": 0.0, "p_pct": 0.0, "k_pct": 0.0, "is_organic": True, "usage": "Mikroorganisme tanah"},
]

DISEASE_RULES = [
    {"disease": "Antraknosa", "crops": "cabai,tomat", "symptoms": "Bercak coklat kehitaman pada buah dan daun", "causes": "Colletotrichum spp.", "severity": "tinggi", "treatment": "Semprot fungisida azoxystrobin 2 ml/L atau mancozeb 2 g/L setiap 5-7 hari", "prevention": "Rotasi tanaman, benih sehat, sanitasi lahan"},
    {"disease": "Layu Fusarium", "crops": "cabai,tomat,terong", "symptoms": "Layu pada siang hari, daun menguning, pembuluh batang coklat", "causes": "Fusarium oxysporum", "severity": "tinggi", "treatment": "Fungisida sistemik benomyl 1 g/L, cabut tanaman sakit", "prevention": "Solarisasi tanah, rotasi tanaman dengan non-solanaceae"},
    {"disease": "Layu Bakteri", "crops": "cabai,tomat,kentang", "symptoms": "Layu mendadak, batang berlendir saat dipotong", "causes": "Ralstonia solanacearum", "severity": "sangat_tinggi", "treatment": "Tidak ada obat kimia efektif, cabut dan musnahkan", "prevention": "Rotasi tanaman, agen hayati Pseudomonas fluorescens"},
    {"disease": "Virus Kuning", "crops": "cabai,tomat", "symptoms": "Daun menguning, menggulung, tanaman kerdil", "causes": "Begomovirus (kutu kebul)", "severity": "tinggi", "treatment": "Kendalikan vektor kutu kebul dengan imidacloprid 1 ml/L", "prevention": "Mulsa plastik perak, tanaman perangkap, musuh alami"},
    {"disease": "Busuk Phytophthora", "crops": "cabai,tomat,kakao", "symptoms": "Busuk basah pada akar dan pangkal batang", "causes": "Phytophthora capsici", "severity": "tinggi", "treatment": "Metalaxyl 2 g/L, perbaiki drainase", "prevention": "Drainase baik, bedengan tinggi, irigasi terkontrol"},
    {"disease": "Bercak Daun Cercospora", "crops": "cabai,kubis", "symptoms": "Bercak coklat dengan halo kuning pada daun", "causes": "Cercospora spp.", "severity": "sedang", "treatment": "Fungisida tembaga 3 g/L setiap 7 hari", "prevention": "Kurangi kelembaban, jarak tanam tidak terlalu rapat"},
    {"disease": "Busuk Daun", "crops": "bawang merah", "symptoms": "Bercak putih pada daun, ujung daun mengering", "causes": "Alternaria porri", "severity": "sedang", "treatment": "Mancozeb 2 g/L atau difenoconazole 1 ml/L", "prevention": "Rotasi tanaman, jangan tumpang sari dengan bawang"},
    {"disease": "Hawar Daun", "crops": "padi", "symptoms": "Bercak coklat berbentuk belah ketupat pada daun", "causes": "Pyricularia oryzae", "severity": "sangat_tinggi", "treatment": "Tricyclazole 1 g/L atau isoprothiolane 2 ml/L", "prevention": "Jarak tanam tidak rapat, pupuk N tidak berlebihan"},
    {"disease": "Blast Padi", "crops": "padi", "symptoms": "Bercak abu-abu pada daun dan leher malai", "causes": "Magnaporthe grisea", "severity": "sangat_tinggi", "treatment": "Fungisida berbahan aktif tebuconazole atau tricyclazole", "prevention": "Gunakan varietas tahan, atur jarak tanam"},
    {"disease": "Bulai", "crops": "jagung", "symptoms": "Daun muda bergaris kuning pucat, tanaman kerdil", "causes": "Peronosclerospora maydis", "severity": "tinggi", "treatment": "Metalaxyl 2 g/L, cabut tanaman terinfeksi", "prevention": "Gunakan benih bersertifikat, tanam serempak"},
    {"disease": "Hawar Bakteri", "crops": "padi", "symptoms": "Daun bergaris kuning basah hingga mengering", "causes": "Xanthomonas oryzae", "severity": "tinggi", "treatment": "Bakterisida tembaga, pemangkasan daun terinfeksi", "prevention": "Hindari pemupukan N berlebihan, drainase baik"},
    {"disease": "Embun Tepung", "crops": "cabai,tomat,kubis", "symptoms": "Bercak putih seperti tepung pada daun", "causes": "Oidium spp.", "severity": "sedang", "treatment": "Sulfur 3 g/L atau fungisida berbahan aktif penconazole", "prevention": "Sirkulasi udara baik, kurangi kelembaban"},
    {"disease": "Bercak Ungu", "crops": "bawang merah", "symptoms": "Bercak ungu pada daun dan umbi", "causes": "Alternaria porri + Stemphylium", "severity": "sedang", "treatment": "Mancozeb + metalaxyl 2 g/L, rotasi dengan fungisida tembaga", "prevention": "Benih sehat, rotasi tanaman 2-3 tahun"},
    {"disease": "Antraknosa Padi", "crops": "padi", "symptoms": "Bercak coklat gelap pada gabah", "causes": "Colletotrichum gloeosporioides", "severity": "sedang", "treatment": "Semprot fungisida berbahan aktif difenoconazole 1 ml/L", "prevention": "Gunakan benih sehat, perlakuan benih sebelum tanam"},
]


async def seed():
    from app.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        existing_crops = await session.execute(select(Crop))
        if existing_crops.scalars().first():
            print("Database already seeded, skipping...")
            return

        for crop_data in CROPS:
            session.add(Crop(**crop_data))
        print(f"Added {len(CROPS)} crops")

        for price_data in MARKET_PRICES:
            session.add(MarketPrice(**price_data))
        print(f"Added {len(MARKET_PRICES)} market prices")

        demo_user = User(
            email="demo@agribrain.ai",
            username="demo",
            hashed_password=hash_password("demo123"),
            full_name="Demo User",
            role="farmer",
        )
        session.add(demo_user)
        print("Added demo user (demo/demo123)")

        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
