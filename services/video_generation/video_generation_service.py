"""
Video Generation Service.

Core service for generating AI-powered videos. Can be used by both the API
and the scheduler for consistent video generation logic.
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any

import config
from services.ai.screenwriter import Screenwriter
from services.video_generation.video_generator import VideoGenerator
from services.integrations.telegram_service import TelegramService
from services.integrations.tiktok_api_service import TikTokAPIService


class VideoGenerationService:
    """
    Service for generating videos with AI.
    
    Orchestrates the complete video generation pipeline:
    1. Generate script from idea (or use random)
    2. Generate video with Veo
    3. Send to Telegram (optional)
    4. Post to TikTok (optional)
    """
    
    def __init__(self):
        """Initialize video generation service."""
        self.screenwriter = Screenwriter()
        self.video_generator = VideoGenerator()
        self.telegram_service = TelegramService()
        self.tiktok_service = TikTokAPIService() if config.TIKTOK_AUTO_UPLOAD else None
    
    def generate_video(
        self,
        user_idea: Optional[str] = None,
        send_to_telegram: bool = True,
        post_to_tiktok: bool = True,
        custom_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete video from idea to distribution.
        
        Args:
            user_idea: User's video idea. If None, generates random idea.
            send_to_telegram: Whether to send video to Telegram
            post_to_tiktok: Whether to post video to TikTok
            custom_title: Custom title for video (optional)
            
        Returns:
            Dict with generation results including video_path, telegram_sent, tiktok_posted
            
        Raises:
            Exception: If critical step fails
        """
        result = {
            'success': False,
            'video_path': None,
            'telegram_sent': False,
            'tiktok_posted': False,
            'error': None
        }
        
        try:
            print("\n" + "="*60)
            print("🤖 AI CONTENT CREATOR - Starting Generation")
            print("="*60)
            
            # Step 1: Generate script
            print("\n📝 Step 1/4: Generating AI script...")
            if user_idea:
                print(f"   User idea: {user_idea[:100]}...")
                # Enhance user idea with AI
                script = self.screenwriter.enhance_user_idea(user_idea)
            else:
                script = self.screenwriter.generate_script()
            
            print("   ✅ Script generated successfully")
            print(f"   Visual: {script.visual_prompt[:100]}...")
            print(f"   Audio: {script.audio_prompt[:50]}...")
            
            # Step 2: Generate video
            print("\n🎬 Step 2/4: Generating video with Veo...")
            video_path = self._generate_output_path()
            
            self.video_generator.generate(
                prompt=script.visual_prompt,
                audio_prompt=script.audio_prompt,
                output_path=video_path
            )
            
            print(f"   ✅ Video generated: {video_path.name}")
            result['video_path'] = str(video_path)
            
            # Step 3: Send to Telegram
            if send_to_telegram:
                print("\n📱 Step 3/4: Sending to Telegram...")
                try:
                    video_title = custom_title or "AI Generated Video"
                    caption = self._format_telegram_caption(script, video_title)
                    
                    self.telegram_service.send_video(
                        video_path=video_path,
                        caption=caption
                    )
                    print("   ✅ Sent to Telegram")
                    result['telegram_sent'] = True
                except Exception as e:
                    print(f"   ⚠️ Telegram send failed: {e}")
            else:
                print("\n📱 Step 3/4: Skipping Telegram (disabled)")
            
            # Step 4: Post to TikTok
            if post_to_tiktok and self.tiktok_service:
                print("\n🎵 Step 4/4: Posting to TikTok...")
                try:
                    video_title = custom_title or "AI Generated Video"
                    publish_id = self.tiktok_service.upload_video(
                        video_path=video_path,
                        title=video_title,
                        privacy_level="SELF_ONLY"  # Sandbox limitation
                    )
                    print(f"   ✅ Posted to TikTok (ID: {publish_id})")
                    result['tiktok_posted'] = True
                except Exception as e:
                    print(f"   ⚠️ TikTok upload failed: {e}")
            else:
                print("\n🎵 Step 4/4: Skipping TikTok (disabled)")
            
            print("\n" + "="*60)
            print("✅ GENERATION COMPLETED SUCCESSFULLY")
            print("="*60)
            
            result['success'] = True
            return result
            
        except Exception as e:
            print(f"\n❌ GENERATION FAILED: {e}")
            result['error'] = str(e)
            raise
    
    def _generate_output_path(self) -> Path:
        """Generate unique output path for video."""
        timestamp = int(time.time())
        filename = f"ai_content_{timestamp}.mp4"
        return config.TEMP_VIDEOS_DIR / filename
    
    def _format_telegram_caption(self, script, title: str) -> str:
        """Format caption for Telegram message."""
        return (
            f"🤖 *AI Content Creator - Vídeo Gerado!*\n\n"
            f"*Título:* {title}\n\n"
            f"*Script:*\n{script.raw_script}\n\n"
            f"_Gerado com Gemini 2.0 Flash + Veo 3.1_"
        )
