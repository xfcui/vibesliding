"""PPT Slide Image Generator - generates slide images from markdown outlines via OpenRouter or Volcengine."""

from src.api_client import OpenRouterClient, VolcengineClient
from src.generator import SlideImageGenerator
from src.parser import Slide

__all__ = ["OpenRouterClient", "VolcengineClient", "SlideImageGenerator", "Slide"]
