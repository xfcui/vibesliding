from __future__ import annotations

import json

import pytest
import httpx
from src.core.api_client import (
    OPENROUTER_IMAGE_PROMPT_MAX_CHARS,
    OpenRouterClient,
    VolcengineClient,
    _credits_timeout,
    _http_error_detail,
    _image_timeout,
    _is_retryable_exception,
    _merge_prompt_parts,
    _supported_parameter_names,
)


def _status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://example.test/images")
    response = httpx.Response(status_code, request=request)
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        response.raise_for_status()
    return exc_info.value


def test_image_timeout_uses_phase_specific_budget() -> None:
    timeout = _image_timeout()
    assert timeout.connect == 30.0
    assert timeout.read == 300.0
    assert timeout.write == 60.0
    assert timeout.pool == 30.0


def test_credits_timeout_keeps_short_read_budget() -> None:
    timeout = _credits_timeout()
    assert timeout.connect == 10.0
    assert timeout.read == 30.0
    assert timeout.write == 30.0
    assert timeout.pool == 10.0


def test_retry_predicate_skips_permanent_http_errors() -> None:
    assert not _is_retryable_exception(_status_error(400))
    assert not _is_retryable_exception(_status_error(401))
    assert not _is_retryable_exception(_status_error(403))
    assert _is_retryable_exception(_status_error(429))
    assert _is_retryable_exception(_status_error(500))
    assert _is_retryable_exception(httpx.ConnectError("connect failed"))
    assert _is_retryable_exception(httpx.ReadTimeout("read timed out"))

@pytest.mark.asyncio
async def test_extract_text_success(client) -> None:
    data = {"choices": [{"message": {"content": "  hello outline  "}}]}
    assert client._extract_text(data) == "hello outline"


@pytest.mark.asyncio
async def test_extract_text_failure(client) -> None:
    with pytest.raises(ValueError, match="No text content"):
        client._extract_text({"choices": [{"message": {"content": ""}}]})


@pytest.mark.asyncio
async def test_complete_text_mocked(client, respx_mock) -> None:
    respx_mock.post(f"{client.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "outline markdown"}}]},
        )
    )
    result = await client.complete_text("write outline", "system rules")
    assert result == "outline markdown"


@pytest.mark.asyncio
async def test_complete_text_parallel_mocked(client, respx_mock) -> None:
    respx_mock.post(f"{client.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "outline markdown"}}]},
        )
    )
    prompts = [("outline 16", "system"), ("outline 25", "system")]
    results = await client.complete_text_parallel(prompts, desc="Outlines")
    assert len(results) == 2
    assert all(result == "outline markdown" for result in results)


@pytest.mark.asyncio
async def test_extract_image_success(client, mock_api_response, mock_image_bytes):
    image_bytes = client._extract_image(mock_api_response)
    assert image_bytes == mock_image_bytes

@pytest.mark.asyncio
async def test_extract_image_failure(client):
    with pytest.raises(ValueError, match="No images in response"):
        client._extract_image({})

@pytest.mark.asyncio
async def test_generate_single_image_mocked(client, mock_api_response, mock_image_bytes, respx_mock):
    # Mock the unified Image API endpoint
    route = respx_mock.post(f"{client.BASE_URL}/images").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )

    async with httpx.AsyncClient() as http_client:
        result = await client._generate_single_image(
            http_client,
            prompt="test prompt",
            system_prompt="system rules",
            image_size="1K",
        )

    assert result == mock_image_bytes
    sent = json.loads(route.calls[0].request.content)
    assert sent["prompt"] == "system rules\n\ntest prompt"
    assert sent["aspect_ratio"] == "16:9"
    assert sent["resolution"] == "1K"
    assert sent["n"] == 1
    assert "input_references" not in sent


@pytest.mark.asyncio
async def test_generate_single_image_sends_reference_images(
    client, mock_api_response, mock_image_bytes, respx_mock
):
    route = respx_mock.post(f"{client.BASE_URL}/images").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )

    async with httpx.AsyncClient() as http_client:
        await client._generate_single_image(
            http_client,
            prompt="test prompt",
            reference_images=[mock_image_bytes, mock_image_bytes],
        )

    sent = json.loads(route.calls[0].request.content)
    refs = sent["input_references"]
    assert len(refs) == 2
    assert all(ref["type"] == "image_url" for ref in refs)
    assert all(
        ref["image_url"]["url"].startswith("data:image/png;base64,") for ref in refs
    )


