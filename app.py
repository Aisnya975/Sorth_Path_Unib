import streamlit as st
from geopy.distance import geodesic
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import folium
from streamlit_folium import st_folium
import requests

# 1. Konfigurasi Halaman (Futuristic/Dark Mode)
st.set_page_config(page_title="UNIB Neural-Route", page_icon="⚡", layout="wide")

# 2. Database Koordinat Akurat UNIB (Sudah diperbaiki 100% di Kandang Limun)
locations = {
    "Gerbang Utama UNIB": (-3.759496, 102.271708),
    "Rektorat UNIB": (-3.758550, 102.272500),
    "Perpustakaan Pusat": (-3.756500, 102.274800),
    "Dekanat Teknik (FT)": (-3.754500, 102.274800),
    "Lab Informatika": (-3.754200, 102.274900),
    "Fakultas Hukum (FH)": (-3.756500, 102.273200),
    "Dekanat FKIP": (-3.755200, 102.274500),
    "Fakultas Ekonomi & Bisnis (FEB)": (-3.757200, 102.272800),
    "Fakultas MIPA": (-3.753000, 102.274500),
    "Fakultas Pertanian (FP)": (-3.753500, 102.275200),
    "Fakultas Kedokteran (FK)": (-3.752500, 102.276000),
    "FISIP": (-3.756000, 102.273500),
    "GOR UNIB": (-3.754000, 102.272000),
    "Gerbang Belakang UNIB": (-3.751000, 102.275000)
}

# 3. Model AI Canggih (Random Forest Regressor)
X_train = np.array([
    [50, 10], [200, 20], [500, 50], [1000, 80], [1500, 90], 
    [50, 90], [200, 80], [500, 20], [1000, 10], [1500, 10]
]) 
y_train = np.array([1, 3, 8, 18, 25, 2, 5, 6, 12, 17]) 

model_ai = RandomForestRegressor(n_estimators=100, random_state=42)
model_ai.fit(X_train, y_train)

# 4. Fungsi Rute OSRM API (Menggunakan rute terdekat)
@st.cache_data
def get_real_route(lat1, lon1, lat2, lon2, mode="foot"):
    url = f"http://router.project-osrm.org/route/v1/{mode}/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            coords = data['routes'][0]['geometry']['coordinates']
            return [[coord[1], coord[0]] for coord in coords]
    except:
        pass
    return None

