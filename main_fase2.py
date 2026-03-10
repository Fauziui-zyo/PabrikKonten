import os
import json
import requests
import sys
import time

def buat_gambar_dasar():
    print("Membaca isi otak (state.json)...")
    try:
        with open("state.json", "r") as f:
            data = json.load(f)
        prompt_visual = data["adobestock"]["prompt_gambar"]
        print(f"Prompt yang akan dilukis: {prompt_visual}")
    except Exception as e:
        print(f"Gagal membaca state.json: {e}")
        sys.exit(1)

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN tidak ditemukan di GitHub Secrets!")
        sys.exit(1)

    # URL BARU SESUAI INSTRUKSI PEMBARUAN HUGGING FACE
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt_visual}

    print("Meminta Hugging Face melukis gambar...")
    
    # Sistem Anti-Gagal: Bot akan mencoba 3 kali jika server menolak
    for percobaan in range(3):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                with open("base_image.jpg", "wb") as f:
                    f.write(response.content)
                print("SUKSES: base_image.jpg berhasil dicetak!")
                sys.exit(0)
            else:
                print(f"Percobaan {percobaan + 1} gagal: {response.status_code} - {response.text}")
                if percobaan < 2:
                    print("Menunggu 5 detik sebelum mencoba lagi...")
                    time.sleep(5)
                    
        except Exception as e:
            print(f"Error Koneksi: {e}")
            if percobaan < 2:
                print("Menunggu 5 detik sebelum mencoba lagi...")
                time.sleep(5)

    print("Gagal melukis setelah 3 percobaan. Silakan cek status server Hugging Face.")
    sys.exit(1)

if __name__ == "__main__":
    buat_gambar_dasar()
