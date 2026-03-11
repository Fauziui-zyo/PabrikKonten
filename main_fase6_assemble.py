import os, subprocess, sys

def rakit_video_world_class():
    print("Memulai perakitan video multi-scene dengan subtitle viral...")
    
    # Pastikan semua bahan lengkap
    for i in range(3):
        if not os.path.exists(f"img_{i}.jpg"):
            print(f"ERROR: img_{i}.jpg tidak ditemukan!")
            sys.exit(1)
    if not os.path.exists("voice.mp3") or not os.path.exists("subtitles.vtt"):
        print("ERROR: Suara atau Subtitle belum siap!")
        sys.exit(1)

    # 1. Mengubah 3 gambar menjadi 3 klip video (5 detik per klip) dengan efek gerak
    for i in range(3):
        print(f"Memproses klip adegan {i+1}...")
        # Efek Zoom-In lambat agar terlihat sinematik
        cmd_clip = (
            f"ffmpeg -y -loop 1 -i img_{i}.jpg -vf "
            f"\"scale=8000:-1,zoompan=z='zoom+0.001':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1920\" "
            f"-c:v libx264 -t 5 -pix_fmt yuv420p clip_{i}.mp4"
        )
        subprocess.run(cmd_clip, shell=True, check=True)

    # 2. Menggabungkan 3 klip dengan transisi 'Fade' dan membakar Subtitle
    # Alur: Gabungkan v0 & v1 -> Gabungkan hasilnya dengan v2 -> Tambah Audio -> Tambah Subtitle
    print("Menyambung adegan dan memasang subtitle...")
    
    # Filter complex untuk transisi halus antar adegan
    filter_complex = (
        "[0:v][1:v]xfade=transition=fade:duration=1:offset=4[v01]; "
        "[v01][2:v]xfade=transition=fade:duration=1:offset=8[vfinal]"
    )
    
    # Perintah Akhir: Menggabungkan semuanya menjadi final_shorts.mp4
    # Subtitle diletakkan di tengah (Alignment=10) dengan warna kuning gaya modern
    final_cmd = [
        "ffmpeg", "-y",
        "-i", "clip_0.mp4", "-i", "clip_1.mp4", "-i", "clip_2.mp4",
        "-i", "voice.mp3",
        "-filter_complex", filter_complex,
        "-map", "[vfinal]", "-map", "3:a",
        "-vf", "subtitles=subtitles.vtt:force_style='Alignment=10,FontSize=22,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3,Outline=1'",
        "-c:v", "libx264", "-c:a aac", "-shortest", "final_shorts.mp4"
    ]

    try:
        subprocess.run(final_cmd, check=True)
        print("SUKSES: Video level 'Influencer Global' siap tayang!")
    except Exception as e:
        print(f"Gagal merakit video final: {e}")
        sys.exit(1)

if __name__ == "__main__":
    rakit_video_world_class()
