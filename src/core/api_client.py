"""OpenRouter and Volcengine (Ark) image API clients with retry and parallelism."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any, Final, NamedTuple, Union

import httpx
from tqdm import tqdm
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)

# Set up logging
logger = logging.getLogger(__name__)

# Constants (OpenRouter defaults align with .env.example / README; retries & HTTP phases are shared with Volcengine.)
DEFAULT_MODEL: Final[str] = "google/gemini-3-pro-image-preview"
DEFAULT_OPENROUTER_BASE: Final[str] = "https://openrouter.ai/api/v1"
DEFAULT_VOLCENGINE_BASE: Final[str] = "https://ark.cn-beijing.volces.com/api/v3"

DEFAULT_MAX_CONCURRENT: Final[int] = 12
# Minimum spacing between successive API calls — caps the request start rate at
# 2 calls/second across all in-flight tasks (including retries) for each client.
DEFAULT_MIN_REQUEST_INTERVAL: Final[float] = 1.0 / 2.0
DEFAULT_IMAGE_CONNECT_TIMEOUT: Final[float] = 30.0
DEFAULT_IMAGE_READ_TIMEOUT: Final[float] = 300.0
DEFAULT_IMAGE_WRITE_TIMEOUT: Final[float] = 60.0
DEFAULT_IMAGE_POOL_TIMEOUT: Final[float] = 30.0
DEFAULT_CREDITS_TIMEOUT: Final[float] = 30.0
DEFAULT_RETRY_ATTEMPTS: Final[int] = 10
DEFAULT_RETRY_WAIT_INITIAL: Final[float] = 1.0
DEFAULT_RETRY_WAIT_MAX: Final[float] = 60.0
RETRYABLE_HTTP_STATUS_CODES: Final[frozenset[int]] = frozenset({408, 409, 425, 429})
DATA_URL_PATTERN: Final[re.Pattern] = re.compile(r"data:image/[^;]+;base64,(.+)")

# OpenRouter image_config (see https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
SLIDE_ASPECT_RATIO: Final[str] = "16:9"
SLIDE_IMAGE_SIZE: Final[str] = "2K"
STYLE_IMAGE_SIZE: Final[str] = "1K"
STYLE_IMAGE_PIXEL_SIZE: Final[tuple[int, int]] = (1280, 720)


class ImagePrompt(NamedTuple):
    """Prompt bundle for parallel image generation.

    ``article_pdfs`` is reserved for future PDF context extraction and is
    currently unused by both image clients.
    """

    prompt: str
    system_prompt: str | None
    reference_images: list[bytes] | None
    article_pdfs: list[bytes] | None
    article_texts: list[str] | None


class TextPrompt(NamedTuple):
    """Prompt bundle for parallel text completion."""

    prompt: str
    system_prompt: str | None


OnImageResult = Callable[[int, Union[bytes, Exception]], None]
OnTextResult = Callable[[int, Union[str, Exception]], None]
GenerateImageFn = Callable[[httpx.AsyncClient, ImagePrompt], Awaitable[bytes]]
CompleteTextFn = Callable[[httpx.AsyncClient, TextPrompt], Awaitable[str]]


def _image_timeout() -> httpx.Timeout:
    """Use long read timeouts for image generation without hiding connect stalls."""
    return httpx.Timeout(
        connect=DEFAULT_IMAGE_CONNECT_TIMEOUT,
        read=DEFAULT_IMAGE_READ_TIMEOUT,
        write=DEFAULT_IMAGE_WRITE_TIMEOUT,
        pool=DEFAULT_IMAGE_POOL_TIMEOUT,
    )


def _credits_timeout() -> httpx.Timeout:
    """Credits calls are lightweight, so keep their total budget short."""
    return httpx.Timeout(DEFAULT_CREDITS_TIMEOUT, connect=10.0, pool=10.0)


def _is_retryable_exception(exc: BaseException) -> bool:
    """Retry transient API failures, but fail fast for permanent client errors."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status >= 500 or status in RETRYABLE_HTTP_STATUS_CODES
    return isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.TimeoutException,
            ValueError,
            json.JSONDecodeError,
        ),
    )


def _image_api_retry():
    """Shared tenacity retry decorator for image/text API calls."""
    return retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=DEFAULT_RETRY_WAIT_INITIAL,
            max=DEFAULT_RETRY_WAIT_MAX,
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        retry=retry_if_exception(_is_retryable_exception),
        reraise=True,
    )


