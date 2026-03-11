import os, json, sys, google.generativeai as genai

def panggil_gemini_otak():
    print("Agent: Merancang skenario 3 adegan...")
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt_instruksi = """
    Buat konsep video Shorts 15 detik. Tema: Teknologi Masa Depan/Medis.
    Berikan 3 prompt gambar yang berurutan untuk 3 adegan berbeda.
    Respon WAJIB dalam JSON:
    {
      "youtube": {"judul": "...", "deskripsi": "...", "naskah_suara": "..."},
      "adobestock": {
        "judul": "...",
        "kata_kunci": "...",
        "prompts": ["prompt adegan 1", "prompt adegan 2", "prompt adegan 3"]
      }
    }
    """
    try:
        response = model.generate_content(prompt_instruksi)
        teks = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        with open("state.json", "w") as f:
            f.write(teks)
        print("SUKSES: Skenario 3 adegan siap!")
    except Exception as e:
        print(f"Gagal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    panggil_gemini_otak()
