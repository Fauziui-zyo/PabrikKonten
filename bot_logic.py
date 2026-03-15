import os
import google.generativeai as genai
import requests
import json
import time
from typing import Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mengambil API Key dari environment variables (GitHub Secrets)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Validasi environment variables
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY tidak ditemukan di environment variables")
if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN tidak ditemukan di environment variables")

# Inisialisasi AI Gemini dengan retry mechanism
def initialize_gemini():
    """Inisialisasi Gemini dengan penanganan error"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Test connection
            test_response = model.generate_content("Hello, are you working?")
            logger.info("✅ Gemini API connected successfully")
            return model
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise Exception("❌ Failed to initialize Gemini API after multiple attempts")

try:
    model = initialize_gemini()
except Exception as e:
    logger.error(f"Fatal error initializing Gemini: {e}")
    exit(1)

def generate_health_content(max_retries: int = 3) -> Dict:
    """Menggunakan Gemini untuk mencari ide kesehatan dan menyusun skrip Reels dengan retry mechanism"""
    prompt = """
    Kamu adalah seorang edukator kesehatan profesional. 
    Buatlah satu konten edukasi kesehatan singkat untuk Facebook Reels.
    Topik: Mitos vs Fakta Medis yang sering salah di masyarakat.
    Format output harus JSON murni tanpa awalan/akhiran apapun:
    {
        "judul": "Judul yang menarik/clickbait",
        "hook": "Kalimat pembuka yang memancing rasa ingin tahu",
        "isi": "Penjelasan singkat dan padat (max 3 poin)",
        "cta": "Call to action (ajakan share/follow)",
        "image_prompt": "Prompt detail dalam bahasa Inggris untuk generate gambar medis estetik di Hugging Face"
    }
    Pastikan informasi akurat secara medis.
    """
    
    for attempt in range(max_retries):
        try:
            logger.info(f"📝 Menggenerate konten kesehatan (Attempt {attempt + 1})...")
            response = model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            # Clean and validate JSON
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            
            # Validate JSON structure
            content_data = json.loads(clean_json)
            required_fields = ["judul", "hook", "isi", "cta", "image_prompt"]
            
            if not all(field in content_data for field in required_fields):
                raise ValueError("Missing required fields in JSON response")
            
            logger.info(f"✅ Konten berhasil digenerate: {content_data['judul']}")
            return content_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error (Attempt {attempt + 1}): {e}")
            logger.error(f"Response received: {response.text if 'response' in locals() else 'No response'}")
            
        except Exception as e:
            logger.error(f"❌ Error generating content (Attempt {attempt + 1}): {e}")
            
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    raise Exception("❌ Failed to generate health content after maximum retries")

def generate_image_hf(image_prompt: str, max_retries: int = 3) -> Optional[str]:
    """Meminta model AI FLUX di Hugging Face untuk menggambar ilustrasi dengan retry mechanism"""
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": image_prompt,
        "parameters": {
            "num_inference_steps": 4,  # FLUX.1-schnell optimal dengan 4 steps
            "guidance_scale": 0  # Unconditional generation untuk speed
        }
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🎨 Menggenerate gambar (Attempt {attempt + 1}): {image_prompt[:50]}...")
            
            response = requests.post(
                API_URL, 
                headers=headers, 
                json=payload,
                timeout=30  # Timeout 30 detik
            )
            
            if response.status_code == 200:
                with open("thumbnail.png", "wb") as f:
                    f.write(response.content)
                logger.info("✅ Gambar berhasil disimpan sebagai thumbnail.png")
                return "thumbnail.png"
            else:
                error_msg = response.json().get('error', 'Unknown error')
                logger.error(f"❌ Hugging Face API error (Attempt {attempt + 1}): {error_msg}")
                
                # Handle model loading wait time
                if "currently loading" in error_msg:
                    estimated_time = response.json().get('estimated_time', 60)
                    logger.info(f"⏳ Model sedang loading, waiting {estimated_time} seconds...")
                    time.sleep(min(estimated_time, 60))  # Max wait 60 seconds
                    continue
                    
        except requests.exceptions.Timeout:
            logger.error(f"❌ Request timeout (Attempt {attempt + 1})")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error (Attempt {attempt + 1}): {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error generating image (Attempt {attempt + 1}): {e}")
            
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    logger.error("❌ Gagal generate gambar setelah maximum retries")
    return None

def save_content_data(content_data: Dict) -> bool:
    """Save content data with error handling"""
    try:
        with open("content_data.json", "w", encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        logger.info("💾 Content data saved successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save content data: {e}")
        return False

def main():
    """Main execution function with comprehensive error handling"""
    try:
        logger.info("🚀 Memulai Proses Otomasi Konten")
        
        # Generate content
        content = generate_health_content()
        logger.info(f"📋 Topik Hari Ini: {content['judul']}")
        
       # Generate image
        image_result = generate_image_hf(content['image_prompt'])
        if not image_result:
            logger.error("❌ Gambar gagal dibuat. Menghentikan proses agar Modal.com tidak error.")
            return False # <-- Langsung hentikan proses
        
        # Save content data
        if not save_content_data(content):
            raise Exception("Failed to save content data")
        
        logger.info("🎉 Logika Selesai. Naskah & Gambar telah siap!")
        return True
        
    except Exception as e:
        logger.error(f"💥 Fatal error in main execution: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