class AsyncRateLimiter:
    """Async rate limiter enforcing a minimum interval between successive acquisitions.

    Calls to :meth:`acquire` are serialized via an internal lock and each call
    schedules the next admissible time, so concurrent waiters are released in a
    fair, evenly-spaced sequence regardless of how many tasks pile up.
    """

    def __init__(self, min_interval: float) -> None:
        if min_interval < 0:
            raise ValueError("min_interval must be non-negative")
        self._min_interval = min_interval
        self._next_available: float = 0.0
        self._lock: asyncio.Lock | None = None

    @property
    def _bound_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def acquire(self) -> None:
        if self._min_interval <= 0:
            return
        async with self._bound_lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            wait_for = self._next_available - now
            if wait_for > 0:
                self._next_available = now + wait_for + self._min_interval
                await asyncio.sleep(wait_for)
            else:
                self._next_available = now + self._min_interval


class CreditsFetchOutcome(NamedTuple):
    """Result of ``GET /credits`` — either balances or a short failure reason for the CLI."""

    credits: dict[str, float] | None
    error: str | None = None


async def _run_parallel_api_calls(
    *,
    total: int,
    max_concurrent: int,
    proxy: str | None,
    desc: str,
    unit: str,
    run_one: Callable[[httpx.AsyncClient, int], Awaitable[tuple[int, Any]]],
    on_result: Callable[[int, Any], None] | None = None,
    missing_error: str,
) -> list[Any]:
    """Run API jobs concurrently with a tqdm progress bar."""
    limits = httpx.Limits(
        max_connections=max_concurrent,
        max_keepalive_connections=max_concurrent,
    )
    async with httpx.AsyncClient(
        proxy=proxy,
        timeout=_image_timeout(),
        limits=limits,
    ) as client:
        with tqdm(total=total, desc=desc, unit=unit) as pbar:

            async def _wrapped(index: int) -> tuple[int, Any]:
                try:
                    return await run_one(client, index)
                finally:
                    pbar.update(1)

            tasks = [asyncio.create_task(_wrapped(index)) for index in range(total)]
            results: list[Any | None] = [None] * total
            for task in asyncio.as_completed(tasks):
                index, result = await task
                results[index] = result
                if on_result is not None:
                    on_result(index, result)
            return [
                r if r is not None else RuntimeError(missing_error) for r in results
            ]


async def _run_parallel_image_generation(
    *,
    prompts: list[ImagePrompt],
    max_concurrent: int,
    proxy: str | None,
    generate_fn: GenerateImageFn,
    on_result: OnImageResult | None = None,
    desc: str = "API calls",
) -> list[bytes | Exception]:
    """Run image jobs concurrently and invoke *on_result* as each one finishes."""
    total = len(prompts)

    async def _run_one(
        client: httpx.AsyncClient, index: int
    ) -> tuple[int, bytes | Exception]:
        try:
            return index, await generate_fn(client, prompts[index])
        except Exception as exc:
            return index, exc

    return await _run_parallel_api_calls(
        total=total,
        max_concurrent=max_concurrent,
        proxy=proxy,
        desc=desc,
        unit="call",
        run_one=_run_one,
        on_result=on_result,
        missing_error="Missing image result",
    )


async def _run_parallel_text_completions(
    *,
    prompts: list[TextPrompt],
    max_concurrent: int,
    proxy: str | None,
    complete_fn: CompleteTextFn,
    desc: str = "API calls",
    on_result: OnTextResult | None = None,
) -> list[str | Exception]:
    """Run text completion jobs concurrently with a tqdm progress bar."""
    total = len(prompts)

    async def _run_one(
        client: httpx.AsyncClient, index: int
    ) -> tuple[int, str | Exception]:
        try:
            return index, await complete_fn(client, prompts[index])
        except Exception as exc:
            return index, exc

    return await _run_parallel_api_calls(
        total=total,
        max_concurrent=max_concurrent,
        proxy=proxy,
        desc=desc,
        unit="call",
        run_one=_run_one,
        on_result=on_result,
        missing_error="Missing text result",
    )


