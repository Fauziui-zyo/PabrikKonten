import os
import json
import modal
import feedparser
from google import genai

# ==========================================
# 1. SETUP SERVERLESS GPU (MODAL)
# ==========================================
# Mengatur nama aplikasi di Modal
app = modal.App("cinema-factory-v-ultimate")

# Membuat kontainer Linux virtual yang berisi semua senjata kita
mesin_produksi = modal.Image.debian_slim().pip_install(
    "google-genai", 
    "requests", 
    "feedparser", 
    "tenacity",
    "elevenlabs" # Kita siapkan untuk Fase Audio nanti
).apt_install("ffmpeg")

# ==========================================
# 2. FITUR TREND SCANNER & SUTRADARA
# ==========================================
def scan_tren_indonesia():
    print("Agent: Memindai tren internet hari ini...")
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=ID"
    try:
        feed = feedparser.parse(url)
        # Ambil 3 topik paling viral hari ini
        topik_viral = [entry.title for entry in feed.entries[:3]]
        print(f"Tren ditemukan: {', '.join(topik_viral)}")
        return topik_viral[0] # Ambil peringkat 1
    except Exception as e:
        print(f"Gagal memindai tren, menggunakan topik default. Error: {e}")
        return "Misteri Sejarah Dunia"

def buat_naskah_dan_prompt(topik_hari_ini, api_key):
    print("Sutradara: Menulis naskah 90 detik berdasarkan tren...")
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Kamu adalah Sutradara Film Pendek YouTube Shorts yang jenius.
    Topik viral hari ini di Indonesia adalah: '{topik_hari_ini}'.
    
    Buat cerita 60-90 detik yang menggabungkan topik viral tersebut dengan sejarah kuno yang absurd (contoh: Tokoh sejarah melakukan hal modern terkait tren tersebut).
    
    Tugas:
    1. Buat 'youtube_title' yang clickbait.
    2. Buat 'youtube_desc' dengan hashtag.
    3. Buat 'voice_script' (naskah narator yang epik, minimal 60 kata).
    4. Buat 1 'character_reference_prompt' (Prompt deskripsi fisik karakter utama, sangat detail, cinematic lighting, 8k resolution).
    5. Buat 6 'video_prompts' berurutan (Bukan gambar statis! Instruksikan gerakan kamera, contoh: 'Cinematic slow pan, smoke rising...').
    
    WAJIB balas HANYA dengan JSON valid:
    {{
        "youtube_title": "...",
        "youtube_desc": "...",
        "voice_script": "...",
        "character_reference_prompt": "...",
        "video_prompts": ["adegan 1 bergerak", "adegan 2...", "adegan 3...", "adegan 4...", "adegan 5...", "adegan 6..."]
    }}
    """
    
    response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
    teks = response.text.strip().removeprefix('```json').removesuffix('```').strip()
    return json.loads(teks)

# ==========================================
# 3. FUNGSI UTAMA (DIJALANKAN DI DALAM GPU)
# ==========================================
# Tanda @app.function inilah yang menyuruh skrip berjalan di server GPU jarak jauh, bukan di GitHub!
@app.function(image=mesin_produksi, timeout=3600, secrets=[modal.Secret.from_dict(os.environ)])
def eksekusi_pabrik():
    print("🔥 MESIN REAKTOR GPU MENYALA 🔥")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    # Menjalankan Fase Pra-Produksi
    topik_viral = scan_tren_indonesia()
    data_skenario = buat_naskah_dan_prompt(topik_viral, gemini_key)
    
    print("\n[HASIL SUTRADARA]")
    print(f"Judul: {data_skenario['youtube_title']}")
    print(f"Jumlah Adegan Video: {len(data_skenario['video_prompts'])}")
    
    # (Di sinilah nanti kita akan memanggil Fase Visual, Audio, dan FFmpeg)
    print("\nMesin Standby untuk Fase Visual & Audio...")

# Entry point untuk dijalankan secara lokal/oleh GitHub
@app.local_entrypoint()
def main():
    eksekusi_pabrik.remote()
