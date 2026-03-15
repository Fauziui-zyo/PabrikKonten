# src/render_video.py
import modal
import json
import subprocess
import os
import uuid
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Modal setup
app = modal.App("health-reels-renderer")

# Image dengan dependency yang dibutuhkan
image = modal.Image.debian_slim().apt_install("ffmpeg", "imagemagick") \
    .pip_install([
        "moviepy>=1.0.3",
        "Pillow>=9.0.0",
        "edge-tts>=6.1.9",
        "numpy>=1.21.0"
    ])

# --- FUNGSI BANTUAN (HELPER FUNCTIONS) DENGAN ERROR HANDLING ---

def generate_voiceover(text: str, output_path: str):
    import edge_tts
    import asyncio
    async def _generate():
        communicate = edge_tts.Communicate(
            text=text,
            voice="id-ID-GadisNeural",
            rate="+15%",
            pitch="+2Hz"
        )
        await communicate.save(output_path)
    asyncio.run(_generate())

def generate_fallback_tts(text: str, output_path: str):
    logger.warning("Using fallback TTS method")
    with open(output_path, 'w') as f:
        f.write("")  # Placeholder

def resize_image(input_path: str, output_path: str, width: int, height: int):
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
        output_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        logger.debug(f"Resize successful: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg resize failed: {e.stderr}")
        raise Exception(f"Failed to resize image: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg resize timed out")
        raise Exception("Image resize operation timed out")

def get_audio_duration(audio_path: str) -> float:
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logger.error(f"FFprobe failed: {e.stderr}")
        raise Exception(f"Failed to get audio duration: {e.stderr}")
    except ValueError as e:
        logger.error(f"Invalid duration value: {result.stdout}")
        raise Exception(f"Invalid audio duration format: {result.stdout}")

def video_from_image(image_path: str, output_path: str, duration: float):
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-c:v", "libx264", "-t", str(duration),
        "-pix_fmt", "yuv420p", "-shortest", output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        logger.debug("Video creation successful")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg video creation failed: {e.stderr}")
        raise Exception(f"Failed to create video: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg video creation timed out")
        raise Exception("Video creation operation timed out")

