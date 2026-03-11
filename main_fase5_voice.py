import os, json, asyncio, edge_tts, sys

async def run():
    print("Agent: Membuat suara & subtitle...")
    with open("state.json", "r") as f: data = json.load(f)
    naskah = data["youtube"]["naskah_suara"]
    
    communicate = edge_tts.Communicate(naskah, "en-US-BrianNeural")
    words = []
    with open("voice.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"s": chunk["offset"]/10**7, "d": chunk["duration"]/10**7, "t": chunk["text"]})

    vtt = "WEBVTT\n\n"
    for i, w in enumerate(words):
        start = f"00:00:{w['s']:06.3f}"; end = f"00:00:{w['s']+w['d']:06.3f}"
        vtt += f"{i+1}\n{start} --> {end}\n{w['t']}\n\n"
    
    with open("subtitles.vtt", "w") as f: f.write(vtt)
    print("Fase 5 Sukses.")

if __name__ == "__main__": asyncio.run(run())
