"""
Example: User-isolated storage for ideas/history.

This example shows how to implement per-user storage for features like:
- Video ideas
- Download history  
- User preferences
- Usage statistics

Each user (chat_id) gets their own isolated storage file.
"""

from pathlib import Path
from storage.ideas_storage import IdeasStorage
from config import config


class UserIsolatedStorage:
    """
    Manages per-user storage instances.
    
    Each chat_id gets:
    - Separate ideas file: temp_videos/ideas_{chat_id}.json
    - Separate history: temp_videos/history_{chat_id}.json
    - Isolated from other users
    """
    
    def __init__(self):
        self.storage_dir = config.TEMP_VIDEOS_DIR
        self._ideas_cache = {}  # Cache of IdeasStorage instances
    
    def get_ideas_storage(self, chat_id: str) -> IdeasStorage:
        """
        Get ideas storage for specific user.
        
        Args:
            chat_id: User's Telegram chat ID
            
        Returns:
            IdeasStorage instance for this user
        """
        if chat_id not in self._ideas_cache:
            storage_path = self.storage_dir / f"ideas_{chat_id}.json"
            self._ideas_cache[chat_id] = IdeasStorage(storage_path)
        
        return self._ideas_cache[chat_id]
    
    def get_history_file(self, chat_id: str) -> Path:
        """
        Get history file path for specific user.
        
        Args:
            chat_id: User's Telegram chat ID
            
        Returns:
            Path to user's history file
        """
        return self.storage_dir / f"history_{chat_id}.json"
    
    def get_preferences_file(self, chat_id: str) -> Path:
        """
        Get preferences file path for specific user.
        
        Args:
            chat_id: User's Telegram chat ID
            
        Returns:
            Path to user's preferences file
        """
        return self.storage_dir / f"preferences_{chat_id}.json"


# Example usage in bot
def example_bot_with_user_storage():
    """Example of using isolated storage in a bot."""
    
    from services.integrations.telegram_service import TelegramService
    
    # Initialize services
    telegram = TelegramService()
    storage_manager = UserIsolatedStorage()
    
    def handle_message(text: str, message_id: int, chat_id: str):
        """Handle incoming message with user-isolated storage."""
        
        # Get storage for THIS user only
        user_ideas = storage_manager.get_ideas_storage(chat_id)
        
        # Example: Save idea for this user
        if text.startswith("/idea "):
            idea_text = text[6:]  # Remove "/idea "
            
            # Save to THIS user's storage
            idea = user_ideas.create(
                title=f"Idea from user {chat_id}",
                description=idea_text,
                tags=["user_submitted"]
            )
            
            telegram.send_message(
                f"💡 Idea saved!\n\n"
                f"ID: {idea['id']}\n"
                f"Title: {idea['title']}\n\n"
                f"Only you can see this idea.",
                chat_id=chat_id
            )
        
        # Example: List THIS user's ideas
        elif text == "/myideas":
            ideas = user_ideas.list_all()
            
            if not ideas:
                telegram.send_message(
                    "📋 You don't have any saved ideas yet.\n\n"
                    "Use /idea <text> to save one!",
                    chat_id=chat_id
                )
            else:
                message = "📋 Your Ideas:\n\n"
                for idx, idea in enumerate(ideas, 1):
                    message += f"{idx}. {idea['title']}\n"
                
                telegram.send_message(message, chat_id=chat_id)
        
        # Other users' ideas are completely isolated
        # User A cannot see User B's ideas
    
    # Start listening
    telegram.listen_for_messages(handle_message)


