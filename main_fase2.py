import os, json, requests, sys, time

def buat_gambar_berantai():
    print("Agent: Melukis 3 adegan berurutan...")
    with open("state.json", "r") as f: 
        data = json.load(f)
    
    prompts = data["adobestock"]["prompts"]
    hf_token = os.environ.get("HF_TOKEN")
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}

    for i, prompt in enumerate(prompts):
        print(f"Melukis adegan {i}...")
        for coba in range(3): # Retry 3 kali jika gagal
            res = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=120)
            if res.status_code == 200:
                with open(f"img_{i}.jpg", "wb") as f:
                    f.write(res.content)
                print(f"Adegan {i} SELESAI.")
                break
            time.sleep(5)
    
    # Backup untuk Adobe Stock
    os.system("cp img_0.jpg base_image.jpg")
    print("Agent: Semua gambar siap!")

if __name__ == "__main__":
    buat_gambar_berantai()
