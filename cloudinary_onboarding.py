import cloudinary
import cloudinary.uploader
import cloudinary.api

# ── Konfigurasi Cloudinary ──
cloudinary.config(
    cloud_name="ddjnmdc5o",
    api_key="365376354221847",
    api_secret="DiPxe8ggRRTNZFaJ_iyurstZbkI",
)

# ── 1. Upload sample image dari domain demo Cloudinary ──
print("[1/3] Mengupload gambar...")
upload_result = cloudinary.uploader.upload(
    "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    public_id="onboarding_sample",
    overwrite=True,
)
secure_url = upload_result["secure_url"]
public_id = upload_result["public_id"]
print("  Upload berhasil!")
print(f"  Secure URL  : {secure_url}")
print(f"  Public ID   : {public_id}")

# ── 2. Ambil metadata gambar ──
print("\n[2/3] Metadata gambar:")
print(f"  Width       : {upload_result['width']} px")
print(f"  Height      : {upload_result['height']} px")
print(f"  Format      : {upload_result['format']}")
print(f"  File size   : {upload_result['bytes']} bytes")

# ── 3. Generate transformed URL (f_auto + q_auto) ──
# f_auto (fetch_format=auto): browser otomatis pilih format paling efisien
# q_auto (quality=auto): Cloudinary otomatis turunkan kualitas tanpa mengurangi kualitas visual
transformed_url = cloudinary.CloudinaryImage(public_id).build_url(
    transformation=[
        {"quality": "auto", "fetch_format": "auto"},
    ]
)
print("\n[3/3] Selesai! Klik link di bawah untuk melihat versi optimal gambar.")
print("  Cek ukuran file dan format-nya.")
print(f"  {transformed_url}")
