import os
import subprocess
import sys

def rakit_video_otomatis():
    print("Memulai proses perakitan video (Auto-Motion)...")
    gambar = "base_image.jpg"
    suara = "voice.mp3"
    output = "final_shorts.mp4"

    # Pastikan bahan baku ada
    if not os.path.exists(gambar):
        print("ERROR: base_image.jpg tidak ditemukan!")
        sys.exit(1)
    if not os.path.exists(suara):
        print("ERROR: voice.mp3 tidak ditemukan!")
        sys.exit(1)

    # Perintah FFmpeg untuk efek Zoom-In perlahan agar video terlihat dinamis
    # Durasi diset otomatis mengikuti panjang suara
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", gambar,
        "-i", suara,
        "-vf", "zoompan=z='min(zoom+0.0015,1.5)':d=700:s=1080x1920,setsar=1",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", output
    ]

    try:
        subprocess.run(cmd, check=True)
        print("SUKSES: final_shorts.mp4 telah dirakit otomatis!")
    except Exception as e:
        print(f"Gagal merakit video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    rakit_video_otomatis()