# Example: Tracking download history per user
class DownloadHistory:
    """Track download history per user."""
    
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.history_file = config.TEMP_VIDEOS_DIR / f"history_{chat_id}.json"
        self._ensure_file()
    
    def _ensure_file(self):
        """Create history file if it doesn't exist."""
        if not self.history_file.exists():
            import json
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def add_download(self, url: str, platform: str, title: str):
        """Add download to user's history."""
        import json
        from datetime import datetime
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        history.append({
            'url': url,
            'platform': platform,
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'chat_id': self.chat_id
        })
        
        # Keep last 100 downloads
        history = history[-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_history(self, limit: int = 10):
        """Get user's recent downloads."""
        import json
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        return history[-limit:]
    
    def get_stats(self):
        """Get user's download statistics."""
        import json
        from collections import Counter
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        platforms = Counter(item['platform'] for item in history)
        
        return {
            'total_downloads': len(history),
            'platforms': dict(platforms),
            'most_used': platforms.most_common(1)[0] if platforms else None
        }


# Example: Enhanced bot with history tracking
def enhanced_bot_example():
    """Bot with per-user download history."""
    
    from services.integrations.telegram_service import TelegramService
    from services.downloads.video_downloader_service import VideoDownloaderService
    
    telegram = TelegramService()
    downloader = VideoDownloaderService()
    
    # Cache of DownloadHistory instances per user
    user_histories = {}
    
    def get_user_history(chat_id: str) -> DownloadHistory:
        """Get history tracker for user."""
        if chat_id not in user_histories:
            user_histories[chat_id] = DownloadHistory(chat_id)
        return user_histories[chat_id]
    
    def handle_message(text: str, message_id: int, chat_id: str):
        """Handle message with history tracking."""
        
        history = get_user_history(chat_id)
        
        # Stats command
        if text == "/stats":
            stats = history.get_stats()
            
            message = (
                f"📊 Your Statistics:\n\n"
                f"Total Downloads: {stats['total_downloads']}\n"
            )
            
            if stats['platforms']:
                message += "\nPlatforms:\n"
                for platform, count in stats['platforms'].items():
                    message += f"  • {platform}: {count}\n"
            
            telegram.send_message(message, chat_id=chat_id)
            return
        
        # History command
        if text == "/history":
            recent = history.get_history(limit=5)
            
            if not recent:
                telegram.send_message(
                    "📋 No download history yet!",
                    chat_id=chat_id
                )
                return
            
            message = "📋 Recent Downloads:\n\n"
            for item in recent:
                message += f"• {item['title'][:30]}...\n"
                message += f"  Platform: {item['platform']}\n\n"
            
            telegram.send_message(message, chat_id=chat_id)
            return
        
        # Download video
        if "http" in text:
            url = text
            
            telegram.send_message(
                "⬇️ Downloading...",
                chat_id=chat_id
            )
            
            video_info = downloader.download(url)
            
            if video_info:
                # Track download
                history.add_download(
                    url=url,
                    platform=video_info.platform,
                    title=video_info.title
                )
                
                # Send video
                telegram.send_video(
                    video_info.filepath,
                    caption=f"✅ {video_info.title}",
                    chat_id=chat_id
                )
    
    telegram.listen_for_messages(handle_message)


# Usage in production code:
"""
# In bots/link_downloader_bot.py

from user_isolated_storage import UserIsolatedStorage, DownloadHistory

class LinkDownloaderBot:
    def __init__(self):
        self.telegram = TelegramService()
        self.downloader = VideoDownloaderService()
        
        # Add storage manager
        self.storage = UserIsolatedStorage()
        self.user_histories = {}
    
    def get_user_history(self, chat_id: str) -> DownloadHistory:
        if chat_id not in self.user_histories:
            self.user_histories[chat_id] = DownloadHistory(chat_id)
        return self.user_histories[chat_id]
    
    def handle_message(self, text: str, message_id: int, chat_id: str):
        # Get user-specific storage
        history = self.get_user_history(chat_id)
        
        # Process message...
        video_info = self.downloader.download(url)
        
        if video_info:
            # Track in user's history
            history.add_download(url, video_info.platform, video_info.title)
            
            # Send to user
            self.telegram.send_video(
                video_info.filepath,
                caption="✅ Downloaded!",
                chat_id=chat_id  # Always pass chat_id
            )
"""

if __name__ == "__main__":
    print("This is an example file - see code for implementation patterns")
    print()
    print("Key concepts:")
    print("  1. Each user gets separate storage files")
    print("  2. Storage is accessed via chat_id")
    print("  3. No interference between users")
    print("  4. Easy to implement stats/history per user")
