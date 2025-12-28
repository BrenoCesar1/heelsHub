"""
JSON-based storage for video ideas.

Provides persistent storage for user-submitted video ideas that can be used
for multiple video generations.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from threading import Lock

import config


class IdeasStorage:
    """Thread-safe JSON storage for video ideas."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize ideas storage.
        
        Args:
            storage_path: Path to JSON file. Defaults to {TEMP_VIDEOS_DIR}/ideas.json
        """
        self.storage_path = storage_path or config.TEMP_VIDEOS_DIR / "ideas.json"
        self._lock = Lock()
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """Create storage file if it doesn't exist."""
        if not self.storage_path.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_data([])
    
    def _read_data(self) -> List[Dict[str, Any]]:
        """Read all ideas from storage."""
        with self._lock:
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
    
    def _write_data(self, data: List[Dict[str, Any]]) -> None:
        """Write ideas to storage."""
        with self._lock:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create(self, title: str, description: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new idea.
        
        Args:
            title: Idea title
            description: Detailed description
            tags: Optional list of tags
            
        Returns:
            Created idea with generated ID
        """
        ideas = self._read_data()
        
        now = datetime.now().isoformat()
        idea = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': description,
            'tags': tags or [],
            'created_at': now,
            'updated_at': now,
            'videos_generated': 0
        }
        
        ideas.append(idea)
        self._write_data(ideas)
        
        return idea
    
    def get(self, idea_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an idea by ID.
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            Idea dict or None if not found
        """
        ideas = self._read_data()
        return next((idea for idea in ideas if idea['id'] == idea_id), None)
    
    def list_all(self) -> List[Dict[str, Any]]:
        """
        Get all ideas.
        
        Returns:
            List of all ideas, sorted by creation date (newest first)
        """
        ideas = self._read_data()
        return sorted(ideas, key=lambda x: x['created_at'], reverse=True)
    
    def update(self, idea_id: str, title: Optional[str] = None, 
               description: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Update an existing idea.
        
        Args:
            idea_id: Idea identifier
            title: New title (if provided)
            description: New description (if provided)
            tags: New tags (if provided)
            
        Returns:
            Updated idea or None if not found
        """
        ideas = self._read_data()
        
        for idea in ideas:
            if idea['id'] == idea_id:
                if title is not None:
                    idea['title'] = title
                if description is not None:
                    idea['description'] = description
                if tags is not None:
                    idea['tags'] = tags
                idea['updated_at'] = datetime.now().isoformat()
                
                self._write_data(ideas)
                return idea
        
        return None
    
    def delete(self, idea_id: str) -> bool:
        """
        Delete an idea.
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            True if deleted, False if not found
        """
        ideas = self._read_data()
        initial_count = len(ideas)
        
        ideas = [idea for idea in ideas if idea['id'] != idea_id]
        
        if len(ideas) < initial_count:
            self._write_data(ideas)
            return True
        
        return False
    
    def increment_video_count(self, idea_id: str) -> None:
        """
        Increment the video generation counter for an idea.
        
        Args:
            idea_id: Idea identifier
        """
        ideas = self._read_data()
        
        for idea in ideas:
            if idea['id'] == idea_id:
                idea['videos_generated'] = idea.get('videos_generated', 0) + 1
                self._write_data(ideas)
                break
    
    def get_random(self) -> Optional[Dict[str, Any]]:
        """
        Get a random idea for automated generation.
        
        Returns:
            Random idea or None if no ideas exist
        """
        import random
        ideas = self._read_data()
        return random.choice(ideas) if ideas else None
