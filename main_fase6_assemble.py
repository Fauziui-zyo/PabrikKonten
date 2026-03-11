import os
from moviepy.editor import *
from moviepy.video.fx.all import *

def rakit_video_modern():
    print("Memulai editing sinematik tingkat lanjut...")
    
    # 1. Ambil bahan
    clips = []
    for i in range(3):
        # Setiap gambar diberikan efek 'Ken Burns' (zoom lambat yang halus)
        img_clip = ImageClip(f"img_{i}.jpg").set_duration(5)
        img_clip = img_clip.resize(lambda t: 1 + 0.04*t) # Zoom in 4% selama 5 detik
        clips.append(img_clip)
    
    # 2. Gabungkan dengan transisi Crossfade (Hanya ini yang terlihat profesional)
    video = concatenate_videoclips(clips, method="compose", padding=-1)
    
    # 3. Masukkan Audio Narasi
    audio = AudioFileClip("voice.mp3")
    video = video.set_audio(audio)
    
    # 4. TAMBAHKAN OVERLAY SINEMATIK (Ini kuncinya!)
    # Kita bisa mendownload video 'Dust Particles' transparan dan menumpuknya
    # Untuk tahap awal, kita gunakan filter warna (Color Grading)
    video = video.fx(vfx.colorx, 1.2) # Meningkatkan kontras sedikit agar 'pop'
    
    # 5. Render dengan kualitas High-Bitrate
    video.write_videofile("final_shorts.mp4", fps=30, codec="libx264", audio_codec="aac", bitrate="5000k")
    print("Video 'World Class' siap tayang!")

if __name__ == "__main__":
    rakit_video_modern()
