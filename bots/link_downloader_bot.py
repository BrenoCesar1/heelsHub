
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
from services.integrations.tiktok_service import TikTokUploader
from services.ai.marketer import Marketer


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
        self.tiktok = TikTokUploader()
        self.marketer = Marketer()
        
        print("🤖 LINK DOWNLOADER BOT")
        print("=" * 60)
        print("Supports: Instagram, TikTok, Facebook, YouTube, Twitter")
        print("=" * 60)
    
    def handle_message(self, message_text: str, message_id: int, chat_id: str) -> None:
        """
        Process incoming Telegram message.
        
        Args:
            message_text: Message text content
            message_id: Telegram message ID
            chat_id: Telegram chat ID
        """
        print(f"\n📩 New message: {message_text[:50]}...")
        
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
                f"✅ Supported: Instagram, TikTok, Facebook, YouTube, Twitter"
            )
            return
        
        # Notify user that download is starting
        platform = self.downloader.get_platform(url)
        self.telegram.send_message(
            f"⬇️ Downloading from {platform}...\n⏳ Please wait..."
        )
        
        # Download video
        video_info = self.downloader.download(url)
        
        if not video_info:
            self.telegram.send_message(
                f"❌ Download failed\n\n"
                f"Possible reasons:\n"
                f"• Private or deleted video\n"
                f"• Invalid link\n"
                f"• Geographic restriction"
            )
            return
        
        # Send video to user
        caption = TelegramFormatter.format_download_caption(
            title=video_info.title,
            platform=video_info.platform,
            duration=video_info.duration,
            size_mb=video_info.size_mb
        )
        
        print(f"\n📤 Sending video to Telegram...")
        success = self.telegram.send_video(video_info.filepath, caption)
        
        if success:
            print(f"   ✅ Video sent successfully!")
            self.telegram.send_message("🚀 Preparing to upload to TikTok...")
            
            # Generate marketing metadata
            try:
                metadata = self.marketer.generate(video_info.title)
                
                # Upload to TikTok
                tiktok_success = self.tiktok.upload_video(
                    file_path=str(video_info.filepath),
                    title=metadata['title'],
                    hashtags=metadata['hashtags']
                )
                
                if tiktok_success:
                    self.telegram.send_message("✅ Video uploaded to TikTok successfully!")
                else:
                    self.telegram.send_message("❌ Failed to upload video to TikTok.")
                    
            except Exception as e:
                print(f"   ❌ Failed to generate metadata or upload to TikTok: {e}")
                self.telegram.send_message("❌ Failed to generate metadata or upload to TikTok.")

        else:
            print(f"   ❌ Failed to send video")
            self.telegram.send_message(
                f"❌ Video downloaded but failed to send\n"
                f"Size: {video_info.size_mb:.1f} MB\n\n"
                f"(Telegram has 50 MB limit for videos)"
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
