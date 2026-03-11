import os, json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def run():
    print("Agent: Mengunggah ke YouTube...")
    creds = Credentials.from_authorized_user_info({
        "client_id": os.environ.get("YT_CLIENT_ID"),
        "client_secret": os.environ.get("YT_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YT_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    youtube = build("youtube", "v3", credentials=creds)
    with open("state.json", "r") as f: data = json.load(f)

    body = {
        "snippet": {"title": data["youtube"]["judul"], "description": data["youtube"]["deskripsi"], "categoryId": "28"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload("final_shorts.mp4", chunksize=-1, resumable=True)
    youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    print("Fase 7 Sukses! Video LIVE.")

if __name__ == "__main__": run()
