"""
Synthia Media Generation Service - The Pauli Effect

Integrates top image and video generators:
- Nano Banana (nanobanana.ai) - AI image generation
- Midjourney - High-quality image generation
- DALL-E 3 - OpenAI image generation
- RunwayML - AI video generation
- Pika Labs - Video generation
"""

import os
import asyncio
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import base64
import io


class ImageProvider(str, Enum):
    NANO_BANANA = "nano_banana"
    MIDJOURNEY = "midjourney"
    DALLE = "dalle"
    STABLE_DIFFUSION = "stable_diffusion"


class VideoProvider(str, Enum):
    RUNWAY_ML = "runway_ml"
    PIKA_LABS = "pika_labs"
    HEYGEN = "heygen"


@dataclass
class GeneratedImage:
    url: str
    provider: str
    prompt: str
    local_path: Optional[str] = None
    base64_data: Optional[str] = None


@dataclass
class GeneratedVideo:
    url: str
    provider: str
    prompt: str
    duration: int = 4  # seconds
    status: str = "completed"


class MediaGenerationService:
    """
    Synthia's Media Generation Service for The Pauli Effect.
    Handles image and video generation across multiple providers.
    """
    
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.midjourney_api_key = os.getenv("MIDJOURNEY_API_KEY")
        self.runway_api_key = os.getenv("RUNWAY_API_KEY")
        self.pika_api_key = os.getenv("PIKA_API_KEY")
        self.nano_banana_api_key = os.getenv("NANO_BANANA_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.heygen_api_key = os.getenv("HEY_GEN_API")
        
    # ═══════════════════════════════════════════════════════════════
    # IMAGE GENERATION
    # ═══════════════════════════════════════════════════════════════
    
    async def generate_image_nano_banana(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: Optional[str] = None
    ) -> GeneratedImage:
        """
        Generate image using Nano Banana (nanobanana.ai)
        Nano Banana is known for artistic and creative image generation.
        """
        if not self.nano_banana_api_key:
            raise ValueError("NANO_BANANA_API_KEY not configured")
        
        url = "https://api.nanobanana.ai/v1/generate"
        
        headers = {
            "Authorization": f"Bearer {self.nano_banana_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "style": style or "photorealistic",
            "num_images": 1,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return GeneratedImage(
                url=data["images"][0]["url"],
                provider="nano_banana",
                prompt=prompt
            )
    
    async def generate_image_dalle(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid"
    ) -> GeneratedImage:
        """
        Generate image using DALL-E 3 (OpenAI)
        Best for detailed, accurate image generation.
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "style": style,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return GeneratedImage(
                url=data["data"][0]["url"],
                provider="dalle",
                prompt=prompt
            )
    
    async def generate_image_stable_diffusion(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0
    ) -> GeneratedImage:
        """
        Generate image using Stability AI (Stable Diffusion XL)
        Great for customization and control.
        """
        if not self.stability_api_key:
            raise ValueError("STABILITY_API_KEY not configured")
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": cfg_scale,
            "samples": 1,
            "steps": steps,
            "width": width,
            "height": height,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Stability returns base64
            image_data = data["artifacts"][0]["base64"]
            
            return GeneratedImage(
                url="",  # Base64 only
                provider="stable_diffusion",
                prompt=prompt,
                base64_data=image_data
            )
    
    async def generate_image(
        self,
        prompt: str,
        provider: ImageProvider = ImageProvider.DALLE,
        **kwargs
    ) -> GeneratedImage:
        """
        Generate image using specified provider.
        Synthia intelligently selects the best provider for the task.
        """
        if provider == ImageProvider.NANO_BANANA:
            return await self.generate_image_nano_banana(prompt, **kwargs)
        elif provider == ImageProvider.DALLE:
            return await self.generate_image_dalle(prompt, **kwargs)
        elif provider == ImageProvider.STABLE_DIFFUSION:
            return await self.generate_image_stable_diffusion(prompt, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    # ═══════════════════════════════════════════════════════════════
    # VIDEO GENERATION
    # ═══════════════════════════════════════════════════════════════
    
    async def generate_video_runway(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 4,
        motion_scale: float = 1.0
    ) -> GeneratedVideo:
        """
        Generate video using RunwayML Gen-2
        Industry-leading AI video generation.
        """
        if not self.runway_api_key:
            raise ValueError("RUNWAY_API_KEY not configured")
        
        url = "https://api.runwayml.com/v1/generations"
        
        headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text_prompt": prompt,
            "duration": duration,
            "motion_scale": motion_scale,
        }
        
        if image_url:
            payload["image_url"] = image_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return GeneratedVideo(
                url=data.get("url", ""),
                provider="runway_ml",
                prompt=prompt,
                duration=duration,
                status="processing"
            )
    
    async def generate_video_pika(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 3,
        guidance_scale: float = 12.0
    ) -> GeneratedVideo:
        """
        Generate video using Pika Labs
        Fast, creative video generation.
        """
        if not self.pika_api_key:
            raise ValueError("PIKA_API_KEY not configured")
        
        url = "https://api.pika.art/v1/generations"
        
        headers = {
            "Authorization": f"Bearer {self.pika_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "prompt": prompt,
            "duration": duration,
            "guidance_scale": guidance_scale,
        }
        
        if image_url:
            payload["image_url"] = image_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return GeneratedVideo(
                url=data.get("url", ""),
                provider="pika_labs",
                prompt=prompt,
                duration=duration,
                status="processing"
            )
    
    async def generate_video(
        self,
        prompt: str,
        provider: VideoProvider = VideoProvider.RUNWAY_ML,
        **kwargs
    ) -> GeneratedVideo:
        """
        Generate video using specified provider.
        """
        if provider == VideoProvider.RUNWAY_ML:
            return await self.generate_video_runway(prompt, **kwargs)
        elif provider == VideoProvider.PIKA_LABS:
            return await self.generate_video_pika(prompt, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    # ═══════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════
    
    async def download_image(self, url: str, save_path: str) -> str:
        """Download image from URL to local path."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            return save_path
    
    def save_base64_image(self, base64_data: str, save_path: str) -> str:
        """Save base64 image data to file."""
        image_data = base64.b64decode(base64_data)
        with open(save_path, "wb") as f:
            f.write(image_data)
        return save_path


# Singleton instance
_media_service: Optional[MediaGenerationService] = None


def get_media_service() -> MediaGenerationService:
    """Get or create media generation service singleton."""
    global _media_service
    if _media_service is None:
        _media_service = MediaGenerationService()
    return _media_service
