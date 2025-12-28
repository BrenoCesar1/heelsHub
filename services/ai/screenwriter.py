"""
Script generation agent using Gemini AI.

This agent creates creative video scripts for AI-generated content, generating:
- Visual prompts (in English for Veo AI)
- Audio prompts (in Portuguese with São Paulo slang)
- Raw script summaries
"""

import json
import os
import re
import time
from typing import Any
from dataclasses import dataclass

import requests


@dataclass
class Script:
    """Represents a generated video script."""
    visual_prompt: str
    audio_prompt: str
    raw_script: str
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Script':
        """Create Script from dictionary response."""
        return cls(
            visual_prompt=data['visual_prompt'],
            audio_prompt=data['audio_prompt'],
            raw_script=data['raw_script']
        )
    
    def to_dict(self) -> dict[str, str]:
        """Convert Script to dictionary."""
        return {
            'visual_prompt': self.visual_prompt,
            'audio_prompt': self.audio_prompt,
            'raw_script': self.raw_script
        }


class Screenwriter:
    """
    AI-powered script generator for comedy videos.
    
    Uses Gemini AI to create engaging, humorous scripts for AI-generated
    content in everyday situations with a comedic twist.
    """
    
    # Character and universe definition
    SYSTEM_PROMPT = (
        "You are a prompt engineering expert for Google Veo 3.1 video generation. "
        "Create technical, structured prompts for AI-generated comedy videos.\n\n"
        "### UNIVERSE & CHARACTERS\n"
        "* **Character (Protagonist):** Capuchin monkey, charismatic 'maloqueiro' (street-smart). "
        "Wears black Ray-Ban sunglasses. Acts like a São Paulo periphery digital influencer.\n"
        "* **Setting:** Amazon rainforest treated as São Paulo 'quebrada' (neighborhood).\n\n"
        "### CRITICAL RULES\n"
        "1. **Language:** Technical prompts in ENGLISH. Dialogue in PORTUGUESE with São Paulo slang.\n"
        "2. **Safety:** NEVER describe weapons, drugs, or explicit violence.\n"
        "3. **Format:** VERTICAL 9:16 (smartphone portrait) for TikTok/Reels.\n"
        "4. Character does NOT sing/rap. He SPEAKS in comedic everyday situations."
    )
    
    # Example situations for variation (USE AS INSPIRATION ONLY - create original variations)
    SITUATION_EXAMPLES = [
        "Riding an armadillo like a motorcycle (making engine sounds, doing wheelies)",
        "Playing street football (acting like Real Madrid signed him)",
        "Hiding from loan shark Cleitin (owes bananas, whispering in fear)",
        "Taking Uber/99 (riding capybara, complaining about driver)",
        "Checking WhatsApp (looking at tree leaves like a phone)",
        "BBQ on rooftop (grilling chestnuts, calling friends)",
        "Counting money (stack of bananas, showing off)",
        "Complaining about property tax (jungle city hall charging bananas)"
    ]
    
    # API configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 60
    REQUEST_TIMEOUT = 60
    
    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        Initialize screenwriter with API credentials.
        
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
    
    def generate(self) -> dict[str, str]:
        """
        Generate a complete video script with automatic retry on rate limits.
        
        Returns:
            Dictionary with visual_prompt, audio_prompt, and raw_script
            
        Raises:
            RuntimeError: If all retries fail
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                return self._generate_script()
            except Exception as e:
                if self._is_rate_limit_error(e) and attempt < self.MAX_RETRIES - 1:
                    self._handle_retry(attempt)
                else:
                    raise
        
        raise RuntimeError(f"Script generation failed after {self.MAX_RETRIES} attempts")
    
    def generate_script(self) -> Script:
        """
        Generate a complete video script (returns Script object).
        
        Returns:
            Script object with visual_prompt, audio_prompt, and raw_script
            
        Raises:
            RuntimeError: If all retries fail
        """
        script_dict = self.generate()
        return Script.from_dict(script_dict)
    
    def enhance_user_idea(self, user_idea: str) -> Script:
        """
        Enhance user's video idea with AI and generate a complete script.
        
        Takes a user's simple idea and transforms it into a full production-ready
        script with detailed visual and audio prompts.
        
        Args:
            user_idea: User's video concept/idea
            
        Returns:
            Script object with enhanced prompts
            
        Raises:
            RuntimeError: If generation fails
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                prompt = self._build_idea_enhancement_prompt(user_idea)
                response = self._call_gemini_api(prompt)
                script_data = self._parse_response(response)
                self._validate_script(script_data)
                return Script.from_dict(script_data)
            except Exception as e:
                if self._is_rate_limit_error(e) and attempt < self.MAX_RETRIES - 1:
                    self._handle_retry(attempt)
                else:
                    raise
        
        raise RuntimeError(f"Idea enhancement failed after {self.MAX_RETRIES} attempts")
    
    def _generate_script(self) -> dict[str, str]:
        """Generate script by calling Gemini AI API."""
        prompt = self._build_prompt()
        response = self._call_gemini_api(prompt)
        script_data = self._parse_response(response)
        self._validate_script(script_data)
        
        return script_data
    
    def _build_prompt(self) -> str:
        """Build the complete prompt for Gemini."""
        situations = "\n".join(f"- {s}" for s in self.SITUATION_EXAMPLES)
        
        return (
            "Create a viral 8-second comedy script.\n\n"
            f"USE THESE AS INSPIRATION (create something ORIGINAL with similar style):\n{situations}\n\n"
            "⚠️ DO NOT copy examples - invent new funny situations keeping the same comedy style!\n\n"
            "RETURN ONLY THIS JSON (no markdown, single object):\n"
            "{\n"
            '  "visual_prompt": "IN ENGLISH - Detailed technical cinematographic description: '
            'Vertical 9:16 format. POV handheld selfie style. Close-up of capuchin monkey wearing black Ray-Ban sunglasses...",\n'
            '  "audio_prompt": "IN PORTUGUESE - Complete dialogue with São Paulo slang: '
            'Chama no grau família! Pega o ronco da XJ6! RANDANDANDAN!...",\n'
            '  "raw_script": "IN PORTUGUESE - Summary: Monkey rides armadillo like motorcycle..."\n'
            "}\n\n"
            "MANDATORY RULES:\n"
            "- visual_prompt: ENGLISH, very detailed, VERTICAL 9:16, camera style (POV/selfie/handheld)\n"
            "- audio_prompt: PORTUGUESE, complete dialogue with heavy São Paulo accent, urban slang\n"
            "- Character acts as street influencer, does NOT sing/rap\n"
            "- Use real Amazon animals (capybara, armadillo, jaguar, macaw) in urban situations\n"
            "- Combined visual + verbal humor\n"
            "- Return 1 JSON object only, not a list"
        )
    
    def _build_idea_enhancement_prompt(self, user_idea: str) -> str:
        """Build prompt for enhancing user's idea into a full script."""
        return (
            f"Transform this user idea into a viral 8-second comedy video script:\n\n"
            f"USER IDEA: {user_idea}\n\n"
            "Enhance and develop this idea following these guidelines:\n"
            "- Keep the core concept but make it more dynamic and visually interesting\n"
            "- Add specific camera angles and movements for vertical 9:16 format\n"
            "- Create engaging Portuguese dialogue with São Paulo slang\n"
            "- Make it funny and shareable\n\n"
            "RETURN ONLY THIS JSON (no markdown):\n"
            "{\n"
            '  "visual_prompt": "IN ENGLISH - Detailed cinematographic description: '
            'Vertical 9:16, camera style, lighting, actions...",\n'
            '  "audio_prompt": "IN PORTUGUESE - Complete dialogue with slang...",\n'
            '  "raw_script": "IN PORTUGUESE - Brief summary of the scene..."\n'
            "}\n\n"
            "MANDATORY RULES:\n"
            "- visual_prompt: ENGLISH, very detailed, VERTICAL 9:16 format\n"
            "- audio_prompt: PORTUGUESE with São Paulo slang\n"
            "- 8 seconds maximum duration\n"
            "- Return 1 JSON object only"
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
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json"
            }
        }
        
        print(f"   → Calling Gemini ({self.model})...")
        response = requests.post(
            url,
            json=payload,
            params={"key": self.api_key},
            timeout=self.REQUEST_TIMEOUT
        )
        
        if response.status_code == 429:
            self._print_rate_limit_message()
        
        response.raise_for_status()
        return response.json()
    
    def _parse_response(self, response: dict[str, Any]) -> dict[str, str]:
        """Extract and parse script data from API response."""
        text = self._extract_text_from_response(response)
        print(f"   → Response received ({len(text)} chars)")
        
        return self._parse_json(text)
    
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
    def _parse_json(text: str) -> dict[str, Any]:
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
        
        # Extract first JSON object
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise RuntimeError(f"Could not parse JSON from response: {text}")
    
    @staticmethod
    def _validate_script(data: dict[str, Any]) -> None:
        """Validate that script has all required fields."""
        required_keys = {"visual_prompt", "audio_prompt", "raw_script"}
        missing_keys = required_keys - set(data.keys())
        
        if missing_keys:
            raise RuntimeError(f"Script missing required keys: {missing_keys}. Got: {data}")
    
    @staticmethod
    def _is_rate_limit_error(error: Exception) -> bool:
        """Check if error is a rate limit (429) error."""
        return "429" in str(error)
    
    def _handle_retry(self, attempt: int) -> None:
        """Handle retry logic with delay."""
        print(f"\n⏳ Attempt {attempt + 1}/{self.MAX_RETRIES} failed (429 rate limit)")
        print(f"   Waiting {self.RETRY_DELAY_SECONDS}s before retry...")
        time.sleep(self.RETRY_DELAY_SECONDS)
        print(f"   🔄 Retrying (attempt {attempt + 2}/{self.MAX_RETRIES})...\n")
    
    @staticmethod
    def _print_rate_limit_message() -> None:
        """Print helpful message about rate limits."""
        print("\n" + "="*60)
        print("⚠️  RATE LIMIT REACHED - GEMINI API")
        print("="*60)
        print("Google AI Studio free tier has usage limits.")
        print("\n💡 SOLUTIONS:")
        print("  1️⃣  Wait 1-5 minutes and try again")
        print("  2️⃣  Use API key with higher quota")
        print("  3️⃣  Reduce generation frequency")
        print("="*60 + "\n")
