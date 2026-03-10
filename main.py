import requests
import os
from datetime import datetime

def buat_gambar_ai():
    # Contoh tema: Pemandangan Futuristik (Bisa diganti nanti lewat AI Gemini)
    prompt = "high_quality_medical_abstract_art_dna_blue_theme_4k"
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1920&nologo=true"
    
    print(f"Sedang membuat gambar dengan prompt: {prompt}...")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        # Folder untuk hasil
        os.makedirs("hasil_konten", exist_ok=True)
        
        # Nama file berdasarkan waktu agar tidak duplikat
        nama_file = f"hasil_konten/AI_Image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        with open(nama_file, 'wb') as f:
            f.write(response.content)
        print(f"Berhasil! Gambar disimpan di: {nama_file}")
    else:
        print("Gagal mengambil gambar dari server AI.")

if __name__ == "__main__":
    buat_gambar_ai()
