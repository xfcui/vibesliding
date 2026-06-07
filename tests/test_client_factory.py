"""Tests for API client factory helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.api_client import OpenRouterClient, VolcengineClient
from src.core.client_factory import (
    create_image_client,
    create_text_client,
    normalize_provider,
    provider_label,
)
from src.core.config import Config


def _openrouter_config() -> Config:
    return Config(
        provider="openrouter",
        api_key="sk-test",
        proxy="socks5://127.0.0.1:1080",
        model="google/test-model",
        max_concurrent=4,
        output_dir=Path("out"),
        openrouter_management_api_key="mgmt-key",
    )


def _volcengine_config() -> Config:
    return Config(
        provider="volcengine",
        api_key="ark-test",
        proxy=None,
        model="doubao-seedream",
        max_concurrent=2,
        output_dir=Path("out"),
        volcengine_base_url="https://ark.example/v1",
        volcengine_image_size="1K",
        volcengine_response_format="b64_json",
        volcengine_watermark=False,
        volcengine_proxy="http://proxy:8080",
    )


def test_create_image_client_openrouter() -> None:
    client = create_image_client(_openrouter_config())
    assert isinstance(client, OpenRouterClient)
    assert client.api_key == "sk-test"
    assert client._proxy == "socks5://127.0.0.1:1080"
    assert client._model == "google/test-model"
    assert client.max_concurrent == 4
    assert client._management_api_key == "mgmt-key"


def test_create_image_client_volcengine() -> None:
    client = create_image_client(_volcengine_config())
    assert isinstance(client, VolcengineClient)
    assert client.api_key == "ark-test"
    assert client._model == "doubao-seedream"
    assert client._base_url == "https://ark.example/v1"
    assert client._image_size == "1K"
    assert client._response_format == "b64_json"
    assert client._watermark is False
    assert client._proxy == "http://proxy:8080"


def test_create_text_client() -> None:
    client = create_text_client(
        api_key="sk-text",
        proxy=None,
        model="anthropic/claude",
        max_concurrent=3,
        management_api_key="mgmt",
    )
    assert isinstance(client, OpenRouterClient)
    assert client.api_key == "sk-text"
    assert client._model == "anthropic/claude"
    assert client.max_concurrent == 3


def test_normalize_provider() -> None:
    assert normalize_provider(None) is None
    assert normalize_provider("OpenRouter") == "openrouter"
    assert normalize_provider("VOLCENGINE") == "volcengine"


def test_normalize_provider_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid provider"):
        normalize_provider("azure")


def test_provider_label() -> None:
    assert provider_label(OpenRouterClient(api_key="k")) == "openrouter"
    assert provider_label(
        VolcengineClient(api_key="k", model="m", max_concurrent=1)
    ) == "volcengine"
