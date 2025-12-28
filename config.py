"""Configuration settings for AI Content Creator Bot."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BotConfig:
    """Centralized configuration for the bot."""
    
    # Execution settings
    DEBUG_MODE: bool = True
    RUN_IMMEDIATELY: bool = True
    
    # Scheduling
    SCHEDULE_TIMES: tuple[str, ...] = ("12:00", "19:00")
    
    # Directories
    PROJECT_ROOT: Path = Path(__file__).parent.resolve()
    TEMP_VIDEOS_DIR: Path = PROJECT_ROOT / "temp_videos"
    
    # Video settings
    VIDEO_DURATION_SECONDS: int = 8
    VIDEO_FORMAT: str = "9:16"  # Vertical format for TikTok/Reels
    
    # AI Models
    GEMINI_MODEL: str = "gemini-2.0-flash-thinking-exp"  # Experimental model with enhanced reasoning
    VEO_MODEL: str = "veo-3.1-fast-generate-preview"
    
    # Credits
    CREDITS_PER_VIDEO: int = 20
    MAX_CREDITS_PER_ACCOUNT: int = 1000
    
    def __post_init__(self):
        """Ensure directories exist."""
        object.__setattr__(self, 'TEMP_VIDEOS_DIR', self.TEMP_VIDEOS_DIR.resolve())
        self.TEMP_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = BotConfig()

# Backwards-compatible module-level settings
from os import getenv

# Expose common settings as module-level variables for older imports
TEMP_VIDEOS_DIR = config.TEMP_VIDEOS_DIR
GEMINI_MODEL = config.GEMINI_MODEL
VEO_MODEL = config.VEO_MODEL

# Toggle automatic TikTok uploads (can be set via environment)
TIKTOK_AUTO_UPLOAD = getenv('TIKTOK_AUTO_UPLOAD', 'true').lower() in ('1', 'true', 'yes')

# Optional TikTok credentials from environment (if provided)
TIKTOK_CLIENT_KEY = getenv('TIKTOK_CLIENT_KEY')
TIKTOK_CLIENT_SECRET = getenv('TIKTOK_CLIENT_SECRET')