def test_merge_prompt_parts_keeps_user_when_system_cannot_fit() -> None:
    user = "USER PROMPT MUST SURVIVE"
    system = "SYSTEM " + ("z" * 400)
    merged = _merge_prompt_parts(user, system, max_chars=120)
    assert merged == user
    assert len(merged) <= 120


def test_merge_prompt_parts_clips_system_when_there_is_room() -> None:
    user = "USER PROMPT MUST SURVIVE"
    system = "SYSTEM " + ("z" * 800)
    merged = _merge_prompt_parts(user, system, max_chars=400)
    assert user in merged
    assert len(merged) <= 400
    assert "[truncated]" in merged


def test_image_payload_stays_within_openrouter_prompt_limit() -> None:
    client = OpenRouterClient(
        api_key="fake-key",
        model="openai/gpt-image-2.5-sunburst",
        supported_parameters=frozenset({"aspect_ratio", "quality"}),
    )
    payload = client._build_image_payload(
        "GENERATE SLIDE 20: keep the current slide",
        "system " + ("s" * 25_000),
        None,
        image_size="2K",
        supported=client._supported_parameters,
    )
    assert len(payload["prompt"]) <= OPENROUTER_IMAGE_PROMPT_MAX_CHARS
    assert "GENERATE SLIDE 20" in payload["prompt"]


def test_image_payload_omits_resolution_for_openai_quality_models() -> None:
    client = OpenRouterClient(
        api_key="fake-key",
        model="openai/gpt-image-2.5-sunburst",
        supported_parameters=frozenset(
            {"aspect_ratio", "quality", "n", "input_references"}
        ),
    )
    payload = client._build_image_payload(
        "a slide",
        None,
        None,
        image_size="2K",
        supported=client._supported_parameters,
    )
    assert payload["model"] == "openai/gpt-image-2.5-sunburst"
    assert payload["aspect_ratio"] == "16:9"
    assert payload["quality"] == "high"
    assert payload["n"] == 1
    assert "resolution" not in payload


def test_image_payload_omits_resolution_when_capabilities_unknown() -> None:
    client = OpenRouterClient(api_key="fake-key", model="openai/gpt-image-2.5-sunburst")
    payload = client._build_image_payload(
        "a slide", None, None, image_size="2K", supported=None
    )
    assert "resolution" not in payload
    assert "quality" not in payload
    assert payload["aspect_ratio"] == "16:9"


def test_supported_parameter_names_unions_endpoints() -> None:
    names = _supported_parameter_names(
        {
            "endpoints": [
                {"supported_parameters": {"aspect_ratio": {}, "quality": {}}},
                {"supported_parameters": {"n": {}}},
            ]
        }
    )
    assert names == frozenset({"aspect_ratio", "quality", "n"})


def test_http_error_detail_reads_openrouter_message() -> None:
    response = httpx.Response(
        400,
        json={"error": {"message": "Invalid input: resolution is not supported"}},
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/images"),
    )
    assert "resolution is not supported" in _http_error_detail(response)


@pytest.mark.asyncio
async def test_generate_single_image_uses_model_capabilities(
    mock_api_response, mock_image_bytes, respx_mock
) -> None:
    client = OpenRouterClient(api_key="fake-key", model="openai/gpt-image-2.5-sunburst")
    respx_mock.get(
        f"{client.BASE_URL}/images/models/openai/gpt-image-2.5-sunburst/endpoints"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "endpoints": [
                    {
                        "supported_parameters": {
                            "aspect_ratio": {"type": "enum", "values": ["16:9"]},
                            "quality": {"type": "enum", "values": ["high"]},
                            "n": {"type": "range", "min": 1, "max": 10},
                        }
                    }
                ]
            },
        )
    )
    route = respx_mock.post(f"{client.BASE_URL}/images").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )

    async with httpx.AsyncClient() as http_client:
        result = await client._generate_single_image(
            http_client, prompt="test prompt", image_size="2K"
        )

    assert result == mock_image_bytes
    sent = json.loads(route.calls[0].request.content)
    assert sent["quality"] == "high"
    assert "resolution" not in sent


