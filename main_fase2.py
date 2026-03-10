import os
import json
import requests
import sys

def buat_gambar_dasar():
    print("Membaca isi otak (state.json)...")
    try:
        with open("state.json", "r") as f:
            data = json.load(f)
        # Mengambil prompt gambar yang sudah dibuat Gemini di Fase 1
        prompt_visual = data["adobestock"]["prompt_gambar"]
        print(f"Prompt yang akan dilukis: {prompt_visual}")
    except Exception as e:
        print(f"Gagal membaca state.json: {e}")
        sys.exit(1)

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN tidak ditemukan di GitHub Secrets!")
        sys.exit(1)

    # Memanggil model Stable Diffusion XL (Gratis & Berkualitas Tinggi)
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt_visual}

    print("Meminta Hugging Face melukis gambar (Bisa memakan waktu 1-2 menit)...")
    try:
        # Timeout diset 120 detik karena render gambar 4K butuh waktu
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            with open("base_image.jpg", "wb") as f:
                f.write(response.content)
            print("SUKSES: base_image.jpg berhasil dicetak!")
            sys.exit(0)
        else:
            print(f"Gagal melukis dari Hugging Face: {response.status_code} - {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error Koneksi ke Hugging Face: {e}")
        sys.exit(1)

if __name__ == "__main__":
    buat_gambar_dasar()
