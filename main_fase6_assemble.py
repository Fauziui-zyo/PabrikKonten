import os, subprocess, sys

def run():
    print("Agent: Merakit video viral...")
    for i in range(3):
        # Setiap adegan 5 detik + Slow Zoom
        subprocess.run(f"ffmpeg -y -loop 1 -i img_{i}.jpg -vf \"scale=8000:-1,zoompan=z='zoom+0.001':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1920\" -c:v libx264 -t 5 -pix_fmt yuv420p c_{i}.mp4", shell=True)

    # Gabung dengan XFade (Transisi Mulus) + Burn Subtitles
    filter = "[0:v][1:v]xfade=transition=fade:duration=1:offset=4[v01]; [v01][2:v]xfade=transition=fade:duration=1:offset=8[vfinal]"
    cmd = [
        "ffmpeg", "-y", "-i", "c_0.mp4", "-i", "c_1.mp4", "-i", "c_2.mp4", "-i", "voice.mp3",
        "-filter_complex", filter, "-map", "[vfinal]", "-map", "3:a",
        "-vf", "subtitles=subtitles.vtt:force_style='Alignment=10,FontSize=22,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3,Outline=1'",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", "final_shorts.mp4"
    ]
    subprocess.run(cmd, check=True)
    print("Fase 6 Sukses.")

if __name__ == "__main__": run()
