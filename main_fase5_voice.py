import os, json, sys, asyncio, edge_tts

async def buat_suara_dan_vtt():
    print("Membaca naskah dan membuat subtitle...")
    try:
        with open("state.json", "r") as f: 
            data = json.load(f)
        naskah = data["youtube"]["naskah_suara"]
    except Exception as e:
        print(f"Gagal baca state.json: {e}")
        sys.exit(1)

    VOICE = "en-US-BrianNeural"
    # Menginisialisasi pembuat suara dan pembuat subtitle
    communicate = edge_tts.Communicate(naskah, VOICE)
    submaker = edge_tts.SubMaker()
    
    print("Menyintesis suara dan menyelaraskan teks...")
    with open("voice.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Mencatat waktu setiap kata untuk subtitle
                submaker.feed(chunk)

    # Perbaikan: Menggunakan 'generate_subs()' bukan 'get_vtt'
    with open("subtitles.vtt", "w", encoding="utf-8") as f:
        f.write(submaker.generate_subs())
    
    print("SUKSES: Voice.mp3 dan Subtitles.vtt berhasil dibuat!")

if __name__ == "__main__":
    asyncio.run(buat_suara_dan_vtt())
