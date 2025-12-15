"""
MC Macaco Bot - Automated Video Generation Bot.

Workflow:
1. Generate creative script using AI
2. Create viral marketing metadata
3. Generate video with Veo AI
4. Send via Telegram

Runs on schedule: 12:00 and 19:00 daily.
"""

import sys
import time
from pathlib import Path
from typing import NoReturn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import schedule
from dotenv import load_dotenv

from services.ai.marketer import Marketer
from services.ai.screenwriter import Screenwriter
from config import config
from services.integrations.telegram_service import TelegramService, TelegramFormatter
from services.video_generation.video_generator import VideoGenerator


class MCMacacoBot:
    """Main bot orchestrator handling the complete video generation pipeline."""
    
    def __init__(self):
        """Initialize bot components."""
        self.screenwriter = Screenwriter()
        self.marketer = Marketer()
        self.video_generator = VideoGenerator()
        self.telegram = TelegramService()
    
    def _generate_output_path(self) -> Path:
        """
        Generate unique output path for video file.
        
        Returns:
            Path object for the video file
        """
        timestamp = int(time.time())
        filename = f"mc_macaco_{timestamp}.mp4"
        return config.TEMP_VIDEOS_DIR / filename
    
    def run_cycle(self) -> bool:
        """
        Execute one complete content generation cycle.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("🦍 MC MACACO BOT - Starting Generation Cycle")
        print("="*60)
        
        video_path: Path | None = None
        
        try:
            # Step 1: Generate creative script
            print("\n📝 [1/4] Generating script with Gemini AI...")
            script = self.screenwriter.generate()
            print(f"   ✓ Script generated: {script.get('raw_script', 'N/A')[:50]}...")
            
            # Step 2: Create marketing metadata
            print("\n📊 [2/4] Creating viral marketing metadata...")
            marketing = self.marketer.generate(script.get("raw_script", ""))
            
            title = marketing.get("title", "MC Macaco na Selva")
            hashtags = marketing.get("hashtags", [])
            print(f"   ✓ Title: {title}")
            print(f"   ✓ Hashtags: {' '.join(hashtags)}")
            
            # Step 3: Generate video
            print("\n🎬 [3/4] Generating video (this may take 2-3 minutes)...")
            output_path = self._generate_output_path()
            print(f"   → Saving to: {output_path}")
            
            video_path = self.video_generator.generate(
                visual_prompt=script["visual_prompt"],
                audio_prompt=script["audio_prompt"],
                output_path=output_path
            )
            
            if not video_path:
                print("\n❌ Video generation failed")
                self.video_generator.print_stats()
                return False
            
            # Print generation stats
            self.video_generator.print_stats()
            
            # Step 4: Distribute via Telegram
            print(f"\n📱 [4/4] Sending to Telegram: '{title}'")
            
            stats_summary = self.video_generator.get_stats_summary()
            caption = TelegramFormatter.format_video_caption(title, hashtags, stats_summary)
            
            success = self.telegram.send_video(
                video_path=video_path,
                caption=caption
            )
            
            if success:
                print("\n✅ SUCCESS - Video sent to Telegram!")
                return True
            else:
                print("\n⚠️  WARNING - Failed to send to Telegram")
                return False
                
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Cleanup (only if not in debug mode)
            if video_path:
                video_file = Path(video_path) if isinstance(video_path, str) else video_path
                if video_file.exists():
                    if config.DEBUG_MODE:
                        print(f"\n💾 [DEBUG] Video saved at: {video_file}")
                    else:
                        print("\n🧹 Cleaning up temporary files...")
                        video_file.unlink(missing_ok=True)


def setup_scheduler(bot: MCMacacoBot) -> None:
    """
    Configure scheduled execution times.
    
    Args:
        bot: Bot instance to schedule
    """
    for schedule_time in config.SCHEDULE_TIMES:
        schedule.every().day.at(schedule_time).do(bot.run_cycle)
    
    times_str = " and ".join(config.SCHEDULE_TIMES)
    print(f"📅 Scheduled daily execution at: {times_str}")


def run_scheduler() -> NoReturn:
    """Run the scheduler loop indefinitely."""
    print("\n💤 Scheduler active - waiting for scheduled times...")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)


def main() -> None:
    """Main entry point for MC Macaco Bot."""
    # Load environment variables
    load_dotenv()
    
    print("="*60)
    print("🤖 MC MACACO BOT - System Initialized")
    print("="*60)
    print(f"Debug Mode: {'ON' if config.DEBUG_MODE else 'OFF'}")
    print(f"Schedule: {', '.join(config.SCHEDULE_TIMES)}")
    print(f"Video Format: {config.VIDEO_FORMAT} (vertical)")
    print("="*60)
    
    # Initialize bot
    bot = MCMacacoBot()
    
    # Run immediately if configured
    if config.RUN_IMMEDIATELY:
        print("\n⚡ Running immediate test cycle...")
        bot.run_cycle()
    
    # Setup and run scheduler
    setup_scheduler(bot)
    run_scheduler()


if __name__ == "__main__":
    main()