def combine_video_audio(video_path: str, voiceover_path: str, output_path: str):
    cmd = [
        "ffmpeg", "-y", "-i", video_path, "-i", voiceover_path,
        "-c:v", "copy", "-c:a", "aac", "-shortest", output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        logger.debug("Audio-video combination successful")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg combine failed: {e.stderr}")
        raise Exception(f"Failed to combine video and audio: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg combine timed out")
        raise Exception("Audio-video combination timed out")

def apply_anti_detection(input_video: str, output_video: str):
    noise_level = 12
    import random
    crf = random.randint(21, 25)
    speed_factor = 1 + random.uniform(-0.001, 0.001)
    
    cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", f"noise=alls={noise_level}:allf=t+u,setpts={1/speed_factor}*PTS",
        "-af", f"atempo={speed_factor}",
        "-c:v", "libx264", "-crf", str(crf), "-preset", "medium", "-c:a", "aac",
        "-metadata", "title=", "-metadata", "comment=", "-metadata", "artist=",
        "-metadata", "encoder=", "-metadata", "creation_time=",
        "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact",
        output_video
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
        logger.debug("Anti-detection applied successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg anti-detection failed: {e.stderr}")
        raise Exception(f"Failed to apply anti-detection: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg anti-detection timed out")
        raise Exception("Anti-detection operation timed out")

# --- FUNGSI UTAMA MODAL.COM ---

@app.function(image=image, timeout=600)
def render_health_reel(content_data_bytes: bytes, thumbnail_bytes: bytes) -> bytes:
    """
    Render video Reels kesehatan di Cloud dengan error handling yang robust.
    """
    logger.info("🚀 Memulai proses render di server Modal...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Tulis ulang bytes ke file lokal di Cloud Modal
            content_path = os.path.join(tmpdir, "content_data.json")
            thumbnail_path = os.path.join(tmpdir, "thumbnail.png")
            
            with open(content_path, "wb") as f:
                f.write(content_data_bytes)
            with open(thumbnail_path, "wb") as f:
                f.write(thumbnail_bytes)

            # Baca data konten JSON
            try:
                with open(content_path, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON in content data: {e}")
            except Exception as e:
                raise Exception(f"Failed to read content data: {e}")

            # Step 2: Generate voiceover
            logger.info("🎙️ Generating voiceover...")
            voiceover_path = os.path.join(tmpdir, "voiceover.mp3")
            try:
                generate_voiceover(content_data['isi'], voiceover_path)
                if not os.path.exists(voiceover_path) or os.path.getsize(voiceover_path) == 0:
                    raise Exception("Voiceover generation failed - empty file")
            except Exception as e:
                logger.error(f"Voiceover generation failed: {e}")
                # Fallback ke TTS sederhana jika edge-tts gagal
                generate_fallback_tts(content_data['isi'], voiceover_path)

            # Step 3: Siapkan visual
            logger.info("🖼️ Memproses visual...")
            output_video = os.path.join(tmpdir, f"temp_video_{uuid.uuid4().hex[:8]}.mp4")
            resized_thumbnail = os.path.join(tmpdir, "resized_thumb.jpg")
            resize_image(thumbnail_path, resized_thumbnail, width=1080, height=1920)
            
            # Buat video dari gambar
            try:
                duration = get_audio_duration(voiceover_path)
                if duration <= 0:
                    duration = 30  # Default duration jika gagal
                    logger.warning(f"Using default duration: {duration}s")
            except Exception as e:
                logger.error(f"Gagal mendapat durasi audio, menggunakan default 30 detik. Error: {e}")
                duration = 30
                
            video_from_image(resized_thumbnail, output_video, duration)
            
            # Step 4: Gabungkan visual dengan audio
            logger.info("🎬 Menggabungkan audio dan video...")
            final_video = os.path.join(tmpdir, "final_with_audio.mp4")
            combine_video_audio(output_video, voiceover_path, final_video)
            
            # Step 5: Terapkan anti-detection
            logger.info("🛡️ Menerapkan teknik anti-detection...")
            anti_detected_video = os.path.join(tmpdir, "anti_detected_final.mp4")
            apply_anti_detection(final_video, anti_detected_video)
            
            # Step 6: Baca file hasil sebagai bytes
            if not os.path.exists(anti_detected_video):
                raise Exception("Final video file was not created")
            
            logger.info("📦 Membungkus video ke dalam bytes...")
            with open(anti_detected_video, "rb") as video_file:
                video_bytes = video_file.read()
                
            if len(video_bytes) == 0:
                raise Exception("Generated video file is empty")
                
            logger.info(f"✅ Video rendering completed ({len(video_bytes)} bytes). Mengirim kembali ke GitHub Actions.")
            return video_bytes
            
    except Exception as e:
        logger.error(f"❌ Fatal error in render process: {e}")
        raise Exception(f"Render process failed: {str(e)}")


# --- ENTRYPOINT UNTUK GITHUB ACTIONS ---

@app.local_entrypoint()
def main():
    logger.info("Mencoba mengirim tugas render ke Cloud Modal...")
    
    if os.path.exists("content_data.json") and os.path.exists("thumbnail.png"):
        # 1. Baca file lokal sebagai bytes dari GitHub runner
        with open("content_data.json", "rb") as f: 
            content_bytes = f.read()
        with open("thumbnail.png", "rb") as f: 
            thumbnail_bytes = f.read()
            
        # 2. Panggil fungsi remote Modal dan kirim bytes
        hasil_video_bytes = render_health_reel.remote(content_bytes, thumbnail_bytes)
        
        # 3. Tulis balasan bytes dari server Modal menjadi file .mp4 lokal
        with open("reels_siap_upload.mp4", "wb") as f:
            f.write(hasil_video_bytes)
            
        logger.info("✅ SUKSES! Video berhasil dirender dan disimpan sebagai 'reels_siap_upload.mp4'")
    else:
        logger.error("❌ Error: File content_data.json atau thumbnail.png tidak ditemukan.")
        raise FileNotFoundError("Bahan baku video tidak tersedia.")
