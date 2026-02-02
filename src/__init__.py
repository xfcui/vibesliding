"""PPT Slide Image Generator - generates slide images from markdown outlines via OpenRouter API."""

from src.api_client import OpenRouterClient
from src.generator import SlideImageGenerator
from src.parser import Slide

__all__ = ["OpenRouterClient", "SlideImageGenerator", "Slide"]