def _image_bytes_to_data_url(image_bytes: bytes) -> str:
    """Build ``data:image/...;base64,...`` for API reference images."""
    if len(image_bytes) >= 3 and image_bytes[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif len(image_bytes) >= 8 and image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    else:
        mime = "image/png"
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _article_context_from_prompt(prompt: ImagePrompt) -> str | None:
    """Combine article texts into assistant context (PDFs not yet supported)."""
    if prompt.article_texts:
        return "\n\n---\n\n".join(prompt.article_texts)
    return None


def _coerce_image_prompt(prompt: ImagePrompt | tuple[str, str | None, list[bytes] | None, list[bytes] | None, list[str] | None]) -> ImagePrompt:
    """Accept legacy 5-tuples or ImagePrompt instances."""
    if isinstance(prompt, ImagePrompt):
        return prompt
    return ImagePrompt(*prompt)


class _BaseImageClient:
    """Shared concurrency, rate limiting, and parallel generation for image clients."""

    def __init__(
        self,
        *,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        proxy: str | None = None,
        min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
    ) -> None:
        self.max_concurrent = max_concurrent
        self._proxy = proxy
        self._semaphore: asyncio.Semaphore | None = None
        self._rate_limiter = AsyncRateLimiter(min_request_interval)

    @property
    def semaphore(self) -> asyncio.Semaphore:
        """Get or create semaphore for the current event loop."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    async def _generate_single_image(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        system_prompt: str | None = None,
        reference_images: list[bytes] | None = None,
        assistant_context: str | None = None,
        *,
        image_size: str | None = None,
    ) -> bytes:
        raise NotImplementedError

    async def generate_images_parallel(
        self,
        prompts: list[ImagePrompt],
        on_result: OnImageResult | None = None,
        *,
        desc: str = "API calls",
        image_size: str | None = None,
    ) -> list[bytes | Exception]:
        """Generate multiple images in parallel with progress tracking."""

        async def _generate_one(client: httpx.AsyncClient, raw_prompt: ImagePrompt) -> bytes:
            prompt = _coerce_image_prompt(raw_prompt)
            context = _article_context_from_prompt(prompt)
            return await self._generate_single_image(
                client,
                prompt.prompt,
                prompt.system_prompt,
                prompt.reference_images,
                context,
                image_size=image_size,
            )

        return await _run_parallel_image_generation(
            prompts=prompts,
            max_concurrent=self.max_concurrent,
            proxy=self._proxy,
            generate_fn=_generate_one,
            on_result=on_result,
            desc=desc,
        )


class OpenRouterClient(_BaseImageClient):
    """Async client for OpenRouter image generation with optional proxy and retry."""

    BASE_URL: Final[str] = DEFAULT_OPENROUTER_BASE

    def __init__(
        self,
        api_key: str,
        proxy: str | None = None,
        model: str = DEFAULT_MODEL,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        management_api_key: str | None = None,
        min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
    ) -> None:
        super().__init__(
            max_concurrent=max_concurrent,
            proxy=proxy,
            min_request_interval=min_request_interval,
        )
        self.api_key = api_key
        self._management_api_key = (management_api_key or "").strip() or None
        self._model = model

    def _build_messages(
        self,
        prompt: str,
        system_prompt: str | None = None,
        reference_images: list[bytes] | None = None,
        assistant_context: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build messages array for the API request."""
        messages: list[dict[str, Any]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if assistant_context:
            messages.append({"role": "assistant", "content": assistant_context})

        if not reference_images:
            messages.append({"role": "user", "content": prompt})
            return messages

        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for image_bytes in reference_images:
            data_url = _image_bytes_to_data_url(image_bytes)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                }
            )
        messages.append({"role": "user", "content": content})
        return messages

    def _extract_text(self, data: dict[str, Any]) -> str:
        """Extract text content from OpenRouter chat completion response."""
        try:
            choices = data.get("choices")
            if not choices:
                raise ValueError("No choices in response")

            message = choices[0].get("message")
            if not message:
                raise ValueError("No message in first choice")

            content = message.get("content")
            if not content or not str(content).strip():
                raise ValueError("No text content in response")

            return str(content).strip()
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Failed to extract text from response: {e}") from e

    def _extract_image(self, data: dict[str, Any]) -> bytes:
        """Extract image bytes from OpenRouter chat completion response.

        Raises:
            ValueError: If the response format is invalid or image data is missing.
        """
        try:
            choices = data.get("choices")
            if not choices:
                raise ValueError("No choices in response")

            message = choices[0].get("message")
            if not message:
                raise ValueError("No message in first choice")

            images = message.get("images")
            if not images:
                raise ValueError("No images in response")

            first_image = images[0]
            url = (
                first_image.get("image_url", {}).get("url")
                or first_image.get("imageUrl", {}).get("url")
            )
            if not url:
                raise ValueError("No image URL in first image")

            # Parse data URL: data:image/png;base64,<payload>
            match = DATA_URL_PATTERN.match(url)
            if not match:
                raise ValueError(f"Image URL is not a valid base64 data URL: {url[:50]}...")

            return base64.standard_b64decode(match.group(1))
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Failed to extract image from response: {e}") from e

    def _credits_http_error_detail(self, response: httpx.Response) -> str:
        detail = f"HTTP {response.status_code}"
        try:
            body = response.json()
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict) and err.get("message") is not None:
                    return f"{detail}: {err['message']}"
        except (ValueError, TypeError):
            pass
        text = (response.text or "").strip()
        if text:
            tail = text if len(text) <= 200 else text[:200] + "…"
            return f"{detail} ({tail})"
        return detail

    async def fetch_credits(self) -> CreditsFetchOutcome:
        """GET ``/credits`` — purchased vs used totals (remaining is their difference).

        OpenRouter expects a Management API key for this route; pass ``management_api_key``
        when constructing the client if your model ``api_key`` is not allowed on ``/credits``.
        """
        credits_key = self._management_api_key or self.api_key
        try:
            async with httpx.AsyncClient(
                proxy=self._proxy,
                timeout=_credits_timeout(),
            ) as http:
                response = await http.get(
                    f"{self.BASE_URL}/credits",
                    headers={"Authorization": f"Bearer {credits_key}"},
                )
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError:
                    return CreditsFetchOutcome(
                        None, self._credits_http_error_detail(response)
                    )
                payload = response.json()
                data = payload.get("data")
                if not isinstance(data, dict):
                    return CreditsFetchOutcome(
                        None, "Invalid response: missing or invalid \"data\" object"
                    )
                raw_tc = data.get("total_credits")
                raw_tu = data.get("total_usage")
                if raw_tc is None or raw_tu is None:
                    return CreditsFetchOutcome(
                        None, "Invalid response: total_credits or total_usage missing"
                    )
                return CreditsFetchOutcome(
                    {
                        "total_credits": float(raw_tc),
                        "total_usage": float(raw_tu),
                    },
                    None,
                )
        except httpx.HTTPError as e:
            return CreditsFetchOutcome(None, str(e) or type(e).__name__)
        except (ValueError, TypeError) as e:
            return CreditsFetchOutcome(None, f"Invalid response: {e}")

    async def _generate_single_image(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        system_prompt: str | None = None,
        reference_images: list[bytes] | None = None,
        assistant_context: str | None = None,
        *,
        image_size: str | None = None,
    ) -> bytes:
        """Generate a single image with retry logic."""

        @_image_api_retry()
        async def _do_request() -> bytes:
            await self._rate_limiter.acquire()
            async with self.semaphore:
                payload = {
                    "model": self._model,
                    "messages": self._build_messages(
                        prompt, system_prompt, reference_images, assistant_context
                    ),
                    "modalities": ["image", "text"],
                    "image_config": {
                        "aspect_ratio": SLIDE_ASPECT_RATIO,
                        "image_size": image_size or SLIDE_IMAGE_SIZE,
                    },
                }
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                return self._extract_image(response.json())

        return await _do_request()

    async def _complete_text_with_client(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        system_prompt: str | None = None,
        *,
        model: str | None = None,
    ) -> str:
        """Generate text via OpenRouter chat completions using a shared HTTP client."""

        @_image_api_retry()
        async def _do_request() -> str:
            await self._rate_limiter.acquire()
            async with self.semaphore:
                payload: dict[str, Any] = {
                    "model": model or self._model,
                    "messages": self._build_messages(prompt, system_prompt),
                }
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                return self._extract_text(response.json())

        return await _do_request()

    async def complete_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        *,
        model: str | None = None,
    ) -> str:
        """Generate text via OpenRouter chat completions (no image modalities)."""
        limits = httpx.Limits(
            max_connections=self.max_concurrent,
            max_keepalive_connections=self.max_concurrent,
        )
        async with httpx.AsyncClient(
            proxy=self._proxy,
            timeout=_image_timeout(),
            limits=limits,
        ) as client:
            return await self._complete_text_with_client(
                client,
                prompt,
                system_prompt,
                model=model,
            )

    async def complete_text_parallel(
        self,
        prompts: list[TextPrompt | tuple[str, str | None]],
        *,
        model: str | None = None,
        on_result: OnTextResult | None = None,
        desc: str = "API calls",
    ) -> list[str | Exception]:
        """Generate multiple text completions in parallel with progress tracking."""
        coerced = [
            prompt if isinstance(prompt, TextPrompt) else TextPrompt(*prompt)
            for prompt in prompts
        ]

        async def _complete_one(
            client: httpx.AsyncClient, text_prompt: TextPrompt
        ) -> str:
            return await self._complete_text_with_client(
                client,
                text_prompt.prompt,
                text_prompt.system_prompt,
                model=model,
            )

        return await _run_parallel_text_completions(
            prompts=coerced,
            max_concurrent=self.max_concurrent,
            proxy=self._proxy,
            complete_fn=_complete_one,
            desc=desc,
            on_result=on_result,
        )


