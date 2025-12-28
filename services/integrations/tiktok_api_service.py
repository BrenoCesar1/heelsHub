"""
TikTok API Service - Official Content Posting API
Simple helper for OAuth and video upload (uses port 8070 as default callback).
"""

import os
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class TikTokAPIService:
    """Service for uploading videos to TikTok using the official Content Posting API.

    Defaults use http://localhost:8070/callback for OAuth redirect when running locally.
    """

    OAUTH_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    UPLOAD_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"

    def __init__(self):
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY', '')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET', '')
        self.access_token: Optional[str] = None

        if not self.client_key or not self.client_secret:
            raise ValueError("TikTok API credentials not found. Set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET in .env")

    def get_authorization_url(self, redirect_uri: str = "http://localhost:8070/callback") -> str:
        scopes = ['video.upload', 'video.publish']
        auth_url = (
            f"https://www.tiktok.com/v2/auth/authorize/?client_key={self.client_key}"
            f"&scope={','.join(scopes)}&response_type=code&redirect_uri={redirect_uri}&state=random_state_string"
        )
        return auth_url

    def exchange_code_for_token(self, code: str, redirect_uri: str = "http://localhost:8070/callback") -> bool:
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(self.OAUTH_URL, data=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            token = result.get('access_token')
            if token:
                self.access_token = token
                Path('.tiktok_token').write_text(token)
                print("✅ Access token obtained and saved")
                return True

            print(f"❌ No access token in response: {result}")
            return False

        except requests.RequestException as e:
            print(f"❌ Token exchange failed: {e}")
            return False

    def load_token(self) -> bool:
        token_file = Path('.tiktok_token')
        if token_file.exists():
            self.access_token = token_file.read_text().strip()
            print("✅ Access token loaded from file")
            return True
        return False

    def upload_video(self, video_path: Path, title: str, privacy_level: str = "SELF_ONLY") -> Optional[str]:
        if not self.access_token:
            if not self.load_token():
                print("❌ No access token. Run authorization flow first.")
                return None

        video_size = video_path.stat().st_size

        init_headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json; charset=UTF-8'}

        init_data = {
            'post_info': {'title': title[:150], 'privacy_level': privacy_level},
            'source_info': {'source': 'FILE_UPLOAD', 'video_size': video_size, 'chunk_size': video_size, 'total_chunk_count': 1},
        }

        try:
            response = requests.post(self.UPLOAD_INIT_URL, headers=init_headers, json=init_data)
            response.raise_for_status()
            result = response.json()

            data = result.get('data') or {}
            upload_url = data.get('upload_url')
            publish_id = data.get('publish_id')

            if not upload_url or not publish_id:
                print(f"❌ Upload init failed: {result}")
                return None

            print(f"✅ Upload initialized (ID: {publish_id})")

            with open(video_path, 'rb') as f:
                upload_resp = requests.put(upload_url, data=f, headers={'Content-Type': 'video/mp4', 'Content-Length': str(video_size)})
                upload_resp.raise_for_status()

            print("✅ Video uploaded successfully!")
            return publish_id

        except requests.RequestException as e:
            print(f"❌ Upload failed: {e}")
            return None


def setup_tiktok_auth():
    print("\n🔐 TIKTOK API AUTHORIZATION SETUP")
    service = TikTokAPIService()
    auth_url = service.get_authorization_url()
    print(f"\n1. Open this URL in your browser:\n   {auth_url}")
    print("\n2. After authorizing you'll be redirected to http://localhost:8070/callback?code=...\n")
    code = input("📋 Paste the authorization code here: ").strip()
    if not code:
        print("❌ No code provided")
        return
    if service.exchange_code_for_token(code):
        print("\n✅ Authorization complete! Access token saved to .tiktok_token")
    else:
        print("\n❌ Authorization failed")


if __name__ == '__main__':
    setup_tiktok_auth()
