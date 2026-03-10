import requests
import os
import sys
from datetime import datetime

def tes_pabrik():
    # Kita pakai penyedia gambar dummy yang servernya sangat stabil untuk ngetes
    url = "https://picsum.photos/1080/1920"
    print("Mengambil gambar tes untuk memastikan GitHub bisa menyimpan file...")
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            os.makedirs("hasil_konten", exist_ok=True)
            # Namanya kita ubah jadi TEST_Image
            nama_file = f"hasil_konten/TEST_Image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            with open(nama_file, 'wb') as f:
                f.write(response.content)
            print(f"PIPA PENYIMPANAN SUKSES! Gambar berhasil disimpan di: {nama_file}")
            sys.exit(0) # Sukses (Hijau)
        else:
            print(f"Gagal mengambil gambar tes. Error: {response.status_code}")
            sys.exit(1) # Gagal (Merah)
            
    except Exception as e:
        print(f"Error jaringan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    tes_pabrik()
    
