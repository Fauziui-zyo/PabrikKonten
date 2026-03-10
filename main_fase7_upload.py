import os
import json
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_ke_youtube():
    print("Mempersiapkan pengunggahan otomatis ke YouTube Shorts...")
    
    # Mengambil rahasia dari environment GitHub
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    creds_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    creds = Credentials.from_authorized_user_info(creds_data)
    
    # Refresh token otomatis jika expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    # Baca metadata dari state.json yang dibuat Gemini
    with open("state.json", "r") as f:
        data = json.load(f)

    request_body = {
        "snippet": {
            "title": data["youtube"]["judul"],
            "description": data["youtube"]["deskripsi"] + "\n\n#shorts #ai #automation",
            "categoryId": "28" # Science & Technology
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    # Upload file final_shorts.mp4 hasil rakitan FFmpeg
    media = MediaFileUpload("final_shorts.mp4", chunksize=-1, resumable=True)
    
    print("Sedang mengirim video ke server YouTube...")
    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )
        response = request.execute()
        print(f"SUKSES! Video Shorts berhasil tayang di: https://youtu.be/{response['id']}")
    except Exception as e:
        print(f"Gagal upload: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload_ke_youtube()
