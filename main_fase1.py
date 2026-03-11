import os, json, sys
from google import genai

def panggil_gemini_otak():
    print("Agent: Memulai koneksi ke Google GenAI (Versi Terbaru)...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: API Key tidak ditemukan di Secrets!")
        sys.exit(1)

    # Inisialisasi Client Baru 2026
    client = genai.Client(api_key=api_key)

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
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt_instruksi
        )
        
        teks = response.text.strip()
        if teks.startswith("```json"):
            teks = teks.removeprefix('```json').removesuffix('```').strip()
        
        # Validasi JSON sebelum simpan
        json.loads(teks) 
        
        with open("state.json", "w") as f:
            f.write(teks)
        print("SUKSES: Skenario 3 adegan siap tanpa error!")
    except Exception as e:
        print(f"Agent Gagal pada Fase 1: {e}")
        sys.exit(1)

if __name__ == "__main__":
    panggil_gemini_otak()
