
"""
Link Downloader Bot - Clean Code Version.
Listens for video URLs in Telegram and downloads them.
"""

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.integrations.telegram_service import TelegramService, TelegramFormatter
from services.downloads.video_downloader_service import VideoDownloaderService
from services.integrations.tiktok_api_service import TikTokAPIService


class LinkDownloaderBot:
    """
    Bot that downloads videos from social media links.
    
    Workflow:
    1. Listen for Telegram messages
    2. Extract URL from message
    3. Download video
    4. Send back to user
    """
    
    URL_PATTERN = r'https?://[^\s]+'
    
    def __init__(self):
        """Initialize services."""
        self.telegram = TelegramService()
        self.downloader = VideoDownloaderService()
        
        # TikTok auto-upload using official API
        self.auto_upload = os.getenv('TIKTOK_AUTO_UPLOAD', 'false').lower() == 'true'
        self.tiktok_api = None
        
        if self.auto_upload:
            try:
                self.tiktok_api = TikTokAPIService()
                upload_method = "TikTok API (Official)"
            except Exception as e:
                print(f"⚠️  TikTok API init failed: {e}")
                self.auto_upload = False
                upload_method = "Disabled"
        else:
            upload_method = "Disabled"
        
        print("🤖 LINK DOWNLOADER BOT")
        print("=" * 60)
        print("Supports: Instagram, TikTok, Facebook, YouTube, Twitter")
        print(f"TikTok Auto-Upload: {'✅' if self.auto_upload else '❌'} {upload_method}")
        print("=" * 60)
    
    def handle_message(self, message_text: str, message_id: int, chat_id: str) -> None:
        """
        Process incoming Telegram message.
        
        Args:
            message_text: Message text content
            message_id: Telegram message ID
            chat_id: Telegram chat ID
        """
        print(f"\n📩 New message from chat {chat_id}: {message_text[:50]}...")
        
        # Extract URL from message
        url = self._extract_url(message_text)
        if not url:
            print("   ℹ️  No URL found, ignoring")
            return
        
        # Check if platform is supported
        if not self.downloader.is_supported(url):
            platform = self.downloader.get_platform(url) or "unknown"
            self.telegram.send_message(
                f"❌ Unsupported platform: {platform}\n\n"
                f"✅ Supported: Instagram, TikTok, Facebook, YouTube, Twitter",
                chat_id=chat_id
            )
            return
        
        # Notify user that download is starting
        platform = self.downloader.get_platform(url)
        self.telegram.send_message(
            f"⬇️ Downloading from {platform}...\n⏳ Please wait...",
            chat_id=chat_id
        )
        
        # Download video
        video_info = self.downloader.download(url)
        
        if not video_info:
            self.telegram.send_message(
                f"❌ Download failed\n\n"
                f"Possible reasons:\n"
                f"• Private or deleted video\n"
                f"• Invalid link\n"
                f"• Geographic restriction",
                chat_id=chat_id
            )
            return
        
        # Send video to user
        caption = TelegramFormatter.format_download_caption(
            title=video_info.title,
            platform=video_info.platform,
            duration=video_info.duration,
            size_mb=video_info.size_mb
        )
        
        print(f"\n📤 Sending video to Telegram chat {chat_id}...")
        success = self.telegram.send_video(video_info.filepath, caption, chat_id=chat_id)
        
        if success:
            print(f"   ✅ Video sent successfully!")
            
            # TikTok auto-upload (if enabled)
            if self.auto_upload and self.tiktok_api:
                self.telegram.send_message("🚀 Uploading to TikTok...", chat_id=chat_id)
                
                try:
                    # Use ORIGINAL description from video (no AI)
                    description = video_info.description or video_info.title
                    
                    # Limit to 150 chars (TikTok limit)
                    if len(description) > 150:
                        description = description[:147] + "..."
                    
                    print(f"   📝 Using original description:")
                    print(f"      {description[:100]}...")
                    print(f"   📤 Uploading to TikTok via Official API...")
                    
                    publish_id = self.tiktok_api.upload_video(
                        video_path=video_info.filepath,
                        title=description,
                        privacy_level="SELF_ONLY"  # Upload as private for review
                    )
                    
                    if publish_id:
                        print(f"   ✅ TikTok API upload successful!")
                        self.telegram.send_message(
                            f"✅ Video uploaded to TikTok!\n\n"
                            f"📝 Description:\n{description}\n\n"
                            f"🔒 Uploaded as PRIVATE\n"
                            f"📱 Check TikTok app to publish\n\n"
                            f"🆔 Publish ID: {publish_id}",
                            chat_id=chat_id
                        )
                    else:
                        print(f"   ❌ TikTok upload failed")
                        self.telegram.send_message(
                            "❌ TikTok upload failed\n"
                            "💡 Video saved in temp_videos/ for manual upload",
                            chat_id=chat_id
                        )
                        
                except Exception as e:
                    import traceback
                    print(f"   ❌ TikTok error:")
                    print(traceback.format_exc())
                    self.telegram.send_message(
                        f"❌ TikTok error: {str(e)}\n"
                        "💡 Set TIKTOK_AUTO_UPLOAD=false to disable",
                        chat_id=chat_id
                    )
            else:
                print(f"   ℹ️  TikTok auto-upload disabled")
                
                # Show description for manual upload
                description = video_info.description or video_info.title
                if len(description) > 150:
                    description = description[:147] + "..."
                
                self.telegram.send_message(
                    f"✅ Vídeo baixado com sucesso!\n\n"
                    f"📝 Descrição original:\n{description}\n\n"
                    f"💡 Copie a descrição e poste manualmente no TikTok!",
                    chat_id=chat_id
                )

        else:
            print(f"   ❌ Failed to send video")
            self.telegram.send_message(
                f"❌ Video downloaded but failed to send\n"
                f"Size: {video_info.size_mb:.1f} MB\n\n"
                f"(Telegram has 50 MB limit for videos)",
                chat_id=chat_id
            )
        
        # Cleanup downloaded file
        try:
            video_info.filepath.unlink()
            print(f"   🧹 Temporary file removed")
        except Exception as e:
            print(f"   ⚠️  Failed to remove file: {e}")
    
    def run(self) -> None:
        """Start the bot."""
        print("\n✅ Bot started!")
        print("💡 Send video links to the bot on Telegram\n")
        
        # Cleanup old files
        self.downloader.cleanup_old_files()
        
        # Start listening
        try:
            self.telegram.listen_for_messages(self.handle_message)
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")
    
    def _extract_url(self, text: str) -> str:
        """
        Extract URL from text.
        
        Args:
            text: Text to search
            
        Returns:
            First URL found or empty string
        """
        match = re.search(self.URL_PATTERN, text)
        return match.group(0) if match else ""


def main():
    """Entry point."""
    # Load environment variables
    load_dotenv()
    
    # Validate configuration
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not configured in .env")
        sys.exit(1)
    
    if not os.getenv("TELEGRAM_CHAT_ID"):
        print("❌ ERROR: TELEGRAM_CHAT_ID not configured in .env")
        sys.exit(1)
    
    # Start bot
    bot = LinkDownloaderBot()
    bot.run()


if __name__ == "__main__":
    main()
