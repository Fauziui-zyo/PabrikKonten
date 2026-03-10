import os
import json
import requests
import sys

def panggil_gemini_otak():
    # Mengambil kunci dari Brankas GitHub
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY tidak ditemukan di GitHub Secrets!")
        sys.exit(1)

    # PERUBAHAN DI SINI: Kita gunakan 'gemini-pro' yang merupakan model paling stabil
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    # Perintah (Prompt) ketat agar Gemini menjawab HANYA dengan format JSON
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

    payload = {
        "contents": [{"parts": [{"text": instruksi}]}],
        "generationConfig": {"temperature": 0.7}
    }

    print("Meminta Gemini merumuskan konsep & metadata...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            hasil = response.json()
            teks_json = hasil['candidates'][0]['content']['parts'][0]['text']
            
            # Membersihkan teks dari sisa-sisa markdown jika ada
            teks_json = teks_json.strip().removeprefix('```json').removesuffix('```').strip()
            
            # Validasi apakah format JSON benar
            data_terstruktur = json.loads(teks_json)
            
            # Menyimpan hasil ke file state.json
            with open("state.json", "w") as f:
                json.dump(data_terstruktur, f, indent=4)
                
            print("SUKSES: Otak telah merumuskan state.json!")
            print(f"Bocoran Konsep: {data_terstruktur['adobestock']['judul']}")
            sys.exit(0)
        else:
            print(f"Gagal memanggil Gemini: {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"Error Jaringan/Parsing JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    panggil_gemini_otak()
