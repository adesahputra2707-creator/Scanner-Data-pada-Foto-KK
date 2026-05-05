import streamlit as st
import easyocr
import pandas as pd
import numpy as np
import re
from PIL import Image, ImageOps

# Konfigurasi tampilan HP
st.set_page_config(page_title="KK Scanner Mobile", layout="centered")

st.title("📸 KK Scanner Pro (Mobile)")
st.write("Versi Stabil - Dioptimalkan untuk Website & HP")

# Load OCR dengan caching agar cepat
@st.cache_resource
def load_reader():
    # Menggunakan 'id' untuk bahasa Indonesia
    return easyocr.Reader(['id'], gpu=False) # gpu=False agar stabil di server gratis

reader = load_reader()

uploaded_file = st.file_uploader("Ambil Foto atau Unggah KK", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 1. Optimasi Gambar (Sangat Penting agar tidak Error)
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image) # Memperbaiki rotasi otomatis dari HP
    
    # Perkecil ukuran jika terlalu besar (agar server cloud tidak crash)
    if image.width > 1500:
        image = image.resize((1500, int(image.height * 1500 / image.width)))
    
    st.image(image, caption="Foto Berhasil Diunggah", use_container_width=True)

    if st.button("🔍 Mulai Ekstrak Data"):
        with st.spinner("Mesin sedang membaca teks... (Proses ini memakan waktu 10-30 detik)"):
            try:
                img_np = np.array(image.convert('RGB'))
                results = reader.readtext(img_np, detail=0)
                
                if not results:
                    st.error("Gagal membaca teks. Pastikan foto terang dan tulisan jelas.")
                else:
                    full_text = " ".join(results).upper()
                    
                    # Logika Pencarian Data (Regex)
                    no_kk = re.search(r'\d{16}', full_text)
                    kk_val = no_kk.group(0) if no_kk else "Tidak ditemukan"
                    
                    # Ambil semua NIK yang terdeteksi
                    all_niks = list(set(re.findall(r'\b\d{16}\b', full_text)))
                    if kk_val in all_niks: all_niks.remove(kk_val)
                    
                    # Tampilkan Hasil
                    st.success(f"Ditemukan {len(all_niks)} NIK")
                    
                    data_final = []
                    for nik in sorted(all_niks):
                        data_final.append({
                            "No KK": kk_val,
                            "NIK": nik,
                            "Nama": "Klik untuk Edit",
                            "Hubungan": "Edit Hubungan",
                            "Ayah/Ibu": "Edit Orang Tua"
                        })
                    
                    df = pd.DataFrame(data_final)
                    
                    st.subheader("📝 Hasil Ekstraksi (Bisa Diedit)")
                    # Tabel yang bisa langsung diedit di layar HP
                    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
                    
                    # Export
                    csv = edited_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Excel (CSV)", csv, "data_kk.csv", "text/csv")
            
            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {e}")
                st.info("Saran: Gunakan foto dengan ukuran file yang lebih kecil atau pencahayaan lebih baik.")
