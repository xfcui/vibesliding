import base64
import json
import pytest
from src.api_client import OpenRouterClient

@pytest.fixture
def mock_image_bytes():
    return b"fake-image-bytes"

@pytest.fixture
def mock_api_response(mock_image_bytes):
    b64_data = base64.b64encode(mock_image_bytes).decode("ascii")
    return {
        "choices": [
            {
                "message": {
                    "images": [
                        {
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_data}"
                            }
                        }
                    ]
                }
            }
        ]
    }

@pytest.fixture
def client():
    return OpenRouterClient(api_key="fake-key")
