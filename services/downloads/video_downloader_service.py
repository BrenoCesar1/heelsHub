"""
Video Downloader Service - Clean Code Version.
Downloads videos from social media platforms using yt-dlp.
"""

import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """Information about a downloaded video."""
    filepath: Path
    title: str
    platform: str
    duration: int  # seconds
    size_mb: float


class VideoDownloaderService:
    """
    Service for downloading videos from social media platforms.
    
    Supported platforms:
    - Instagram
    - TikTok
    - Facebook
    - YouTube
    - Twitter/X
    """
    
    SUPPORTED_PLATFORMS = {
        'instagram.com': 'Instagram',
        'tiktok.com': 'TikTok',
        'facebook.com': 'Facebook',
        'fb.watch': 'Facebook',
        'youtube.com': 'YouTube',
        'youtu.be': 'YouTube',
        'twitter.com': 'Twitter',
        'x.com': 'Twitter',
    }
    
    def __init__(self, output_dir: str = "temp_videos"):
        """
        Initialize downloader service.
        
        Args:
            output_dir: Directory to save downloaded videos
            
        Raises:
            ImportError: If yt-dlp is not installed
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """Check if yt-dlp is installed."""
        try:
            import yt_dlp  # noqa
        except ImportError:
            raise ImportError(
                "yt-dlp is not installed. "
                "Install with: pip install yt-dlp"
            )
    
    def is_supported(self, url: str) -> bool:
        """
        Check if URL is from a supported platform.
        
        Args:
            url: URL to check
            
        Returns:
            True if platform is supported
        """
        try:
            domain = self._extract_domain(url)
            return any(
                platform in domain
                for platform in self.SUPPORTED_PLATFORMS.keys()
            )
        except Exception:
            return False
    
    def get_platform(self, url: str) -> Optional[str]:
        """
        Identify platform from URL.
        
        Args:
            url: URL to identify
            
        Returns:
            Platform name or None if not supported
        """
        try:
            domain = self._extract_domain(url)
            
            for platform_domain, platform_name in self.SUPPORTED_PLATFORMS.items():
                if platform_domain in domain:
                    return platform_name
            
            return None
        except Exception:
            return None
    
    def download(self, url: str) -> Optional[VideoInfo]:
        """
        Download video from URL.
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo if successful, None otherwise
        """
        if not self.is_supported(url):
            print(f"❌ Unsupported URL: {url}")
            return None
        
        platform = self.get_platform(url)
        print(f"\n⬇️  Downloading from {platform}...")
        print(f"   URL: {url}")
        
        try:
            return self._download_with_ytdlp(url, platform)
        except Exception as e:
            print(f"   ❌ Download failed: {type(e).__name__}: {e}")
            return None
    
    def _download_with_ytdlp(self, url: str, platform: str) -> VideoInfo:
        """
        Download video using yt-dlp library.
        
        Args:
            url: Video URL
            platform: Platform name
            
        Returns:
            VideoInfo object
            
        Raises:
            Exception: If download fails
        """
        import yt_dlp
        
        options = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(self.output_dir / '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if not info:
                raise ValueError("Failed to extract video information")
            
            # Extract metadata
            video_id = info.get('id', 'unknown')
            title = info.get('title', 'Untitled')
            duration = info.get('duration', 0)
            ext = info.get('ext', 'mp4')
            
            # Locate downloaded file
            filepath = self.output_dir / f"{video_id}.{ext}"
            
            if not filepath.exists():
                raise FileNotFoundError("Downloaded file not found")
            
            # Calculate file size
            size_bytes = filepath.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            print(f"   ✅ Download complete!")
            print(f"   📁 File: {filepath.name}")
            print(f"   📏 Size: {size_mb:.2f} MB")
            print(f"   ⏱️  Duration: {duration}s")
            
            return VideoInfo(
                filepath=filepath,
                title=title,
                platform=platform,
                duration=int(duration),
                size_mb=size_mb
            )
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Remove old downloaded files.
        
        Args:
            max_age_hours: Maximum file age in hours
            
        Returns:
            Number of files removed
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        removed_count = 0
        
        for filepath in self.output_dir.glob("*"):
            if not filepath.is_file():
                continue
            
            file_age = current_time - filepath.stat().st_mtime
            
            if file_age > max_age_seconds:
                try:
                    filepath.unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to remove {filepath.name}: {e}")
        
        if removed_count > 0:
            print(f"🧹 Cleanup: {removed_count} old file(s) removed")
        
        return removed_count
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc.lower().replace('www.', '')