# 5. Kustomisasi UI Futuristik (Cyberpunk Style)
st.markdown("""
    <style>
    .stApp { background-color: #090a0f; color: #00ffcc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3 { color: #00ffcc !important; text-shadow: 0 0 10px rgba(0,255,204,0.5); }
    .stMetric { background: rgba(0, 255, 204, 0.03); border: 1px solid rgba(0, 255, 204, 0.3); border-left: 4px solid #ff007f; padding: 20px; border-radius: 8px; box-shadow: 0 0 15px rgba(0,255,204,0.1); }
    div[data-testid="stSidebar"] { background-color: #0b0d14; border-right: 1px solid #1a1f2e; }
    .stSlider > div > div > div > div { background-color: #ff007f !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Header UI ---
st.title("⚡ NEURAL-SYNC ROUTER // UNIB")
st.markdown("<p style='color:#a0aabf;'>Sistem Navigasi Cerdas Berbasis AI & Satelit Geospasial</p>", unsafe_allow_html=True)
st.write("---")

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("### 🎛️ SYSTEM CONTROL")
    
    origin = st.selectbox("Titik Ekstraksi (Asal):", list(locations.keys()), index=0)
    target = st.selectbox("Titik Infiltrasi (Tujuan):", list(locations.keys()), index=3)
    
    st.markdown("---")
    transport_mode = st.radio("Mode Transportasi:", [
        "🚶 Pejalan Kaki (Stealth)", 
        "🚲 Sepeda Kampus", 
        "🛵 Sepeda Motor", 
        "🚗 Mobil"
    ])
    
    st.markdown("---")
    traffic_level = st.slider("🚨 Tingkat Kepadatan (Wisuda/Event)", min_value=1, max_value=100, value=30)

    # Memaksa algoritma peta mengambil rute terpendek antar gedung (foot)
    if "Kaki" in transport_mode:
        osrm_mode, speed_modifier, color = "foot", 1.0, "#00ffff" # Cyan terang
    elif "Sepeda" in transport_mode:
        osrm_mode, speed_modifier, color = "foot", 0.4, "#ffff00" # Kuning terang
    elif "Motor" in transport_mode:
        osrm_mode, speed_modifier, color = "foot", 0.25 + (traffic_level/1000), "#ff00ff" # Magenta
    else:
        osrm_mode, speed_modifier, color = "foot", 0.35 + (traffic_level/200), "#ff3300" # Orange

# --- Logika Perhitungan ---
origin_coords = locations[origin]
target_coords = locations[target]

dist_geodesic = geodesic(origin_coords, target_coords).meters
base_pred_time = model_ai.predict([[dist_geodesic, traffic_level]])[0]
final_time = base_pred_time * speed_modifier

# --- Main Layout ---
col1, col2 = st.columns([1, 2.5])

with col1:
    st.subheader("📊 TELEMETRI DATA")
    if origin == target:
        st.warning("Titik asal dan tujuan tidak boleh sama.")
    else:
        st.metric("Jarak Analisis", f"{dist_geodesic:.0f} Meter")
        st.metric("Waktu Tempuh (AI)", f"{max(1, final_time):.1f} Menit")
        st.metric("Status Lalu Lintas", f"{traffic_level}% Kepadatan")
        
        st.write("---")
        st.subheader("🧠 ANALISIS SISTEM")
        if dist_geodesic < 50:
            st.success("Target terdeteksi di sekitar radius Anda.")
        elif traffic_level > 70 and "Mobil" in transport_mode:
            st.error("PERINGATAN: Rute sangat padat. Penggunaan mobil tidak disarankan. Ganti ke Motor atau Sepeda.")
        else:
            st.info(f"Rute optimal menggunakan {transport_mode.split()[1]}. Jalur aman untuk dilalui.")

with col2:
    st.subheader("🗺️ SATELIT GEOSPASIAL")
    
    mid_lat = (origin_coords[0] + target_coords[0]) / 2
    mid_lon = (origin_coords[1] + target_coords[1]) / 2

    # Buat Map dengan base kosong dulu
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=16)
    
    # Tambahkan Layer Satelit Dunia Nyata
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satelit HD',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Tambahkan Layer Nama Jalan di atas Satelit
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
        attr='CartoDB',
        name='Label Jalan',
        overlay=True,
        control=True
    ).add_to(m)

    # Marker Asal
    folium.Marker(
        [origin_coords[0], origin_coords[1]], 
        popup=f"<b>ASAL:</b> {origin}", 
        tooltip="Lokasi Asal",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

    # Marker Tujuan
    folium.Marker(
        [target_coords[0], target_coords[1]], 
        popup=f"<b>TUJUAN:</b> {target}", 
        tooltip="Lokasi Tujuan",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Dapatkan rute asli
    route_coords = get_real_route(origin_coords[0], origin_coords[1], target_coords[0], target_coords[1], mode=osrm_mode)
    if not route_coords:
        route_coords = [origin_coords, target_coords]

    # Gambar Garis Rute Menyala
    folium.PolyLine(
        route_coords, 
        color=color, 
        weight=6, 
        opacity=0.9,
        dash_array='8, 8',
        tooltip=f"Jalur Transmisi ({transport_mode})"
    ).add_to(m)

    st_folium(m, width=900, height=550, returned_objects=[])

st.markdown("---")
st.caption("Aisyah Azzahrah_G1A024033 // DEPT: Informatics Engineering UNIB // V.2.2 (Final)")