@pytest.mark.asyncio
async def test_generate_single_image_does_not_retry_permanent_http_error(
    client, respx_mock
) -> None:
    route = respx_mock.post(f"{client.BASE_URL}/images").mock(
        return_value=httpx.Response(400, json={"error": {"message": "bad request"}})
    )

    async with httpx.AsyncClient() as http_client:
        with pytest.raises(httpx.HTTPStatusError):
            await client._generate_single_image(http_client, prompt="test prompt")

    assert len(route.calls) == 1


@pytest.mark.asyncio
async def test_fetch_credits_mocked(client, respx_mock):
    respx_mock.get(f"{client.BASE_URL}/credits").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"total_credits": 10.5, "total_usage": 3.25}},
        )
    )
    out = await client.fetch_credits()
    assert out.credits == {"total_credits": 10.5, "total_usage": 3.25}
    assert out.error is None


@pytest.mark.asyncio
async def test_fetch_credits_prefers_management_api_key(respx_mock):
    route = respx_mock.get(f"{OpenRouterClient.BASE_URL}/credits").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"total_credits": 1.0, "total_usage": 0.5}},
        )
    )
    client = OpenRouterClient(
        api_key="infer-key",
        management_api_key="mgmt-key",
    )
    await client.fetch_credits()
    assert route.calls
    auth = route.calls[0].request.headers.get("authorization", "")
    assert auth == "Bearer mgmt-key"


@pytest.mark.asyncio
async def test_fetch_credits_http_error_returns_outcome(client, respx_mock):
    respx_mock.get(f"{client.BASE_URL}/credits").mock(return_value=httpx.Response(403))
    out = await client.fetch_credits()
    assert out.credits is None
    assert out.error is not None
    assert "403" in out.error


@pytest.mark.asyncio
async def test_generate_images_parallel_mocked(client, mock_api_response, mock_image_bytes, respx_mock):
    respx_mock.post(f"{client.BASE_URL}/images").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )
    prompts = [
        ("prompt 1", None, None),
        ("prompt 2", None, None),
    ]
    results = await client.generate_images_parallel(prompts)
    assert len(results) == 2
    assert all(r == mock_image_bytes for r in results)


@pytest.mark.asyncio
async def test_generate_images_parallel_invokes_on_result_per_completion(
    client, mock_api_response, mock_image_bytes, respx_mock
):
    respx_mock.post(f"{client.BASE_URL}/images").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )
    prompts = [
        ("prompt 1", None, None),
        ("prompt 2", None, None),
    ]
    seen: list[tuple[int, bytes | Exception]] = []

    def on_result(index: int, result: bytes | Exception) -> None:
        seen.append((index, result))

    results = await client.generate_images_parallel(prompts, on_result=on_result)
    assert len(results) == 2
    assert len(seen) == 2
    assert {index for index, _ in seen} == {0, 1}
    assert all(result == mock_image_bytes for _, result in seen)

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
    prompts = [("a", None, None), ("b", None, None)]
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
            http_client, "prompt", reference_images=[mock_image_bytes]
        )
    body = captured["body"]
    assert isinstance(body, dict)
    assert "image" in body
    img_list = body["image"]
    assert isinstance(img_list, list) and len(img_list) == 1
    assert isinstance(img_list[0], str)
    assert img_list[0].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_volcengine_multiple_style_references(mock_image_bytes, respx_mock):
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
            http_client,
            "prompt",
            reference_images=[mock_image_bytes, mock_image_bytes],
        )
    body = captured["body"]
    assert isinstance(body, dict)
    imgs = body["image"]
    assert isinstance(imgs, list) and len(imgs) == 2


def test_openrouter_build_messages_multiple_images() -> None:
    client = OpenRouterClient(api_key="x")
    tiny_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    msgs = client._build_messages("do it", reference_images=[tiny_png, tiny_png])
    user = msgs[-1]["content"]
    assert isinstance(user, list)
    assert sum(1 for p in user if p.get("type") == "image_url") == 2
