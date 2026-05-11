"""OpenRouter and Volcengine (Ark) image API clients with retry and parallelism."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
from typing import Any, Final, NamedTuple

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

# Constants
DEFAULT_MODEL: Final[str] = "google/gemini-3.1-flash-image-preview"
DEFAULT_MAX_CONCURRENT: Final[int] = 12
DEFAULT_IMAGE_CONNECT_TIMEOUT: Final[float] = 30.0
DEFAULT_IMAGE_READ_TIMEOUT: Final[float] = 300.0
DEFAULT_IMAGE_WRITE_TIMEOUT: Final[float] = 60.0
DEFAULT_IMAGE_POOL_TIMEOUT: Final[float] = 30.0
DEFAULT_CREDITS_TIMEOUT: Final[float] = 30.0
DEFAULT_RETRY_ATTEMPTS: Final[int] = 5
DEFAULT_RETRY_WAIT_INITIAL: Final[float] = 1.0
DEFAULT_RETRY_WAIT_MAX: Final[float] = 20.0
RETRYABLE_HTTP_STATUS_CODES: Final[frozenset[int]] = frozenset({408, 409, 425, 429})
DATA_URL_PATTERN: Final[re.Pattern] = re.compile(r"data:image/[^;]+;base64,(.+)")
DEFAULT_VOLCENGINE_BASE: Final[str] = "https://ark.cn-beijing.volces.com/api/v3"


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


class CreditsFetchOutcome(NamedTuple):
    """Result of ``GET /credits`` — either balances or a short failure reason for the CLI."""

    credits: dict[str, float] | None
    error: str | None = None


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


class OpenRouterClient:
    """Async client for OpenRouter image generation with optional proxy and retry."""

    BASE_URL: Final[str] = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        proxy: str | None = None,
        model: str = DEFAULT_MODEL,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        management_api_key: str | None = None,
    ) -> None:
        self.api_key = api_key
        self._management_api_key = (management_api_key or "").strip() or None
        self._proxy = proxy
        self._model = model
        self.max_concurrent = max_concurrent
        self._semaphore: asyncio.Semaphore | None = None

    @property
    def semaphore(self) -> asyncio.Semaphore:
        """Get or create semaphore for the current event loop."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

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
    ) -> bytes:
        """Generate a single image with retry logic.
        
        Args:
            client: HTTP client for making requests
            prompt: User prompt for image generation
            system_prompt: Optional system instructions
            reference_images: Optional reference image bytes (one or more)
            assistant_context: Optional assistant context
            
        Returns:
            Generated image as bytes
            
        Raises:
            httpx.HTTPStatusError: If API returns error status
            ValueError: If response format is invalid
        """
        @retry(
            stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
            wait=wait_exponential_jitter(
                initial=DEFAULT_RETRY_WAIT_INITIAL,
                max=DEFAULT_RETRY_WAIT_MAX,
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            retry=retry_if_exception(_is_retryable_exception),
            reraise=True,
        )
        async def _do_request() -> bytes:
            async with self.semaphore:
                payload = {
                    "model": self._model,
                    "messages": self._build_messages(
                        prompt, system_prompt, reference_images, assistant_context
                    ),
                    "modalities": ["image", "text"],
                }
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                return self._extract_image(response.json())

        return await _do_request()

    async def generate_images_parallel(
        self,
        prompts: list[tuple[
            str, str | None, list[bytes] | None, list[bytes] | None, list[str] | None
        ]],
    ) -> list[bytes | Exception]:
        """Generate multiple images in parallel with progress tracking.

        Args:
            prompts: List of (prompt, system_prompt, reference_images,
                article_pdfs, article_texts).

        Returns:
            List of generated images (bytes) or exceptions for failed generations
        """
        total = len(prompts)
        limits = httpx.Limits(
            max_connections=self.max_concurrent,
            max_keepalive_connections=self.max_concurrent,
        )
        async with httpx.AsyncClient(
            proxy=self._proxy,
            timeout=_image_timeout(),
            limits=limits,
        ) as client:
            with tqdm(total=total, desc="API calls", unit="call") as pbar:

                async def _wrap_with_progress(
                    prompt: str,
                    sys_prompt: str | None,
                    ref_images: list[bytes] | None,
                    article_pdfs: list[bytes] | None,
                    article_texts: list[str] | None,
                ) -> bytes | Exception:
                    """Wrap generation with progress bar update."""
                    try:
                        # NOTE: PDF content extraction is not implemented yet
                        # For now, combine all article texts as context
                        context = None
                        if article_texts:
                            context = "\n\n---\n\n".join(article_texts)
                        return await self._generate_single_image(
                            client, prompt, sys_prompt, ref_images, context
                        )
                    finally:
                        pbar.update(1)

                tasks = [
                    _wrap_with_progress(
                        prompt, sys_prompt, ref_images, article_pdfs, article_texts
                    )
                    for prompt, sys_prompt, ref_images, article_pdfs, article_texts in prompts
                ]
                return list(await asyncio.gather(*tasks, return_exceptions=True))


class VolcengineClient:
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
    ) -> None:
        self.api_key = api_key
        self._model = model
        self.max_concurrent = max_concurrent
        self._base_url = (base_url or DEFAULT_VOLCENGINE_BASE).rstrip("/")
        self._image_size = image_size
        rf = response_format.strip().lower()
        if rf not in ("url", "b64_json"):
            raise ValueError("response_format must be 'url' or 'b64_json'")
        self._response_format = rf
        self._watermark = watermark
        self._proxy = proxy
        self._semaphore: asyncio.Semaphore | None = None

    @property
    def semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

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
    ) -> bytes:
        @retry(
            stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
            wait=wait_exponential_jitter(
                initial=DEFAULT_RETRY_WAIT_INITIAL,
                max=DEFAULT_RETRY_WAIT_MAX,
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            retry=retry_if_exception(_is_retryable_exception),
            reraise=True,
        )
        async def _do_request() -> bytes:
            async with self.semaphore:
                merged = self._merge_prompt(
                    prompt, system_prompt, assistant_context
                )
                payload: dict[str, Any] = {
                    "model": self._model,
                    "prompt": merged,
                    "size": self._image_size,
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

    async def generate_images_parallel(
        self,
        prompts: list[tuple[
            str, str | None, list[bytes] | None, list[bytes] | None, list[str] | None
        ]],
    ) -> list[bytes | Exception]:
        total = len(prompts)
        limits = httpx.Limits(
            max_connections=self.max_concurrent,
            max_keepalive_connections=self.max_concurrent,
        )
        async with httpx.AsyncClient(
            proxy=self._proxy,
            timeout=_image_timeout(),
            limits=limits,
        ) as client:
            with tqdm(total=total, desc="API calls", unit="call") as pbar:

                async def _wrap_with_progress(
                    prompt: str,
                    sys_prompt: str | None,
                    ref_images: list[bytes] | None,
                    article_pdfs: list[bytes] | None,
                    article_texts: list[str] | None,
                ) -> bytes | Exception:
                    try:
                        context = None
                        if article_texts:
                            context = "\n\n---\n\n".join(article_texts)
                        return await self._generate_single_image(
                            client, prompt, sys_prompt, ref_images, context
                        )
                    finally:
                        pbar.update(1)

                tasks = [
                    _wrap_with_progress(
                        prompt, sys_prompt, ref_images, article_pdfs, article_texts
                    )
                    for prompt, sys_prompt, ref_images, article_pdfs, article_texts in prompts
                ]
                return list(await asyncio.gather(*tasks, return_exceptions=True))
