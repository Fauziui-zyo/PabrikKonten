import os, json, sys, asyncio, edge_tts

# Fungsi pembantu untuk mengubah detik menjadi format waktu VTT (00:00:00.000)
def format_vtt_time(seconds):
    td = float(seconds)
    hours = int(td // 3600)
    minutes = int((td % 3600) // 60)
    secs = td % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"

async def buat_suara_dan_vtt():
    print("Agent Memulai: Membaca naskah...")
    try:
        with open("state.json", "r") as f: 
            data = json.load(f)
        naskah = data["youtube"]["naskah_suara"]
    except Exception as e:
        print(f"Gagal baca state.json: {e}")
        sys.exit(1)

    VOICE = "en-US-BrianNeural"
    communicate = edge_tts.Communicate(naskah, VOICE)
    
    # Tempat menyimpan data waktu setiap kata
    word_boundaries = []
    
    print("Agent Sedang Menyintesis Audio...")
    with open("voice.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Menyimpan posisi waktu (dalam detik) dan teksnya
                word_boundaries.append({
                    "start": chunk["offset"] / 10000000, # Konversi ke detik
                    "duration": chunk["duration"] / 10000000,
                    "text": chunk["text"]
                })

    print("Agent Sedang Menyusun Subtitle (Manual Formatting)...")
    # Membangun file VTT secara manual agar tidak bergantung pada fungsi library yang labil
    vtt_content = "WEBVTT\n\n"
    for i, word in enumerate(word_boundaries):
        start = format_vtt_time(word["start"])
        end = format_vtt_time(word["start"] + word["duration"])
        vtt_content += f"{i+1}\n{start} --> {end}\n{word['text']}\n\n"

    with open("subtitles.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_content)
    
    print("SUKSES: Pabrik Suara & Subtitle selesai bekerja tanpa error!")

if __name__ == "__main__":
    asyncio.run(buat_suara_dan_vtt())
