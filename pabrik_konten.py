import os
import json
import asyncio
import requests
import feedparser
import modal
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

# ==========================================
# 0. SETUP REAKTOR SERVERLESS (MODAL)
# ==========================================
app = modal.App("cinema-factory-v-ultimate")

# Menambahkan library YouTube API ke dalam reaktor
mesin_produksi = modal.Image.debian_slim().pip_install(
    "google-genai", 
    "requests", 
    "feedparser", 
    "tenacity",
    "edge-tts",
    "google-api-python-client",
    "google-auth-oauthlib",
    "google-auth-httplib2"
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
        return topik_viral[0]
    except Exception:
        return "Misteri Sejarah Dunia"

def buat_naskah_dan_prompt(topik_hari_ini, api_key):
    print("Sutradara: Menulis naskah berdasarkan tren...")
    client = genai.Client(api_key=api_key)
    prompt = f"""
    Kamu adalah Sutradara Video Shorts. Topik viral hari ini: '{topik_hari_ini}'.
    Buat cerita 60-90 detik. WAJIB format JSON murni HANYA seperti ini:
    {{
        "youtube_title": "Judul Clickbait",
        "youtube_desc": "Deskripsi dan hashtag",
        "voice_script": "Naskah narator yang epik panjang",
        "video_prompts": ["Prompt scene 1 rinci", "Prompt scene 2", "Prompt scene 3", "Prompt scene 4", "Prompt scene 5"]
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
    response = requests.post(url, headers=headers, json={"inputs": prompt_kamera}, timeout=200)
    
    if response.status_code == 200:
        nama_file = f"scene_{index}.mp4"
        with open(nama_file, "wb") as f: f.write(response.content)
        return nama_file
    raise Exception(f"Server Video AI Error")

def produksi_semua_video(prompts, hf_token):
    klip_tersimpan = []
    for i, prompt in enumerate(prompts):
        try:
            file_video = panggil_ai_video(prompt, i, hf_token)
            klip_tersimpan.append(file_video)
        except Exception as e:
            print(f"Baju Zirah: Kloning scene sebelumnya untuk scene {i}.")
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
            if chunk["type"] == "audio": f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"start": chunk["offset"]/1e7, "dur": chunk["duration"]/1e7, "txt": chunk["text"]})

    vtt = "WEBVTT\n\n"
    for i, w in enumerate(words):
        vtt += f"{i+1}\n{format_waktu(w['start'])} --> {format_waktu(w['start']+w['dur'])}\n{w['txt']}\n\n"
    with open("subtitles.vtt", "w") as f: f.write(vtt)

def siapkan_bgm():
    print("Audio: Menyiapkan Background Music...")
    try:
        url_bgm = "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=epic.mp3"
        response = requests.get(url_bgm, timeout=30)
        with open("bgm_raw.mp3", "wb") as f: f.write(response.content)
    except:
        os.system("ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 60 -q:a 9 -acodec libmp3lame bgm_raw.mp3")

# ==========================================
# 4. FASE EDITOR (GPU FFMPEG)
# ==========================================
def rakit_video_final(klip_tersimpan):
    print("Editor: Menyatukan mahakarya (Render Berjenjang)...")
    
    # Langkah 1: Sambung kasar semua video agar RAM tidak meledak
    with open("list_video.txt", "w") as f:
        for klip in klip_tersimpan:
            f.write(f"file '{klip}'\n")
    os.system("ffmpeg -y -f concat -safe 0 -i list_video.txt -c copy mentahan_panjang.mp4")

    # Langkah 2: Campur Audio (Vokal 100%, BGM 10%)
    cmd_audio = "ffmpeg -y -i vokal_utama.mp3 -i bgm_raw.mp3 -filter_complex \"[0:a]volume=1.0[v];[1:a]volume=0.1[b];[v][b]amix=inputs=2:duration=first\" -c:a aac mixed_audio.m4a"
    os.system(cmd_audio)

    # Langkah 3: Final Coating (Warna, Grain, Subtitle Profesional)
    # Alignment=2 artinya di tengah bawah (aman dari tombol Like YouTube)
    sub_style = "force_style='Alignment=2,MarginV=60,FontSize=26,FontName=Arial,Bold=1,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=1'"
    
    cmd_final = (
        f"ffmpeg -y -i mentahan_panjang.mp4 -i mixed_audio.m4a "
        f"-filter_complex \"[0:v]noise=alls=8:allf=t+u,eq=contrast=1.1:saturation=1.2[v_coated];[v_coated]subtitles=subtitles.vtt:{sub_style}\" "
        f"-c:v libx264 -preset fast -c:a copy -shortest final_shorts.mp4"
    )
    os.system(cmd_final)
    print("✅ Video Final Siap!")

# ==========================================
# 5. FASE KURIR & PEMBERSIHAN (YOUTUBE UPLOAD)
# ==========================================
def upload_ke_youtube(judul, deskripsi):
    print("Kurir: Mengunggah ke YouTube...")
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    
    creds = Credentials.from_authorized_user_info({
        "client_id": os.environ.get("YT_CLIENT_ID"),
        "client_secret": os.environ.get("YT_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YT_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    youtube = build("youtube", "v3", credentials=creds)
    
    body = {
        "snippet": {"title": judul, "description": deskripsi, "categoryId": "28"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload("final_shorts.mp4", chunksize=1024*1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status: print(f"Proses unggah: {int(status.progress() * 100)}%")
    print(f"✅ Video LIVE di YouTube: https://youtu.be/{response['id']}")

def bersihkan_sampah_pabrik():
    print("Pembersih: Menghapus file mentah untuk mencegah kebocoran penyimpanan...")
    os.system("rm -f scene_*.mp4 vokal_utama.mp3 bgm_raw.mp3 mixed_audio.m4a subtitles.vtt list_video.txt mentahan_panjang.mp4 final_shorts.mp4")
    print("✅ Gudang bersih. Pabrik dimatikan.")

# ==========================================
# FUNGSI UTAMA (DI DALAM GPU)
# ==========================================
@app.function(image=mesin_produksi, timeout=3600, secrets=[modal.Secret.from_dict(dict(os.environ))])
def eksekusi_pabrik():
    print("🔥 REAKTOR GPU MENYALA 🔥")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    topik_viral = scan_tren_indonesia()
    data_skenario = buat_naskah_dan_prompt(topik_viral, gemini_key)
    
    daftar_klip = produksi_semua_video(data_skenario['video_prompts'], hf_token)
    asyncio.run(sintesis_suara_dan_subtitle(data_skenario['voice_script']))
    siapkan_bgm()
    
    rakit_video_final(daftar_klip)
    
    try:
        upload_ke_youtube(data_skenario['youtube_title'], data_skenario['youtube_desc'])
    except Exception as e:
        print(f"❌ Upload Gagal (Mungkin Token Expired): {e}")
        print("⚠️ Video 'final_shorts.mp4' tidak dihapus agar bisa diunduh manual.")
        return # Berhenti di sini agar tidak memanggil fungsi pembersih
    
    bersihkan_sampah_pabrik()

@app.local_entrypoint()
def main():
    eksekusi_pabrik.remote()
