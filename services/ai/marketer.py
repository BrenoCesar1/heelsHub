"""
Marketing metadata generation agent using Gemini AI.

This agent creates viral titles and hashtags for videos
optimized for TikTok, Instagram Reels, and YouTube Shorts.
Supports video analysis via Gemini File API.
"""

import json
import os
import re
import time
import mimetypes
from pathlib import Path
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
        "Você é especialista em marketing viral para TikTok no Brasil. "
        "Crie títulos CHAMATIVOS com gírias de São Paulo (mano, mina, rolê) "
        "e hashtags HIGH-REACH para vídeos engraçados de animais. "
        "Seja criativo, use humor brasileiro, e foque em viralizar!"
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
    
    def generate_from_video(self, video_path: str) -> dict[str, Any]:
        """
        Generate viral metadata by ANALYZING the video content.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with 'title' and 'hashtags' keys
        """
        print(f"   🎥 Analyzing video: {Path(video_path).name}")
        
        # 1. Upload video to Gemini File API
        file_uri = self._upload_video(video_path)
        
        # 2. Wait for processing
        self._wait_for_processing(file_uri)
        
        # 3. Generate metadata from video
        prompt = self._build_video_prompt()
        response = self._call_gemini_with_video(prompt, file_uri)
        metadata = self._parse_response(response)
        self._validate_metadata(metadata)
        
        return metadata
    
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
            f"Analise este vídeo e crie metadata VIRAL:\n\n"
            f"CONTEXTO DO VÍDEO:\n{script}\n\n"
            "INSTRUÇÕES:\n"
            "1. Título: Crie um título CLICKBAIT em português BR (máx 50 caracteres)\n"
            "   - Use gírias de SP: mano, bicho, cara, mina, rolê, parada, etc\n"
            "   - Seja engraçado e chamativo!\n"
            "2. Hashtags: 5 hashtags HIGH-REACH relacionadas ao conteúdo\n"
            "   - Misture: específicas (#bicho, #animal) + gerais (#humor, #viral)\n"
            "   - Evite repetir palavras do título\n\n"
            "RESPONDA APENAS COM JSON (sem markdown, sem texto extra):\n"
            '{"title": "seu título aqui", "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]}\n\n'
            "EXEMPLO VÁLIDO:\n"
            '{"title": "Bicho ladrão rouba até doguinho kkkk", "hashtags": ["#animais", "#humor", "#roubado", "#viral", "#pets"]}'
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
    
    def _upload_video(self, video_path: str) -> str:
        """Upload video to Gemini File API and return file URI."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(video_path)
        if not mime_type or not mime_type.startswith('video/'):
            mime_type = 'video/mp4'
        
        print(f"   ⬆️  Uploading video to Gemini...")
        
        url = f"{self._base_url}/files"
        
        with open(video_path, 'rb') as video_file:
            files = {
                'file': (Path(video_path).name, video_file, mime_type)
            }
            response = requests.post(
                url,
                files=files,
                params={'key': self.api_key},
                timeout=180
            )
        
        response.raise_for_status()
        data = response.json()
        file_uri = data['file']['uri']
        print(f"   ✅ Video uploaded: {file_uri}")
        return file_uri
    
    def _wait_for_processing(self, file_uri: str) -> None:
        """Wait for video processing to complete."""
        file_name = file_uri.split('/')[-1]
        url = f"{self._base_url}/files/{file_name}"
        
        print(f"   ⏳ Processing video...")
        for _ in range(30):  # Max 30 seconds
            response = requests.get(url, params={'key': self.api_key}, timeout=30)
            response.raise_for_status()
            
            state = response.json().get('file', {}).get('state')
            if state == 'ACTIVE':
                print(f"   ✅ Video ready for analysis")
                return
            
            time.sleep(1)
        
        raise RuntimeError("Video processing timeout")
    
    def _build_video_prompt(self) -> str:
        """Build prompt for video analysis."""
        return (
            "Assista este vídeo e crie metadata VIRAL para TikTok:\n\n"
            "INSTRUÇÕES:\n"
            "1. ASSISTA O VÍDEO e entenda o conteúdo\n"
            "2. Título: Crie um título CLICKBAIT em português BR (máx 50 caracteres)\n"
            "   - Use gírias de SP: mano, bicho, cara, mina, parada\n"
            "   - Seja engraçado e relacionado ao conteúdo!\n"
            "3. Hashtags: 5 hashtags HIGH-REACH baseadas no que você VIU\n"
            "   - Misture específicas + gerais (#humor, #viral)\n\n"
            "RESPONDA APENAS COM JSON:\n"
            '{"title": "título baseado no vídeo", "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]}'
        )
    
    def _call_gemini_with_video(self, prompt: str, file_uri: str) -> dict[str, Any]:
        """Call Gemini API with video file."""
        url = f"{self._base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [
                    {"text": f"{self.SYSTEM_PROMPT}\n\n{prompt}"},
                    {"fileData": {"fileUri": file_uri, "mimeType": "video/mp4"}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 256,
                "responseMimeType": "application/json"
            }
        }
        
        print(f"   🤖 Gemini analyzing video...")
        response = requests.post(
            url,
            json=payload,
            params={"key": self.api_key},
            timeout=120
        )
        
        response.raise_for_status()
        return response.json()
    
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
