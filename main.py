import requests
import os
import sys
from datetime import datetime

def buat_gambar_ai():
    prompt = "high_quality_medical_abstract_art_dna_blue_theme_4k"
    # Kita tambahkan parameter acak (seed) agar gambarnya selalu baru
    seed = datetime.now().strftime('%S%M')
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1920&nologo=true&seed={seed}"
    
    print(f"Mengambil gambar dari: {url}")
    
    # Tambahkan header agar kita tidak dikira robot spam oleh Pollinations
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        os.makedirs("hasil_konten", exist_ok=True)
        nama_file = f"hasil_konten/AI_Image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        with open(nama_file, 'wb') as f:
            f.write(response.content)
        print(f"Berhasil! Gambar disimpan di: {nama_file}")
    else:
        print(f"Error {response.status_code}: Gagal mengambil gambar dari server AI.")
        # Ini yang bikin GitHub jadi MERAH kalau beneran gagal
        sys.exit(1) 

if __name__ == "__main__":
    buat_gambar_ai()
