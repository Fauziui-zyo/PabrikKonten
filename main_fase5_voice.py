import os, json, sys, asyncio, edge_tts

async def buat_suara_dan_vtt():
    print("Membaca naskah dan membuat subtitle...")
    with open("state.json", "r") as f: data = json.load(f)
    naskah = data["youtube"]["naskah_suara"]

    VOICE = "en-US-BrianNeural"
    # Kita simpan suara DAN subtitle
    communicate = edge_tts.Communicate(naskah, VOICE)
    submaker = edge_tts.SubMaker()
    
    with open("voice.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    with open("subtitles.vtt", "w", encoding="utf-8") as f:
        f.write(submaker.get_vtt())
    
    print("SUKSES: Voice.mp3 dan Subtitles.vtt berhasil dibuat!")

if __name__ == "__main__":
    asyncio.run(buat_suara_dan_vtt())
