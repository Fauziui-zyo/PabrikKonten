import os
import json
import asyncio
import time
import requests
import feedparser
import modal
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

# ==========================================
# 0. SETUP REAKTOR SERVERLESS (MODAL)
# ==========================================
app = modal.App("cinema-factory-v-ultimate")

# Menyiapkan amunisi untuk mesin GPU virtual
mesin_produksi = modal.Image.debian_slim().pip_install(
    "google-genai", 
    "requests", 
    "feedparser", 
    "tenacity",
    "edge-tts"
).apt_install("ffmpeg")

# ==========================================
# 1. FASE PRA-PRODUKSI (TREND & SUTRADARA)
# ==========================================
def scan_tren_indonesia():
    print("Agent: Memindai tren internet hari ini...")
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=ID"
    try:
        feed = feedparser.parse(url)
        topik_viral = [entry.title for entry in feed.entries[:3]]
        print(f"Tren ditemukan: {', '.join(topik_viral)}")
        return topik_viral[0]
    except Exception as e:
        print(f"Gagal memindai tren, pakai topik default. Error: {e}")
        return "Misteri Sejarah Dunia"

def buat_naskah_dan_prompt(topik_hari_ini, api_key):
    print("Sutradara: Menulis naskah 90 detik berdasarkan tren...")
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Kamu adalah Sutradara Film Pendek YouTube Shorts yang jenius.
    Topik viral hari ini di Indonesia adalah: '{topik_hari_ini}'.
    
    Buat cerita 60-90 detik yang menggabungkan topik viral tersebut dengan sejarah kuno yang absurd.
    
    Tugas WAJIB format JSON:
    {{
        "youtube_title": "...",
        "youtube_desc": "...",
        "voice_script": "...",
        "character_reference_prompt": "...",
        "video_prompts": ["adegan 1", "adegan 2", "adegan 3", "adegan 4"]
    }}
    """
    
    response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
    teks = response.text.strip().removeprefix('```json').removesuffix('```').strip()
    return json.loads(teks)

# ==========================================
# 2. FASE VISUAL (NATIVE AI VIDEO)
# ==========================================
@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=5, max=30))
def panggil_ai_video(prompt_kamera, index, hf_token):
    print(f"Kamera: Merekam Scene {index}...")
    url = "https://api-inference.huggingface.co/models/THUDM/CogVideoX-5b"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt_kamera}
    
    response = requests.post(url, headers=headers, json=payload, timeout=200)
    
    if response.status_code == 200:
        nama_file = f"scene_{index}.mp4"
        with open(nama_file, "wb") as f:
            f.write(response.content)
        return nama_file
    else:
        raise Exception(f"Server Video AI Error: {response.text}")

def produksi_semua_video(prompts, hf_token):
    klip_tersimpan = []
    for i, prompt in enumerate(prompts):
        try:
            file_video = panggil_ai_video(prompt, i, hf_token)
            klip_tersimpan.append(file_video)
        except Exception as e:
            print(f"❌ Gagal di Scene {i}. Baju Zirah: Kloning scene sebelumnya.")
            if i > 0:
                os.system(f"cp scene_{i-1}.mp4 scene_{i}.mp4")
                klip_tersimpan.append(f"scene_{i}.mp4")
    return klip_tersimpan

# ==========================================
# 3. FASE AUDIO (VOKAL & BGM)
# ==========================================
def format_waktu(detik):
    jam = int(detik // 3600); menit = int((detik % 3600) // 60); sec = detik % 60
    return f"{jam:02}:{menit:02}:{sec:06.3f}"

async def sintesis_suara_dan_subtitle(naskah):
    print("Audio: Merekam Vokal & Subtitle...")
    import edge_tts
    communicate = edge_tts.Communicate(naskah, "en-US-ChristopherNeural")
    words = []
    
    with open("vokal_utama.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"start": chunk["offset"]/1e7, "dur": chunk["duration"]/1e7, "txt": chunk["text"]})

    vtt = "WEBVTT\n\n"
    for i, w in enumerate(words):
        vtt += f"{i+1}\n{format_waktu(w['start'])} --> {format_waktu(w['start']+w['dur'])}\n{w['txt']}\n\n"
    
    with open("subtitles.vtt", "w") as f:
        f.write(vtt)

def siapkan_bgm_gratis():
    print("Audio: Menyiapkan Background Music...")
    url_bgm = "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=epic.mp3"
    try:
        response = requests.get(url_bgm, timeout=30)
        with open("bgm_raw.mp3", "wb") as f:
            f.write(response.content)
    except:
        print("BGM gagal. Mode Bisu aktif.")
        os.system("ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 60 -q:a 9 -acodec libmp3lame bgm_raw.mp3")

# ==========================================
# 4. FUNGSI UTAMA (DIJALANKAN DI DALAM GPU)
# ==========================================
@app.function(image=mesin_produksi, timeout=3600, secrets=[modal.Secret.from_dict(os.environ)])
def eksekusi_pabrik():
    print("🔥 REAKTOR GPU MENYALA 🔥")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    # Menjalankan mesin secara berurutan
    topik_viral = scan_tren_indonesia()
    data_skenario = buat_naskah_dan_prompt(topik_viral, gemini_key)
    daftar_klip = produksi_semua_video(data_skenario['video_prompts'], hf_token)
    
    asyncio.run(sintesis_suara_dan_subtitle(data_skenario['voice_script']))
    siapkan_bgm_gratis()
    
    print("\n✅ Bahan baku (Video, Suara, BGM, Teks) siap dirakit!")
    # Nanti kode FFmpeg Editor dan YouTube Upload ditaruh di sini

@app.local_entrypoint()
def main():
    eksekusi_pabrik.remote()
