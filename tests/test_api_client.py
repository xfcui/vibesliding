import pytest
import httpx
from src.api_client import OpenRouterClient

@pytest.mark.asyncio
async def test_extract_image_success(client, mock_api_response, mock_image_bytes):
    image_bytes = client._extract_image(mock_api_response)
    assert image_bytes == mock_image_bytes

@pytest.mark.asyncio
async def test_extract_image_failure(client):
    with pytest.raises(ValueError, match="No choices in response"):
        client._extract_image({})

@pytest.mark.asyncio
async def test_generate_single_image_mocked(client, mock_api_response, mock_image_bytes, respx_mock):
    # Mock the API endpoint
    respx_mock.post(f"{client.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )
    
    async with httpx.AsyncClient() as http_client:
        result = await client._generate_single_image(
            http_client, 
            prompt="test prompt"
        )
    
    assert result == mock_image_bytes

@pytest.mark.asyncio
async def test_generate_images_parallel_mocked(client, mock_api_response, mock_image_bytes, respx_mock):
    # Mock the API endpoint for multiple calls
    respx_mock.post(f"{client.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )
    
    prompts = [
        ("prompt 1", None, None, None, None),
        ("prompt 2", None, None, None, None)
    ]
    
    results = await client.generate_images_parallel(prompts)
    
    assert len(results) == 2
    assert all(r == mock_image_bytes for r in results)
