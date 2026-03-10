import os
import json
import sys
import asyncio
import edge_tts

async def buat_suara():
    print("Membaca naskah dari state.json...")
    try:
        with open("state.json", "r") as f:
            data = json.load(f)
        naskah = data["youtube"]["naskah_suara"]
    except Exception as e:
        print(f"Gagal membaca naskah: {e}")
        sys.exit(1)

    # Suara Pria Berwibawa (Brian)
    VOICE = "en-US-BrianNeural"
    OUTPUT_FILE = "voice.mp3"

    print(f"Menyintesis suara narasi...")
    try:
        communicate = edge_tts.Communicate(naskah, VOICE)
        await communicate.save(OUTPUT_FILE)
        print(f"SUKSES: {OUTPUT_FILE} berhasil dibuat!")
    except Exception as e:
        print(f"Gagal membuat suara: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(buat_suara())
