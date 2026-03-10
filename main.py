import requests
import os
import sys
import urllib.parse
from datetime import datetime
import time

def buat_gambar_ai():
    # Prompt menggunakan spasi biasa, nanti di-encode otomatis oleh sistem
    prompt_teks = "high quality medical abstract art dna blue theme 4k"
    prompt_aman = urllib.parse.quote(prompt_teks)
    
    # URL kita buat sangat sederhana agar server mereka tidak bingung
    url = f"https://image.pollinations.ai/prompt/{prompt_aman}"
    
    print(f"Mencoba mengambil gambar dari API Pollinations...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # Bot akan mencoba maksimal 3 kali kalau server AI sedang sibuk
    for percobaan in range(3):
        print(f"Mulai percobaan ke-{percobaan + 1}...")
        try:
            # timeout=30 agar bot tidak nunggu selamanya kalau server sana hang
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                os.makedirs("hasil_konten", exist_ok=True)
                nama_file = f"hasil_konten/AI_Image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                
                with open(nama_file, 'wb') as f:
                    f.write(response.content)
                print(f"Mantap Bang! Gambar berhasil disimpan di: {nama_file}")
                sys.exit(0) # Lapor sukses (Hijau) ke GitHub
            else:
                print(f"Server AI sibuk (Error {response.status_code}).")
        
        except Exception as e:
            print(f"Terjadi gangguan sinyal ke server: {e}")
        
        # Kalau gagal, istirahat 5 detik sebelum gedor pintu servernya lagi
        print("Istirahat 5 detik sebelum coba lagi...\n")
        time.sleep(5)
        
    print("Sudah mencoba 3 kali tapi server AI tetap menolak. Menyerah untuk sesi ini.")
    sys.exit(1) # Lapor gagal (Merah) ke GitHub

if __name__ == "__main__":
    buat_gambar_ai()
