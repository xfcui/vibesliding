import pytest
import httpx
from src.api_client import OpenRouterClient, VolcengineClient

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
    respx_mock.post(f"{client.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )
    prompts = [
        ("prompt 1", None, None, None, None),
        ("prompt 2", None, None, None, None),
    ]
    results = await client.generate_images_parallel(prompts)
    assert len(results) == 2
    assert all(r == mock_image_bytes for r in results)

@pytest.mark.asyncio
async def test_volcengine_generate_single_image_mocked(mock_image_bytes, respx_mock):
    import base64 as b64mod
    client = VolcengineClient(
        api_key="fake",
        model="doubao-seedream-5-0-260128",
        response_format="b64_json",
    )
    payload_b64 = b64mod.b64encode(mock_image_bytes).decode("ascii")
    respx_mock.post(f"{client._base_url}/images/generations").mock(
        return_value=httpx.Response(200, json={"data": [{"b64_json": payload_b64}]})
    )
    async with httpx.AsyncClient() as http_client:
        result = await client._generate_single_image(http_client, prompt="hello")
    assert result == mock_image_bytes


@pytest.mark.asyncio
async def test_volcengine_parallel_mocked(mock_image_bytes, respx_mock):
    import base64 as b64mod
    client = VolcengineClient(api_key="fake", model="m", response_format="b64_json")
    payload_b64 = b64mod.b64encode(mock_image_bytes).decode("ascii")
    respx_mock.post(f"{client._base_url}/images/generations").mock(
        return_value=httpx.Response(200, json={"data": [{"b64_json": payload_b64}]})
    )
    prompts = [("a", None, None, None, None), ("b", None, None, None, None)]
    results = await client.generate_images_parallel(prompts)
    assert len(results) == 2
    assert all(r == mock_image_bytes for r in results)


def test_volcengine_data_url_jpeg_magic_bytes() -> None:
    blob = b"\xff\xd8\xff\xe0\x00\x10JFIFfake"
    url = VolcengineClient._data_url_for_image(blob)
    assert url.startswith("data:image/jpeg;base64,")


@pytest.mark.asyncio
async def test_volcengine_image_to_image_includes_image_field(mock_image_bytes, respx_mock):
    import base64 as b64mod
    import json

    captured: dict[str, object] = {}

    def on_request(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        out_b64 = b64mod.b64encode(mock_image_bytes).decode("ascii")
        return httpx.Response(200, json={"data": [{"b64_json": out_b64}]})

    client = VolcengineClient(
        api_key="fake",
        model="doubao-seedream-5-0-260128",
        response_format="b64_json",
    )
    respx_mock.post(f"{client._base_url}/images/generations").mock(side_effect=on_request)
    async with httpx.AsyncClient() as http_client:
        await client._generate_single_image(
            http_client, "prompt", reference_image=mock_image_bytes
        )
    body = captured["body"]
    assert isinstance(body, dict)
    assert "image" in body
    img_list = body["image"]
    assert isinstance(img_list, list) and len(img_list) == 1
    assert isinstance(img_list[0], str)
    assert img_list[0].startswith("data:image/png;base64,")
