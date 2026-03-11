import os, json, requests, time, sys

def run():
    print("Agent: Melukis 3 adegan...")
    with open("state.json", "r") as f: data = json.load(f)
    prompts = data["adobestock"]["prompts"]
    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"}

    for i, p in enumerate(prompts):
        for _ in range(3):
            res = requests.post(url, headers=headers, json={"inputs": p})
            if res.status_code == 200:
                with open(f"img_{i}.jpg", "wb") as f: f.write(res.content)
                break
            time.sleep(5)
    
    os.system("cp img_0.jpg base_image.jpg")
    print("Fase 2 Sukses.")

if __name__ == "__main__": run()
