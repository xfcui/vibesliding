import base64
import pytest
from src.core.api_client import OpenRouterClient

@pytest.fixture
def mock_image_bytes():
    return b"fake-image-bytes"

@pytest.fixture
def mock_api_response(mock_image_bytes):
    """OpenRouter unified Image API response (POST /images)."""
    b64_data = base64.b64encode(mock_image_bytes).decode("ascii")
    return {
        "data": [{"b64_json": b64_data, "media_type": "image/png"}],
        "usage": {"total_tokens": 335, "cost": 0.0087},
    }

@pytest.fixture
def client():
    return OpenRouterClient(
        api_key="fake-key",
        supported_parameters=frozenset(
            {"aspect_ratio", "resolution", "n", "input_references"}
        ),
    )
