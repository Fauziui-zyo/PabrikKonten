import os
import json
import asyncio
import requests
import re
import traceback
from duckduckgo_search import DDGS

def clean_json_response(text):
    """Membersihkan dan memvalidasi JSON dari AI agar tidak error"""
    match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
    if match:
        try:
            cleaned = match.group(0).strip()
            json.loads(cleaned) # Tes validasi
            return cleaned
        except json.JSONDecodeError:
            print("⚠️ JSON tidak valid, mencoba pembersihan manual...")
            return None
    return None

def ghost_researcher():
    """Riset Mitos Medis via DuckDuckGo AI (Tanpa Token)"""
    print("🧠 Ghost Scripting: Meriset mitos medis...")
    prompt = (
        "Kamu adalah edukator medis profesional. Buat 1 konten Mitos vs Fakta kesehatan singkat (max 30 kata). "
        "Format JSON murni: {\"judul\": \"...\", \"hook\": \"...\", \"isi\": \"...\", \"prompt_visual\": \"...\"}"
    )
    with DDGS() as ddgs:
        for attempt in range(3):
            try:
                response = ddgs.chat(prompt, model='gpt-4o-mini')
                content = clean_json_response(response)
                if content:
                    return json.loads(content)
            except Exception as e:
                print(f"⚠️ Gagal riset (Percobaan {attempt+1}): {e}")
    raise Exception("Gagal mendapatkan naskah dari AI.")

def ghost_visualizer(prompt):
    """Visual AI: Download citra instan via Pollinations (Tanpa Token)"""
    print(f"🎨 Visualizing: {prompt[:30]}...")
    encoded = requests.utils.quote(f"cinematic medical style, 4k, {prompt}")
    # URL Bersih tanpa kontaminasi Markdown
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true"
    
    for attempt in range(3):
        try:
            print(f"⏳ Mengunduh gambar (Percobaan {attempt+1})...")
            r = requests.get(url, timeout=90)
            if r.status_code == 200:
                with open("input_bg.jpg", "wb") as f:
                    f.write(r.content)
                print("✅ Gambar berhasil diunduh.")
                return
            else:
                print(f"⚠️ Status Code: {r.status_code}")
        except Exception as e:
            print(f"🔁 Gagal: {e}")
    raise Exception("Gagal mengunduh gambar setelah 3 kali percobaan.")

async def ghost_narrator(text):
    """Suara: Sintesis Neural via Edge-TTS (Tanpa Token)"""
    print("🎙️ Narrating: Menghasilkan suara neural...")
    import edge_tts
    communicate = edge_tts.Communicate(text, "id-ID-GadisNeural", rate="+5%")
    await communicate.save("audio.mp3")

if __name__ == "__main__":
    try:
        data = ghost_researcher()
        ghost_visualizer(data['prompt_visual'])
        
        full_text = f"{data['hook']}. {data['isi']}"
        asyncio.run(ghost_narrator(full_text))
        
        with open("meta.json", "w") as f:
            json.dump(data, f)
        print("✅ Semua aset siap rakit.")
    except Exception as e:
        print(f"❌ Error Terdeteksi: {e}")
        traceback.print_exc()
        exit(1)
