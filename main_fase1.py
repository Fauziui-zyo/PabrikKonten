import os
import json
import sys
import google.generativeai as genai
import random

def panggil_gemini_otak():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY tidak ditemukan!")
        sys.exit(1)

    genai.configure(api_key=api_key)

    # Bot mendeteksi model aktif
    model_pilihan = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            model_pilihan = m.name
            break

    model = genai.GenerativeModel(model_pilihan)
    
    # Kumpulan Tema Paling Laris (Best Seller)
    tema_laris = [
        "Abstract Cyber Security with glowing circuits and wide dark copy space on the right",
        "Minimalist modern office interior with soft sunlight and empty white wall for copy space",
        "Geometric 3D background with soft pastel colors and professional minimalist look",
        "Clean medical technology background with DNA strands in the corner and massive empty blue space",
        "Digital banking concept with abstract data visualization and clean layout for text"
    ]
    tema_saat_ini = random.choice(tema_laris)

    instruksi = f"""
    Bertindaklah sebagai Senior Art Director di Adobe Stock. 
    TEMA HARI INI: {tema_saat_ini}.
    Buatlah konsep gambar yang memfokuskan pada 'Copy Space' (area kosong yang luas) agar desainer bisa menaruh teks.
    
    Anda WAJIB merespons HANYA dengan format JSON valid:
    {{
      "youtube": {{
        "judul": "Judul Shorts edukatif & menarik",
        "deskripsi": "Deskripsi singkat + 3 hashtag populer",
        "naskah_suara": "Naskah narasi 15 detik yang membahas fakta menarik tentang teknologi/bisnis sesuai tema."
      }},
      "adobestock": {{
        "judul": "Judul komersial profesional tanpa kata subjektif (5-10 kata)",
        "kata_kunci": "minimalist, background, copy space, professional, modern, (tambah 25 kata kunci relevan lainnya)",
        "prompt_gambar": "High-end commercial photography style, {tema_saat_ini}, cinematic lighting, shot on 8k, sharp focus, professional color grading, minimalist composition."
      }}
    }}
    """

    print(f"Menggunakan tema: {tema_saat_ini}")
    try:
        response = model.generate_content(instruksi)
        teks_json = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        data_terstruktur = json.loads(teks_json)
        
        with open("state.json", "w") as f:
            json.dump(data_terstruktur, f, indent=4)
            
        print("SUKSES: Konsep High-Profit berhasil dirumuskan!")
        print(f"Target Hari Ini: {data_terstruktur['adobestock']['judul']}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    panggil_gemini_otak()
