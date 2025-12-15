"""Video generation service using Google Labs Veo API with multi-account support."""

from pathlib import Path
from typing import Optional

from .multi_account_labs_service import MultiAccountLabsService


class VideoGenerator:
    """
    Generates videos using Google Labs Veo API with automatic account rotation.
    
    This service manages multiple API accounts and automatically switches between them
    when quota limits are reached, providing seamless video generation.
    """
    
    def __init__(self):
        """Initialize video generator with multi-account Labs service."""
        self._labs_service = MultiAccountLabsService()
        self._videos_generated = 0
        self._total_errors = 0
    
    def generate(
        self,
        visual_prompt: str,
        audio_prompt: str,
        output_path: str | Path
    ) -> Optional[str]:
        """
        Generate a video from visual and audio prompts.
        
        Args:
            visual_prompt: English description of the visual scene
            audio_prompt: Portuguese dialogue and audio description
            output_path: Where to save the generated video
            
        Returns:
            Path to generated video if successful, None otherwise
            
        Raises:
            ValueError: If prompts are empty
        """
        if not visual_prompt or not audio_prompt:
            raise ValueError("Both visual_prompt and audio_prompt are required")
        
        try:
            print("🎥 Generating video via Google Labs API...")
            
            video_path = self._labs_service.generate_video(
                visual_prompt=visual_prompt,
                audio_prompt=audio_prompt,
                output_path=str(output_path)
            )
            
            if video_path:
                self._videos_generated += 1
                print("✓ Video generated successfully via Labs API")
                return video_path
            
            self._total_errors += 1
            return None
            
        except Exception as e:
            print(f"❌ Error generating video: {type(e).__name__}: {e}")
            self._total_errors += 1
            return None
    
    def get_stats(self) -> dict[str, any]:
        """
        Get generation statistics.
        
        Returns:
            Dictionary with stats including videos generated, errors, and account info
        """
        account_info = self._labs_service.get_current_account_info()
        
        return {
            'videos_generated': self._videos_generated,
            'errors': self._total_errors,
            'current_account': account_info['email'],
            'credits_remaining': account_info['credits_remaining'],
            'credits_used': account_info['credits_used']
        }
    
    def print_stats(self) -> None:
        """Print detailed statistics about video generation and accounts."""
        print("\n" + "="*50)
        print("📊 VIDEO GENERATION STATISTICS")
        print("="*50)
        print(f"Videos generated: {self._videos_generated}")
        print(f"Errors: {self._total_errors}")
        
        self._labs_service.print_stats()
        print("="*50 + "\n")
    
    def get_stats_summary(self) -> str:
        """
        Get a brief summary of stats for notifications.
        
        Returns:
            Formatted string with key statistics
        """
        stats = self.get_stats()
        
        summary = f"Videos: {stats['videos_generated']}\n"
        summary += f"Errors: {stats['errors']}\n\n"
        summary += f"📊 Account: {stats['current_account']}\n"
        summary += f"Credits: {stats['credits_remaining']}/1000"
        
        return summary
