"""
FastAPI main application.

REST API for AI-powered video generation and management.
"""

import os
import re
import schedule
import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Get port from environment (Render sets $PORT dynamically)
PORT = int(os.getenv("PORT", 8070))

# Check if Telegram bot should run (enabled by default if tokens are set)
ENABLE_TELEGRAM_BOT = os.getenv("ENABLE_TELEGRAM_BOT", "true").lower() == "true"

from api.routes import (
    health_router,
    videos_router,
    ideas_router,
    scheduler_router
)


class EmbeddedLinkDownloaderBot:
    """
    Embedded version of LinkDownloaderBot for running inside FastAPI.
    """
    
    URL_PATTERN = r'https?://[^\s]+'
    
    def __init__(self):
        from services.integrations.telegram_service import TelegramService, TelegramFormatter
        from services.downloads.video_downloader_service import VideoDownloaderService
        from services.integrations.tiktok_api_service import TikTokAPIService
        
        self.telegram = TelegramService()
        self.downloader = VideoDownloaderService()
        self.formatter = TelegramFormatter
        
        # TikTok auto-upload
        self.auto_upload = os.getenv('TIKTOK_AUTO_UPLOAD', 'false').lower() == 'true'
        self.tiktok_api = None
        
        # Lock for concurrent processing (limit to 1 at a time)
        self.processing_lock = threading.Lock()
        
        if self.auto_upload:
            try:
                self.tiktok_api = TikTokAPIService()
            except Exception:
                self.auto_upload = False
    
    def handle_message(self, message_text: str, message_id: int, chat_id: str) -> None:
        """Process incoming Telegram message."""
        print(f"\n📩 [Bot] New message from chat {chat_id}: {message_text[:50]}...")
        
        # Extract URL
        match = re.search(self.URL_PATTERN, message_text)
        if not match:
            return
        
        url = match.group(0)
        
        # Check processing lock
        acquired = self.processing_lock.acquire(blocking=False)
        if not acquired:
            print(f"⏳ Busy processing another request. Queuing chat {chat_id}...")
            self.telegram.send_message(
                "⏳ <b>Todos os processadores ocupados.</b>\nVocê está na fila, aguarde um momento...",
                chat_id=chat_id
            )
            # Wait for lock
            self.processing_lock.acquire()
            
        try:
            if not self.downloader.is_supported(url):
                platform = self.downloader.get_platform(url) or "unknown"
                self.telegram.send_message(
                    f"❌ Unsupported platform: {platform}\n\n"
                    f"✅ Supported: Instagram, TikTok, Facebook, YouTube, Twitter",
                    chat_id=chat_id
                )
                return
            
            platform = self.downloader.get_platform(url)
            self.telegram.send_message(
                f"⬇️ Downloading from {platform}...\n⏳ Please wait...",
                chat_id=chat_id
            )
            
            video_info = None
            try:
                video_info = self.downloader.download(url)
                
                if not video_info:
                    self.telegram.send_message("❌ Download failed", chat_id=chat_id)
                    return
                
                caption = self.formatter.format_download_caption(
                    title=video_info.title,
                    platform=video_info.platform,
                    duration=video_info.duration,
                    size_mb=video_info.size_mb
                )
                
                success = self.telegram.send_video(video_info.filepath, caption, chat_id=chat_id)
                
                # Fallback: if video fails, try sending as document
                if not success:
                    print(f"⚠️  Video send failed, trying as document...")
                    success = self.telegram.send_document(video_info.filepath, caption, chat_id=chat_id)
                    if not success:
                        self.telegram.send_message(
                            f"❌ Failed to send video\n\n"
                            f"📹 {video_info.title[:50]}\n"
                            f"📏 {video_info.size_mb:.2f} MB\n"
                            f"⏱️  {video_info.duration}s",
                            chat_id=chat_id
                        )
                
                if success:
                    description = video_info.description or video_info.title
                    if len(description) > 150:
                        description = description[:147] + "..."
                    
                    if self.auto_upload and self.tiktok_api:
                        self.telegram.send_message("🚀 Uploading to TikTok...", chat_id=chat_id)
                        try:
                            publish_id = self.tiktok_api.upload_video(
                                video_path=video_info.filepath,
                                title=description,
                                privacy_level="SELF_ONLY"
                            )
                            if publish_id:
                                self.telegram.send_message(
                                    f"✅ Uploaded to TikTok!\n🔒 As PRIVATE\n🆔 ID: {publish_id}",
                                    chat_id=chat_id
                                )
                        except Exception as e:
                            self.telegram.send_message(f"❌ TikTok error: {e}", chat_id=chat_id)
                    else:
                        self.telegram.send_message(
                            f"✅ Vídeo baixado!\n\n📝 Descrição:\n{description}",
                            chat_id=chat_id
                        )
            
            finally:
                # Cleanup video file if it exists
                if video_info and video_info.filepath.exists():
                    try:
                        video_info.filepath.unlink()
                        print(f"   🧹 Cleanup: Removed {video_info.filepath.name}")
                    except Exception as e:
                        print(f"   ⚠️ Cleanup failed: {e}")

        except Exception as e:
            print(f"❌ Error handling message: {e}")
            self.telegram.send_message(f"❌ Internal process error: {str(e)}", chat_id=chat_id)
            
        finally:
            self.processing_lock.release()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown including scheduler and Telegram bot.
    """
    # Startup
    print("\n" + "="*60)
    print("🚀 AI CONTENT CREATOR API - Starting Up")
    print("="*60)
    
    tasks = []
    
    # Start scheduler polling task
    async def run_scheduler():
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
    
    scheduler_task = asyncio.create_task(run_scheduler())
    tasks.append(scheduler_task)
    
    # Start Telegram bot if configured
    bot_task = None
    if ENABLE_TELEGRAM_BOT:
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
        telegram_authorized = os.getenv("TELEGRAM_AUTHORIZED_CHAT_IDS")
        
        # Bot needs either TELEGRAM_CHAT_ID or TELEGRAM_AUTHORIZED_CHAT_IDS
        if telegram_token and (telegram_chat or telegram_authorized):
            try:
                bot = EmbeddedLinkDownloaderBot()
                
                # Schedule cleanup every hour
                schedule.every(1).hours.do(bot.downloader.cleanup_old_files)
                print("🧹 Scheduled temporary file cleanup (every 1h)")
                
                # Show configured users
                authorized_ids = bot.telegram.get_authorized_chat_ids()
                print(f"🤖 Telegram Link Downloader Bot: ENABLED")
                print(f"👥 Authorized users: {len(authorized_ids)}")
                
                async def run_telegram_bot():
                    await bot.telegram.listen_for_messages_async(bot.handle_message)
                
                bot_task = asyncio.create_task(run_telegram_bot())
                tasks.append(bot_task)
            except Exception as e:
                print(f"⚠️  Telegram Bot failed to start: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("ℹ️  Telegram Bot: DISABLED (no tokens configured)")
            if not telegram_token:
                print("   Missing: TELEGRAM_BOT_TOKEN")
            if not telegram_chat and not telegram_authorized:
                print("   Missing: TELEGRAM_CHAT_ID or TELEGRAM_AUTHORIZED_CHAT_IDS")
    else:
        print("ℹ️  Telegram Bot: DISABLED (ENABLE_TELEGRAM_BOT=false)")
    
    print("✅ API is ready")
    print(f"📚 Documentation: http://localhost:{PORT}/docs")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down API...")
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    print("✅ Shutdown complete\n")


# Create FastAPI app
app = FastAPI(
    title="AI Content Creator API",
    description=(
        "REST API for AI-powered video generation and management.\n\n"
        "Features:\n"
        "- Generate videos from user ideas\n"
        "- Save and manage video ideas\n"
        "- Schedule automatic video generation\n"
        "- Integrate with Telegram and TikTok"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(videos_router)
app.include_router(ideas_router)
app.include_router(scheduler_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )
