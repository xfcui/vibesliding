"""PPT Slide Image Generator - generates slide images from markdown outlines via OpenRouter or Volcengine."""

from src.compose.gen import SlideImageGenerator
from src.core.api_client import OpenRouterClient, VolcengineClient
from src.outline.parser import Slide

__all__ = ["OpenRouterClient", "VolcengineClient", "SlideImageGenerator", "Slide"]
