import os, json, sys
from google import genai

def run():
    print("Agent: Merancang skenario 3 adegan...")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = """
    Buat konsep video Shorts 15 detik tentang 'Future Tech/Health'.
    Berikan 3 prompt gambar berurutan. Respon hanya JSON:
    {
      "youtube": {"judul": "...", "deskripsi": "...", "naskah_suara": "..."},
      "adobestock": {"judul": "...", "kata_kunci": "...", "prompts": ["p1", "p2", "p3"]}
    }
    """
    try:
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        with open("state.json", "w") as f: f.write(text)
        print("Fase 1 Sukses.")
    except Exception as e:
        print(f"Fase 1 Gagal: {e}"); sys.exit(1)

if __name__ == "__main__": run()
