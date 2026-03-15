import requests
import json
import re
import asyncio
import traceback

# --- LOGIKA DARI QWEN 3 ---
def clean_json_response(text):
    """Membersihkan naskah agar hanya mengambil blok JSON"""
    match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
    if match:
        try:
            cleaned = match.group(0).strip()
            json.loads(cleaned) # Validasi awal
            return cleaned
        except json.JSONDecodeError as e:
            raise ValueError(f"Gagal memvalidasi JSON: {e}")
    raise ValueError("Tidak menemukan blok JSON yang valid dalam respons.")

def ghost_researcher():
    """Riset naskah via Pollinations Text (No-Token)"""
    print("🧠 Ghost Scripting: Meriset mitos medis...")
    prompt = (
        "Kamu adalah edukator medis profesional. Buat 1 konten Mitos vs Fakta kesehatan singkat (max 30 kata). "
        "Format JSON murni: {\"judul\": \"...\", \"hook\": \"...\", \"isi\": \"...\", \"prompt_visual\": \"...\"}"
    )
    
    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [
            {"role": "system", "content": "Balas dalam format JSON sesuai instruksi."},
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                raw_text = response.text.strip()
                content = clean_json_response(raw_text)
                return json.loads(content)
            else:
                print(f"⚠️ Gagal riset (Status {response.status_code})")
        except Exception as e:
            print(f"🔁 Percobaan #{attempt+1} gagal: {str(e)}")
            
    raise Exception("Gagal mendapatkan naskah dari AI.")

# --- LOGIKA VISUAL & SUARA (GHOST WORKFLOW) ---
def ghost_visualizer(prompt):
    print(f"🎨 Visualizing: {prompt[:30]}...")
    encoded = requests.utils.quote(f"cinematic medical style, 4k, {prompt}")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true"
    
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=90)
            if r.status_code == 200:
                with open("input_bg.jpg", "wb") as f:
                    f.write(r.content)
                print("✅ Gambar berhasil diunduh.")
                return
        except Exception as e:
            print(f"🔁 Retrying visual... {e}")
    raise Exception("Gagal unduh gambar.")

async def ghost_narrator(text):
    print("🎙️ Narrating: Menghasilkan suara neural...")
    import edge_tts
    communicate = edge_tts.Communicate(text, "id-ID-GadisNeural", rate="+5%")
    await communicate.save("audio.mp3")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        # Step 1: Naskah
        data = ghost_researcher()
        print(f"✅ Topik: {data['judul']}")
        
        # Step 2: Visual
        ghost_visualizer(data['prompt_visual'])
        
        # Step 3: Audio
        full_text = f"{data['hook']}. {data['isi']}"
        asyncio.run(ghost_narrator(full_text))
        
        # Simpan Metadata
        with open("meta.json", "w") as f:
            json.dump(data, f)
            
        print("🎉 Semua aset siap rakit!")
    except Exception as e:
        print(f"❌ Error Terdeteksi: {e}")
        traceback.print_exc()
        exit(1)
