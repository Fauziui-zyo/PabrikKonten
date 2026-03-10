import json
import csv
import sys
import os

def buat_csv_adobe():
    print("Membaca state.json untuk merakit CSV Adobe Stock...")
    try:
        with open("state.json", "r", encoding='utf-8') as f:
            data = json.load(f)
            
        judul = data["adobestock"]["judul"]
        kata_kunci = data["adobestock"]["kata_kunci"]
        
    except Exception as e:
        print(f"Gagal membaca state.json: {e}")
        sys.exit(1)

    print("Merakit file metadata.csv...")
    try:
        # ATURAN ADOBE: Header CSV harus persis [Filename, Title, Keywords, Category]
        # Kategori 14 = Science (Bisa diganti nanti)
        with open("metadata.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Filename", "Title", "Keywords", "Category"])
            writer.writerow(["base_image.jpg", judul, kata_kunci, "14"])
            
        print("SUKSES: metadata.csv berhasil dirakit dan siap kirim!")
        sys.exit(0)
        
    except Exception as e:
        print(f"Gagal menulis CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    buat_csv_adobe()
