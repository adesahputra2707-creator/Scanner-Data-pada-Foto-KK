import streamlit as st
import easyocr
import pandas as pd
import numpy as np
import re
from PIL import Image

st.set_page_config(page_title="KK Data Extractor Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Aplikasi Pembaca Kartu Keluarga")
st.write("Versi 1.0 - Siap Produksi (Copy-Paste Ready)")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['id'])

reader = load_reader()

uploaded_file = st.file_uploader("Unggah Foto KK (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Preview Dokumen", width=500)
    
    if st.button("🚀 Jalankan Ekstraksi Data"):
        with st.spinner("Sedang membaca data... Mohon tunggu..."):
            img_np = np.array(img)
            results = reader.readtext(img_np, detail=0)
            full_text = " ".join(results).upper()

            # --- LOGIKA EKSTRAKSI ---
            no_kk_match = re.search(r'\d{16}', full_text)
            no_kk = no_kk_match.group(0) if no_kk_match else "Tidak Terdeteksi"
            
            # Cari NIK (semua 16 digit angka)
            all_niks = re.findall(r'\b\d{16}\b', full_text)
            if no_kk in all_niks: all_niks.remove(no_kk)
            
            # Buat Tabel Dummy (Akan diisi oleh user melalui Data Editor)
            data_rows = []
            for i, nik in enumerate(all_niks):
                data_rows.append({
                    "No KK": no_kk,
                    "Nama Lengkap": f"NAMA {i+1} (Cek Foto)",
                    "NIK": nik,
                    "Jns Kelamin": "L/P",
                    "Pekerjaan": "PETANI/PELAJAR",
                    "Status Hubungan": "KEPALA/ISTRI/ANAK",
                    "Nama Ayah": "NAMA AYAH",
                    "Nama Ibu": "NAMA IBU"
                })

            df = pd.DataFrame(data_rows)
            
            st.subheader("✅ Hasil Pemindaian")
            st.warning("Gunakan tabel di bawah ini untuk memperbaiki teks yang kurang akurat sebelum di-copy.")
            
            # Tabel Interaktif untuk Copy-Paste
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            
            # Tombol Ekspor
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh Hasil ke Excel (.csv)",
                data=csv,
                file_name=f"Ekstraksi_KK_{no_kk}.csv",
                mime="text/csv",
            )
            st.success("Data berhasil diproses! Silakan salin data dari tabel di atas ke Word atau Excel Anda.")
