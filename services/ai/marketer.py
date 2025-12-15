"""
Marketing metadata generation agent using Gemini AI.

This agent creates viral titles and hashtags for MC Macaco videos
optimized for TikTok, Instagram Reels, and YouTube Shorts.
"""

import json
import os
import re
from typing import Any
from dataclasses import dataclass

import requests


@dataclass
class MarketingMetadata:
    """Represents marketing metadata for a video."""
    title: str
    hashtags: list[str]
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'MarketingMetadata':
        """Create MarketingMetadata from dictionary response."""
        return cls(
            title=data['title'],
            hashtags=data['hashtags']
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'hashtags': self.hashtags
        }


class Marketer:
    """
    AI-powered marketing metadata generator for viral videos.
    
    Creates clickbait titles and high-reach hashtags tailored to
    Brazilian humor/animal content niche with São Paulo slang.
    """
    
    SYSTEM_PROMPT = (
        "You are a viral marketing strategist for short-form video content. "
        "Create clickbait titles (max 50 characters) and high-reach hashtags "
        "for the humor/animals niche, using São Paulo slang when appropriate."
    )
    
    MAX_TITLE_LENGTH = 50
    EXPECTED_HASHTAG_COUNT = 5
    
    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        Initialize marketer with API credentials.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to GEMINI_MODEL env var or gemini-2.0-flash)
            
        Raises:
            ValueError: If API key is not provided
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Add it to .env file")
        
        self._base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    def generate(self, script: str) -> dict[str, Any]:
        """
        Generate viral marketing metadata from a script.
        
        Args:
            script: The video script content
            
        Returns:
            Dictionary with 'title' and 'hashtags' keys
            
        Raises:
            ValueError: If script is empty
            RuntimeError: If generation fails or response is invalid
        """
        if not script:
            raise ValueError("Script is required for marketing metadata generation")
        
        prompt = self._build_prompt(script)
        response = self._call_gemini_api(prompt)
        metadata = self._parse_response(response)
        self._validate_metadata(metadata)
        
        return metadata
    
    def _build_prompt(self, script: str) -> str:
        """Build the complete prompt for Gemini."""
        return (
            f"Based on the script below, generate viral metadata for TikTok/Shorts.\n\n"
            f"SCRIPT:\n{script}\n\n"
            "Respond ONLY with a valid JSON object (no extra text, no markdown).\n"
            "The JSON must have exactly these 2 keys:\n"
            "- title: clickbait title with max 50 characters\n"
            "- hashtags: list of 5 hashtags (strings starting with #)\n\n"
            "Example valid response:\n"
            '{"title": "MC Macaco na selva de pedra", "hashtags": ["#mcmacaco", "#humor", "#selva", "#viral", "#chave"]}'
        )
    
    def _call_gemini_api(self, prompt: str) -> dict[str, Any]:
        """Call Gemini API with the prompt."""
        url = f"{self._base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": f"{self.SYSTEM_PROMPT}\n\n{prompt}"}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 256,
                "responseMimeType": "application/json"
            }
        }
        
        print(f"   → Calling Gemini ({self.model})...")
        response = requests.post(
            url,
            json=payload,
            params={"key": self.api_key},
            timeout=60
        )
        
        response.raise_for_status()
        return response.json()
    
    def _parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Extract and parse metadata from API response."""
        text = self._extract_text_from_response(response)
        print(f"   → Response received ({len(text)} chars)")
        
        data = self._parse_json(text)
        
        # Handle case where API returns list of candidates
        if isinstance(data, list):
            data = self._select_best_candidate(data)
        
        return data
    
    @staticmethod
    def _extract_text_from_response(response: dict[str, Any]) -> str:
        """Extract text from Gemini response structure."""
        try:
            candidates = response["candidates"]
            content = candidates[0]["content"]
            parts = content["parts"]
            return parts[0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response format: {response}") from e
    
    @staticmethod
    def _parse_json(text: str) -> dict[str, Any] | list[dict[str, Any]]:
        """Parse JSON from text with fallback strategies."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Remove markdown code fences
        cleaned = re.sub(r"```json\s*|```\s*", "", text, flags=re.IGNORECASE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Extract first JSON structure (object or array)
        match = re.search(r"[\[{][\s\S]*[\]}]", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise RuntimeError(f"Could not parse JSON from response: {text}")
    
    @staticmethod
    def _select_best_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
        """Select the best candidate from a list of options."""
        for candidate in candidates:
            if isinstance(candidate, dict) and "title" in candidate and "hashtags" in candidate:
                return candidate
        
        raise RuntimeError(f"No valid candidate found in list: {candidates}")
    
    def _validate_metadata(self, data: dict[str, Any]) -> None:
        """Validate marketing metadata structure and content."""
        # Check required fields
        if not isinstance(data, dict):
            raise RuntimeError(f"Metadata must be a dict, got: {type(data)}")
        
        if "title" not in data or "hashtags" not in data:
            raise RuntimeError(f"Metadata missing title or hashtags: {data}")
        
        # Validate title
        if not isinstance(data["title"], str):
            raise RuntimeError(f"Title must be string, got: {type(data['title'])}")
        
        if len(data["title"]) > self.MAX_TITLE_LENGTH:
            print(f"⚠️  Warning: Title exceeds {self.MAX_TITLE_LENGTH} chars: {data['title']}")
        
        # Validate hashtags
        if not isinstance(data["hashtags"], list):
            raise RuntimeError(f"Hashtags must be list, got: {type(data['hashtags'])}")
        
        if not all(isinstance(tag, str) for tag in data["hashtags"]):
            raise RuntimeError(f"All hashtags must be strings: {data['hashtags']}")
        
        # Ensure hashtags start with #
        data["hashtags"] = [
            tag if tag.startswith("#") else f"#{tag}"
            for tag in data["hashtags"]
        ]
