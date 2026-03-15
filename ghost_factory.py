import os
import json
import asyncio
import requests
import re
import time
import traceback
from urllib.parse import quote
from PIL import Image
import io

# --- 🧠 LOGIKA RISET (TEXT AI) ---
def clean_json_response(text):
    match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
    if match:
        try:
            cleaned = match.group(0).strip()
            json.loads(cleaned)
            return cleaned
        except: return None
    return None

def ghost_researcher():
    print("🧠 Ghost Scripting: Meriset mitos medis...")
    url = "https://text.pollinations.ai/"
    prompt = ("Kamu edukator medis. Buat 1 konten Mitos vs Fakta kesehatan Makassar/Indonesia (max 30 kata). "
              "WAJIB JSON: {\"judul\": \"...\", \"hook\": \"...\", \"isi\": \"...\", \"prompt_visual\": \"...\"}")
    payload = {"messages": [{"role": "system", "content": "JSON Only"}, {"role": "user", "content": prompt}]}
    
    for _ in range(3):
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                data = clean_json_response(r.text)
                if data: return json.loads(data)
        except: continue
    raise Exception("Gagal riset naskah.")

# --- 🎨 LOGIKA VISUAL (ROBUST + PLACEHOLDER) ---
def ghost_visualizer(prompt):
    print(f"🎨 Visualizing: {prompt[:50]}...")
    safe_prompt = prompt.replace('"', '').replace("'", "")
    encoded = quote(f"cinematic medical style, 4k, {safe_prompt}")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Mencoba download gambar utama (5x percobaan)
    for attempt in range(5):
        try:
            print(f"🔄 Mencoba unduh gambar (Percobaan #{attempt + 1})...")
            r = requests.get(url, timeout=120, headers=headers)
            if r.status_code == 200 and r.headers.get('content-type', '').startswith('image'):
                with open("input_bg.jpg", "wb") as f:
                    f.write(r.content)
                # Verifikasi integritas gambar
                with Image.open("input_bg.jpg") as img:
                    img.verify()
                print("✅ Gambar utama berhasil diunduh dan valid.")
                return
        except Exception as e:
            print(f"⚠️ Gagal: {e}")
            time.sleep(5)

    # --- JALUR DARURAT (PLACEHOLDER) ---
    print("⚠️ Semua percobaan gagal. Menggunakan gambar placeholder agar sistem tidak merah...")
    placeholder_url = "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=1080&h=1920&fit=crop"
    r = requests.get(placeholder_url, timeout=60)
    with open("input_bg.jpg", "wb") as f:
        f.write(r.content)
    print("✅ Gambar placeholder (medis umum) siap digunakan.")

# --- 🎙️ LOGIKA SUARA ---
async def ghost_narrator(text):
    print("🎙️ Narrating...")
    import edge_tts
    communicate = edge_tts.Communicate(text, "id-ID-GadisNeural", rate="+5%")
    await communicate.save("audio.mp3")

# --- 🚀 EKSEKUSI ---
if __name__ == "__main__":
    try:
        data = ghost_researcher()
        print(f"✅ Topik: {data['judul']}")
        ghost_visualizer(data['prompt_visual'])
        asyncio.run(ghost_narrator(f"{data['hook']}. {data['isi']}"))
        print("🎉 Aset berhasil dirakit!")
    except Exception as e:
        print(f"❌ Error Fatal: {e}")
        traceback.print_exc()
        exit(1)
