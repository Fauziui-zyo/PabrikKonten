import os
import json
import asyncio
import requests
import subprocess
from duckduckgo_search import DDGS

def ghost_researcher():
    """Otak Konten: Riset Mitos Medis Makassar via DDG AI"""
    print("🧠 Ghost Scripting: Meriset mitos medis...")
    prompt = (
        "Kamu adalah edukator medis profesional Makassar. "
        "Buat 1 konten Mitos vs Fakta kesehatan lokal (contoh: Sanro/Kopi/Kerokan). "
        "Format JSON: {\"judul\": \"...\", \"hook\": \"...\", \"isi\": \"...\", \"prompt_visual\": \"...\"}"
    )
    with DDGS() as ddgs:
        response = ddgs.chat(prompt, model='gpt-4o-mini')
        clean_json = response.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)

def ghost_visualizer(prompt):
    """Visual AI: Download citra instan via Pollinations"""
    print(f"🎨 Visualizing: {prompt[:30]}...")
    encoded = requests.utils.quote(f"medical cinematic style, {prompt}")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&seed=42&nologo=true"
    r = requests.get(url)
    with open("input_bg.jpg", "wb") as f:
        f.write(r.content)

async def ghost_narrator(text):
    """Suara: Sintesis Neural via Edge-TTS"""
    print("🎙️ Narrating: Menghasilkan suara neural...")
    import edge_tts
    # Menggunakan GadisNeural untuk nada edukatif yang ramah
    communicate = edge_tts.Communicate(text, "id-ID-GadisNeural", rate="+5%")
    await communicate.save("audio.mp3")

if __name__ == "__main__":
    data = ghost_researcher()
    ghost_visualizer(data['prompt_visual'])
    asyncio.run(ghost_narrator(f"{data['hook']}. {data['isi']}"))
    with open("meta.json", "w") as f:
        json.dump(data, f)
    print("✅ Semua aset siap rakit.")
