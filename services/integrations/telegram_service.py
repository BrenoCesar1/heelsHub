"""
Telegram Service - Clean Code Version.
Handles all Telegram Bot API interactions with multi-user support.
"""

from __future__ import annotations
import os
import asyncio
from pathlib import Path
from typing import Optional, Callable, Awaitable, Set
import requests


class TelegramService:
    """
    Service for Telegram Bot API interactions with multi-user support.
    
    Responsibilities:
    - Send videos and messages
    - Listen for incoming messages
    - Validate bot configuration
    - Manage authorized users
    
    Multi-user Support:
    - Set TELEGRAM_AUTHORIZED_CHAT_IDS="id1,id2,id3" in .env for multiple users
    - Each chat_id gets isolated message handling
    - Backward compatible with single TELEGRAM_CHAT_ID
    """
    
    API_BASE_URL = "https://api.telegram.org/bot"
    MAX_CAPTION_LENGTH = 1024
    REQUEST_TIMEOUT = 120
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram service.
        
        Args:
            bot_token: Telegram bot token (defaults to env var)
            chat_id: Target chat ID for sending (defaults to env var, optional for multi-user mode)
        """
        self._bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self._chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not self._bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        
        # Multi-user support: load authorized chat IDs
        self._authorized_chat_ids = self._load_authorized_chat_ids()
        
        # For backward compatibility: if single chat_id is provided, add it to authorized list
        if self._chat_id and self._chat_id not in self._authorized_chat_ids:
            self._authorized_chat_ids.add(self._chat_id)
        
        # If no authorized IDs and no chat_id, we need at least one
        if not self._authorized_chat_ids and not self._chat_id:
            raise ValueError(
                "No chat IDs configured. Set TELEGRAM_CHAT_ID or TELEGRAM_AUTHORIZED_CHAT_IDS"
            )
    
    def _load_authorized_chat_ids(self) -> Set[str]:
        """
        Load authorized chat IDs from environment variable.
        
        Returns:
            Set of authorized chat IDs
        """
        authorized_ids = os.getenv("TELEGRAM_AUTHORIZED_CHAT_IDS", "")
        if not authorized_ids:
            return set()
        
        # Parse comma-separated IDs and clean whitespace
        ids = {chat_id.strip() for chat_id in authorized_ids.split(",") if chat_id.strip()}
        return ids
    
    def is_authorized(self, chat_id: str) -> bool:
        """
        Check if a chat ID is authorized to use the bot.
        
        Args:
            chat_id: Chat ID to check
            
        Returns:
            True if authorized
        """
        return str(chat_id) in self._authorized_chat_ids
    
    def get_authorized_chat_ids(self) -> Set[str]:
        """
        Get all authorized chat IDs.
        
        Returns:
            Set of authorized chat IDs
        """
        return self._authorized_chat_ids.copy()
    
    @property
    def is_configured(self) -> bool:
        """Check if service is properly configured."""
        return bool(self._bot_token and self._chat_id)
    
    def send_video(
        self,
        video_path: str | Path,
        caption: str = "",
        parse_mode: str = "HTML",
        chat_id: Optional[str] = None
    ) -> bool:
        """
        Send video file to Telegram chat.
        
        Args:
            video_path: Path to video file
            caption: Video caption (max 1024 chars)
            parse_mode: Caption formatting (HTML or Markdown)
            chat_id: Specific chat ID to send to (defaults to configured chat_id)
            
        Returns:
            True if sent successfully
            
        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        # Use provided chat_id or default
        target_chat_id = chat_id or self._chat_id
        if not target_chat_id:
            raise ValueError("No chat_id provided and no default configured")
        
        url = f"{self.API_BASE_URL}{self._bot_token}/sendVideo"
        
        # Truncate caption if too long
        if len(caption) > self.MAX_CAPTION_LENGTH:
            caption = caption[:self.MAX_CAPTION_LENGTH - 3] + "..."
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'chat_id': target_chat_id,
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
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"   Telegram API error: {error_detail}")
                except:
                    print(f"   Response text: {e.response.text[:200]}")
            return False
    
    def send_document(self, file_path: Path, caption: str = "", parse_mode: str = "HTML", chat_id: Optional[str] = None) -> bool:
        """
        Send file as document to Telegram chat (fallback when video fails).
        
        Args:
            file_path: Path to file
            caption: File caption
            parse_mode: Text formatting
            chat_id: Specific chat ID to send to (defaults to configured chat_id)
            
        Returns:
            True if sent successfully
        """
        target_chat_id = chat_id or self._chat_id
        if not target_chat_id:
            raise ValueError("No chat_id provided and no default configured")
        
        url = f"{self.API_BASE_URL}{self._bot_token}/sendDocument"
        
        try:
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {
                    'chat_id': target_chat_id,
                    'caption': caption,
                    'parse_mode': parse_mode
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
            print(f"❌ Failed to send document: {e}")
            return False
    
    def send_message(self, text: str, parse_mode: str = "HTML", chat_id: Optional[str] = None) -> bool:
        """
        Send text message to Telegram chat.
        
        Args:
            text: Message text
            parse_mode: Text formatting (HTML or Markdown)
            chat_id: Specific chat ID to send to (defaults to configured chat_id)
            
        Returns:
            True if sent successfully
        """
        target_chat_id = chat_id or self._chat_id
        if not target_chat_id:
            raise ValueError("No chat_id provided and no default configured")
        
        url = f"{self.API_BASE_URL}{self._bot_token}/sendMessage"
        
        try:
            data = {
                'chat_id': target_chat_id,
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
                    
                    chat_id = str(message['chat']['id'])
                    
                    # Check if chat is authorized
                    if not self.is_authorized(chat_id):
                        # Send unauthorized message
                        username = message.get('chat', {}).get('username', 'Unknown')
                        print(f"⚠️  Unauthorized access attempt from chat_id: {chat_id} (@{username})")
                        self.send_message(
                            "❌ Acesso não autorizado. Entre em contato com o administrador.",
                            chat_id=chat_id
                        )
                        continue
                    
                    text = message.get('text', '')
                    message_id = message['message_id']
                    
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

    async def listen_for_messages_async(
        self,
        callback: Callable[[str, int, str], None],
        timeout: int = 30
    ) -> None:
        """
        Async version of message polling for running alongside FastAPI.
        
        Args:
            callback: Function called for each message (text, message_id, chat_id)
            timeout: Long polling timeout in seconds
        """
        print("👂 [Async] Listening for Telegram messages...")
        
        offset = 0
        
        while True:
            try:
                # Run blocking request in executor to not block event loop
                loop = asyncio.get_event_loop()
                updates = await loop.run_in_executor(
                    None, 
                    lambda: self._get_updates(offset, timeout)
                )
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    message = update.get('message')
                    if not message:
                        continue
                    
                    chat_id = str(message['chat']['id'])
                    
                    # Check if chat is authorized
                    if not self.is_authorized(chat_id):
                        username = message.get('chat', {}).get('username', 'Unknown')
                        print(f"⚠️  Unauthorized access attempt from chat_id: {chat_id} (@{username})")
                        await loop.run_in_executor(
                            None,
                            lambda c=chat_id: self.send_message(
                                "❌ Acesso não autorizado. Entre em contato com o administrador.",
                                chat_id=c
                            )
                        )
                        continue
                    
                    text = message.get('text', '')
                    message_id = message['message_id']
                    
                    if text:
                        # Run callback in executor (it may do blocking I/O)
                        await loop.run_in_executor(
                            None,
                            lambda t=text, m=message_id, c=chat_id: callback(t, m, c)
                        )
                        
            except asyncio.CancelledError:
                print("👋 [Async] Telegram listener stopped")
                break
            except Exception as e:
                print(f"⚠️  Telegram polling error: {e}")
                await asyncio.sleep(5)  # Wait before retry


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