class VolcengineClient(_BaseImageClient):
    """Ark (火山方舟) Seedream via ``POST .../images/generations``.

    Matches the OpenAI-compatible ``client.images.generate`` flow:

    - **Text-to-image:** ``model``, ``prompt``, ``size`` (e.g. ``2K``),
      ``response_format`` (``url`` / ``b64_json``), ``watermark`` (same as
      SDK ``extra_body`` for Ark-specific fields).

    - **Image-to-image / style reference:** pass one or more reference images
      (PNG/JPEG). The client sets ``image`` to a list of data URLs.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        base_url: str | None = None,
        image_size: str = "2K",
        response_format: str = "url",
        watermark: bool = True,
        proxy: str | None = None,
        min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
    ) -> None:
        super().__init__(
            max_concurrent=max_concurrent,
            proxy=proxy,
            min_request_interval=min_request_interval,
        )
        self.api_key = api_key
        self._model = model
        self._base_url = (base_url or DEFAULT_VOLCENGINE_BASE).rstrip("/")
        self._image_size = image_size
        rf = response_format.strip().lower()
        if rf not in ("url", "b64_json"):
            raise ValueError("response_format must be 'url' or 'b64_json'")
        self._response_format = rf
        self._watermark = watermark

    @staticmethod
    def _merge_prompt(
        prompt: str,
        system_prompt: str | None,
        assistant_context: str | None,
    ) -> str:
        parts: list[str] = []
        if system_prompt:
            parts.append(system_prompt.strip())
        if assistant_context:
            parts.append(assistant_context.strip())
        parts.append(prompt.strip())
        return "\n\n".join(p for p in parts if p)

    @staticmethod
    def _data_url_for_image(image_bytes: bytes) -> str:
        """Build ``data:image/...;base64,...`` for Ark ``image``."""
        return _image_bytes_to_data_url(image_bytes)

    async def _extract_image_bytes(
        self, client: httpx.AsyncClient, data: dict[str, Any]
    ) -> bytes:
        data_arr = data.get("data")
        if not data_arr:
            raise ValueError("No data in Volcengine image response")
        item = data_arr[0]
        b64 = item.get("b64_json")
        if b64:
            return base64.standard_b64decode(b64)
        url = item.get("url")
        if url:
            img_resp = await client.get(url)
            img_resp.raise_for_status()
            return img_resp.content
        raise ValueError("Image response missing b64_json and url")

    async def _generate_single_image(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        system_prompt: str | None = None,
        reference_images: list[bytes] | None = None,
        assistant_context: str | None = None,
        *,
        image_size: str | None = None,
    ) -> bytes:
        @_image_api_retry()
        async def _do_request() -> bytes:
            await self._rate_limiter.acquire()
            async with self.semaphore:
                merged = self._merge_prompt(
                    prompt, system_prompt, assistant_context
                )
                payload: dict[str, Any] = {
                    "model": self._model,
                    "prompt": merged,
                    "size": image_size or self._image_size,
                    "response_format": self._response_format,
                    "sequential_image_generation": "disabled",
                    "watermark": self._watermark,
                }
                if reference_images:
                    payload["image"] = [
                        self._data_url_for_image(b) for b in reference_images
                    ]
                response = await client.post(
                    f"{self._base_url}/images/generations",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                return await self._extract_image_bytes(client, response.json())

        return await _do_request()
