"""Factory for image API clients used by slide and style-reference generation."""

from __future__ import annotations

from src.core.api_client import OpenRouterClient, VolcengineClient
from src.core.config import Config, Provider


def create_image_client(config: Config) -> OpenRouterClient | VolcengineClient:
    """Build an image client from resolved slide-generation config."""
    assert config.api_key is not None
    if config.provider == "volcengine":
        return VolcengineClient(
            api_key=config.api_key,
            model=config.model,
            max_concurrent=config.max_concurrent,
            base_url=config.volcengine_base_url,
            image_size=config.volcengine_image_size,
            response_format=config.volcengine_response_format,
            watermark=config.volcengine_watermark,
            proxy=config.volcengine_proxy,
        )
    return OpenRouterClient(
        api_key=config.api_key,
        proxy=config.proxy,
        model=config.model,
        max_concurrent=config.max_concurrent,
        management_api_key=config.openrouter_management_api_key,
    )


def provider_label(client: OpenRouterClient | VolcengineClient) -> str:
    return "volcengine" if isinstance(client, VolcengineClient) else "openrouter"


def normalize_provider(provider: str | None) -> Provider | None:
    if provider is None:
        return None
    normalized = provider.strip().lower()
    if normalized not in ("openrouter", "volcengine"):
        raise ValueError(f"Invalid provider {provider!r}. Use openrouter or volcengine.")
    return normalized  # type: ignore[return-value]


def create_text_client(
    *,
    api_key: str,
    proxy: str | None,
    model: str,
    max_concurrent: int,
    management_api_key: str | None = None,
) -> OpenRouterClient:
    return OpenRouterClient(
        api_key=api_key,
        proxy=proxy,
        model=model,
        max_concurrent=max_concurrent,
        management_api_key=management_api_key,
    )
