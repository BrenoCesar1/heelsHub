"""
Video Downloader Service - Clean Code Version.
Downloads videos from social media platforms using yt-dlp.
"""

import time
import subprocess
import os
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
    description: str = ""  # Original video description


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
        
        # Base options with anti-detection measures
        options = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(self.output_dir / '%(id)s.%(ext)s'),
            'quiet': False,  # Show output for debugging
            'no_warnings': False,
            'noplaylist': True,
            'socket_timeout': 30,
            'retries': 3,
            # Anti-bot detection headers
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': url,  # Set referer to the URL itself
            'nocheckcertificate': True,
            # Ensure Telegram-compatible format (MP4 with H.264)
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        # Instagram-specific options (help with rate limits)
        if 'instagram' in url.lower():
            options['extractor_args'] = {
                'instagram': {
                    'api_type': 'graphql',  # Use GraphQL API (more stable)
                }
            }

        # Optional credentials/cookies support via environment variables
        # For Instagram: cookies are HIGHLY RECOMMENDED to avoid rate limits
        # Support multiple ways to provide cookies:
        # 1) YTDLP_COOKIES_FILE - path to existing file
        # 2) YTDLP_COOKIES_CONTENT - full cookies.txt content (may be too large for Render)
        # 3) INSTAGRAM_SESSIONID + INSTAGRAM_CSRFTOKEN + INSTAGRAM_DS_USER_ID (minimal, recommended for Render)
        cookies_file = os.getenv('YTDLP_COOKIES_FILE')
        cookies_content = os.getenv('YTDLP_COOKIES_CONTENT')
        username = os.getenv('YTDLP_USERNAME')
        password = os.getenv('YTDLP_PASSWORD')
        
        # Instagram minimal cookies (for Render where full cookies.txt is too large)
        ig_sessionid = os.getenv('INSTAGRAM_SESSIONID')
        ig_csrftoken = os.getenv('INSTAGRAM_CSRFTOKEN')
        ig_ds_user_id = os.getenv('INSTAGRAM_DS_USER_ID')

        # Priority 1: Individual Instagram cookies (most reliable for Render)
        if ig_sessionid and 'instagram' in url.lower():
            try:
                cookies_path = self.output_dir / "cookies_instagram_minimal.txt"
                with open(cookies_path, 'w') as f:
                    f.write("# Netscape HTTP Cookie File\n")
                    f.write("# Generated from INSTAGRAM_* env vars\n\n")
                    # Essential Instagram cookies only
                    f.write(f".instagram.com\tTRUE\t/\tTRUE\t1999999999\tsessionid\t{ig_sessionid}\n")
                    if ig_csrftoken:
                        f.write(f".instagram.com\tTRUE\t/\tTRUE\t1999999999\tcsrftoken\t{ig_csrftoken}\n")
                    if ig_ds_user_id:
                        f.write(f".instagram.com\tTRUE\t/\tTRUE\t1999999999\tds_user_id\t{ig_ds_user_id}\n")
                options['cookiefile'] = str(cookies_path)
                print(f"   🔐 Created minimal Instagram cookies from env vars")
            except Exception as e:
                print(f"   ⚠️  Failed to create minimal cookies: {e}")
        # Priority 2: Full cookies content (may fail on Render if too large)
        elif cookies_content:
            try:
                cookies_path = self.output_dir / "cookies_from_env.txt"
                cookies_path.write_text(cookies_content)
                options['cookiefile'] = str(cookies_path)
                print(f"   🔐 Wrote cookies from YTDLP_COOKIES_CONTENT to: {cookies_path}")
            except Exception as e:
                print(f"   ⚠️  Failed to write cookies from env: {e}")
        # Priority 3: Path to existing file
        elif cookies_file:
            cookies_path = Path(cookies_file)
            if cookies_path.exists():
                options['cookiefile'] = str(cookies_path)
                print(f"   🔐 Using cookies file: {cookies_path}")
            else:
                print(f"   ⚠️  YTDLP_COOKIES_FILE set but file not found: {cookies_file}")
        elif 'instagram' in url.lower():
            print("   ⚠️  Instagram download without cookies - may fail due to rate limits")
            print("   💡 Set YTDLP_COOKIES_FILE environment variable to use browser cookies")

        if username and password:
            options['username'] = username
            options['password'] = password
            print("   🔐 Using YTDLP_USERNAME / YTDLP_PASSWORD from environment")
        
        print(f"   🔧 Starting yt-dlp download...")
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"   ✅ yt-dlp extraction complete")
        except Exception as e:
            # Provide clearer guidance for common yt-dlp failures (login, rate limits)
            msg = str(e).lower()
            error_str = str(e)
            print(f"   ❌ yt-dlp error: {error_str}")

            # Check for common failure patterns
            needs_auth = any(keyword in msg for keyword in [
                'login required', 
                'requested content is not available',
                'rate-limit',
                'rate limit',
                'login page',
                'unable to extract',
                'main webpage is locked'
            ])

            if needs_auth:
                print("\n   ⚠️  DOWNLOAD BLOCKED - Authentication/Rate Limit Issue")
                print("   " + "="*60)
                
                if 'instagram' in url.lower():
                    print("   📱 INSTAGRAM SOLUTION:")
                    print("   1. Export cookies from your browser (use 'Get cookies.txt LOCALLY' extension)")
                    print("   2. Save as cookies.txt in project root or temp_videos/")
                    print("   3. Set environment: YTDLP_COOKIES_FILE=/path/to/cookies.txt")
                    print("\n   📚 Detailed Guide: See INSTAGRAM_COOKIES_GUIDE.md")
                else:
                    print("   🔐 AUTHENTICATION OPTIONS:")
                    print("   • Export browser cookies: YTDLP_COOKIES_FILE=/path/to/cookies.txt")
                    print("   • Use credentials: YTDLP_USERNAME and YTDLP_PASSWORD")
                    print("\n   📖 More info: https://github.com/yt-dlp/yt-dlp#cookies")
                
                print("   " + "="*60)

            raise
        
        if not info:
            raise ValueError("Failed to extract video information")
        
        # Extract metadata
        video_id = info.get('id', 'unknown')
        title = info.get('title', 'Untitled')
        description = info.get('description', '') or ''  # Original description
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
        if description:
            print(f"   📝 Description: {description[:100]}...")
        
        # Remove metadata from video
        print(f"   🧹 Removing metadata...")
        cleaned_filepath = self._remove_metadata(filepath)
        
        return VideoInfo(
            filepath=cleaned_filepath,
            title=title,
            platform=platform,
            duration=int(duration),
            size_mb=size_mb,
            description=description
        )
    
    def _remove_metadata(self, input_path: Path) -> Path:
        """
        Remove all metadata from video file using ffmpeg.
        
        Args:
            input_path: Path to video file with metadata
            
        Returns:
            Path to cleaned video file
            
        Raises:
            RuntimeError: If ffmpeg fails
        """
        output_path = input_path.with_stem(f"{input_path.stem}_clean")
        
        try:
            # Run ffmpeg to strip metadata
            # -map_metadata -1: Remove all metadata
            # -c:v copy: Copy video codec without re-encoding (fast)
            # -c:a copy: Copy audio codec without re-encoding (fast)
            # -fflags +bitexact: Remove encoder information
            # -loglevel error: Only show errors
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-map_metadata', '-1',
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-fflags', '+bitexact',
                '-loglevel', 'error',
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")
            
            # Remove original file and rename cleaned file
            input_path.unlink()
            output_path.rename(input_path)
            
            print(f"   ✅ Metadata removed successfully")
            return input_path
            
        except subprocess.TimeoutExpired:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError("ffmpeg timeout (30s)")
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found. Install with: sudo apt install ffmpeg")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"Failed to remove metadata: {e}")
    
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
