"""
Telegram Service - Clean Code Version.
Handles all Telegram Bot API interactions.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Callable
import requests


class TelegramService:
    """
    Service for Telegram Bot API interactions.
    
    Responsibilities:
    - Send videos and messages
    - Listen for incoming messages
    - Validate bot configuration
    """
    
    API_BASE_URL = "https://api.telegram.org/bot"
    MAX_CAPTION_LENGTH = 1024
    REQUEST_TIMEOUT = 120
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram service.
        
        Args:
            bot_token: Telegram bot token (defaults to env var)
            chat_id: Target chat ID (defaults to env var)
        """
        self._bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self._chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not self._bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        if not self._chat_id:
            raise ValueError("TELEGRAM_CHAT_ID not configured")
    
    @property
    def is_configured(self) -> bool:
        """Check if service is properly configured."""
        return bool(self._bot_token and self._chat_id)
    
    def send_video(
        self,
        video_path: str | Path,
        caption: str = "",
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Send video file to Telegram chat.
        
        Args:
            video_path: Path to video file
            caption: Video caption (max 1024 chars)
            parse_mode: Caption formatting (HTML or Markdown)
            
        Returns:
            True if sent successfully
            
        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        url = f"{self.API_BASE_URL}{self._bot_token}/sendVideo"
        
        # Truncate caption if too long
        if len(caption) > self.MAX_CAPTION_LENGTH:
            caption = caption[:self.MAX_CAPTION_LENGTH - 3] + "..."
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'chat_id': self._chat_id,
                    'caption': caption,
                    'parse_mode': parse_mode,
                    'supports_streaming': True
                }
                
                response = requests.post(
                    url,
                    files=files,
                    data=data,
                    timeout=self.REQUEST_TIMEOUT
                )
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send video: {e}")
            return False
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send text message to Telegram chat.
        
        Args:
            text: Message text
            parse_mode: Text formatting (HTML or Markdown)
            
        Returns:
            True if sent successfully
        """
        url = f"{self.API_BASE_URL}{self._bot_token}/sendMessage"
        
        try:
            data = {
                'chat_id': self._chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    def listen_for_messages(
        self,
        callback: Callable[[str, int, str], None],
        timeout: int = 30
    ) -> None:
        """
        Start polling for incoming messages.
        
        Args:
            callback: Function called for each message (text, message_id, chat_id)
            timeout: Long polling timeout in seconds
            
        Note:
            This is a blocking operation. Use Ctrl+C to stop.
        """
        print("👂 Listening for messages...")
        
        offset = 0
        
        try:
            while True:
                updates = self._get_updates(offset, timeout)
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    message = update.get('message')
                    if not message:
                        continue
                    
                    # Only process messages from configured chat
                    if str(message['chat']['id']) != str(self._chat_id):
                        continue
                    
                    text = message.get('text', '')
                    message_id = message['message_id']
                    chat_id = str(message['chat']['id'])
                    
                    if text:
                        callback(text, message_id, chat_id)
        
        except KeyboardInterrupt:
            print("\n👋 Stopped listening")
    
    def _get_updates(self, offset: int, timeout: int) -> list:
        """
        Get updates from Telegram API.
        
        Args:
            offset: Update offset for pagination
            timeout: Long polling timeout
            
        Returns:
            List of updates
        """
        url = f"{self.API_BASE_URL}{self._bot_token}/getUpdates"
        
        try:
            params = {
                'offset': offset,
                'timeout': timeout,
                'allowed_updates': ['message']
            }
            
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            
            data = response.json()
            return data.get('result', []) if data.get('ok') else []
            
        except requests.exceptions.RequestException:
            return []
    
    def validate_connection(self) -> bool:
        """
        Test connection to Telegram Bot API.
        
        Returns:
            True if bot is reachable
        """
        url = f"{self.API_BASE_URL}{self._bot_token}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok'):
                bot_name = data['result']['username']
                print(f"✅ Connected to bot: @{bot_name}")
                return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
            return False


class TelegramFormatter:
    """Helper class for formatting Telegram messages."""
    
    @staticmethod
    def format_video_caption(
        title: str,
        hashtags: list[str],
        stats: Optional[str] = None
    ) -> str:
        """
        Format video caption with HTML formatting.
        
        Args:
            title: Video title
            hashtags: List of hashtags
            stats: Optional statistics text
            
        Returns:
            Formatted caption
        """
        hashtags_str = ' '.join(hashtags)
        
        caption = f"""🎬 <b>AI Content Creator - Vídeo Gerado!</b>

📝 <b>Título:</b>
{title}

🏷️ <b>Hashtags:</b>
{hashtags_str}"""
        
        if stats:
            caption += f"\n\n📊 <b>Estatísticas:</b>\n{stats}"
        
        caption += "\n\n✅ Vídeo pronto para upload manual no TikTok!"
        
        return caption
    
    @staticmethod
    def format_download_caption(
        title: str,
        platform: str,
        duration: int,
        size_mb: float
    ) -> str:
        """
        Format downloaded video caption.
        
        Args:
            title: Video title
            platform: Source platform
            duration: Duration in seconds
            size_mb: File size in MB
            
        Returns:
            Formatted caption
        """
        return (
            f"🎬 {title[:100]}\n\n"
            f"📱 Plataforma: {platform}\n"
            f"⏱️ Duração: {duration}s\n"
            f"📏 Tamanho: {size_mb:.1f} MB"
        )
