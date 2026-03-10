import os
import json
import sys
import google.generativeai as genai

def panggil_gemini_otak():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY tidak ditemukan di GitHub Secrets!")
        sys.exit(1)

    # Mengaktifkan SDK Resmi
    genai.configure(api_key=api_key)

    print("Mencari model AI yang aktif dan tersedia...")
    model_pilihan = None
    try:
        # Bot otomatis mencari model yang mendukung 'generateContent'
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_pilihan = m.name
                break
    except Exception as e:
        print(f"Gagal menghubungi server Google: {e}")
        sys.exit(1)

    if not model_pilihan:
        print("ERROR: Tidak ada model Gemini yang tersedia untuk API Key ini.")
        sys.exit(1)

    print(f"Berhasil menemukan model aktif: {model_pilihan}")
    model = genai.GenerativeModel(model_pilihan)
    
    instruksi = """
    Bertindaklah sebagai Creative Director & Ahli SEO. Buatlah 1 konsep video/gambar dengan tema 'Microscopic Medical Science' (seperti sel, DNA, virus neon).
    Anda WAJIB merespons HANYA dengan format JSON yang valid, tanpa teks awalan atau akhiran (tanpa ```json). Formatnya harus persis seperti ini:
    {
      "youtube": {
        "judul": "Judul Shorts max 50 karakter",
        "deskripsi": "Deskripsi pendek dengan 3 hashtag",
        "naskah_suara": "Naskah narasi 15 detik dengan hook di awal. Bahasa Inggris."
      },
      "adobestock": {
        "judul": "Judul deskriptif 5-8 kata bahasa Inggris, TANPA nama merk/tokoh",
        "kata_kunci": "keyword1, keyword2, keyword3, ... (Tepat 30 kata kunci dipisah koma)",
        "prompt_gambar": "Prompt bahasa Inggris sangat detail untuk AI Image Generator. Fokus ke 3D render, mikroskopik, neon, hyperrealistic."
      }
    }
    """

    print("Meminta Gemini merumuskan konsep & metadata...")
    try:
        response = model.generate_content(instruksi)
        # Membersihkan teks agar murni JSON
        teks_json = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        
        data_terstruktur = json.loads(teks_json)
        
        with open("state.json", "w") as f:
            json.dump(data_terstruktur, f, indent=4)
            
        print("SUKSES: Otak telah merumuskan state.json!")
        print(f"Bocoran Konsep: {data_terstruktur['adobestock']['judul']}")
        sys.exit(0)

    except Exception as e:
        print(f"Error saat merumuskan atau Parsing JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    panggil_gemini_otak()
