"""OpenRouter and Volcengine (Ark) image API clients with retry and parallelism."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
from typing import Any, Final

import httpx
from tqdm import tqdm
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    before_sleep_log,
)

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL: Final[str] = "google/gemini-3.1-flash-image-preview"
DEFAULT_MAX_CONCURRENT: Final[int] = 36
DEFAULT_TIMEOUT: Final[float] = 120.0
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_RETRY_WAIT: Final[int] = 1
DATA_URL_PATTERN: Final[re.Pattern] = re.compile(r"data:image/[^;]+;base64,(.+)")
DEFAULT_VOLCENGINE_BASE: Final[str] = "https://ark.cn-beijing.volces.com/api/v3"


class OpenRouterClient:
    """Async client for OpenRouter image generation with optional proxy and retry."""

    BASE_URL: Final[str] = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        proxy: str | None = None,
        model: str = DEFAULT_MODEL,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    ) -> None:
        self.api_key = api_key
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
        reference_image: bytes | None = None,
        assistant_context: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build messages array for the API request."""
        messages: list[dict[str, Any]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if assistant_context:
            messages.append({"role": "assistant", "content": assistant_context})

        if reference_image is None:
            messages.append({"role": "user", "content": prompt})
            return messages

        b64 = base64.standard_b64encode(reference_image).decode("ascii")
        data_url = f"data:image/png;base64,{b64}"
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ],
            }
        )
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

    async def _generate_single_image(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        system_prompt: str | None = None,
        reference_image: bytes | None = None,
        assistant_context: str | None = None,
    ) -> bytes:
        """Generate a single image with retry logic.
        
        Args:
            client: HTTP client for making requests
            prompt: User prompt for image generation
            system_prompt: Optional system instructions
            reference_image: Optional reference image bytes
            assistant_context: Optional assistant context
            
        Returns:
            Generated image as bytes
            
        Raises:
            httpx.HTTPStatusError: If API returns error status
            ValueError: If response format is invalid
        """
        @retry(
            stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
            wait=wait_fixed(DEFAULT_RETRY_WAIT),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            retry=retry_if_exception_type(
                (
                    httpx.HTTPStatusError,
                    httpx.ConnectError,
                    httpx.TimeoutException,
                    ValueError,
                    json.JSONDecodeError,
                )
            ),
        )
        async def _do_request() -> bytes:
            async with self.semaphore:
                payload = {
                    "model": self._model,
                    "messages": self._build_messages(
                        prompt, system_prompt, reference_image, assistant_context
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
        prompts: list[tuple[str, str | None, bytes | None, list[bytes] | None, list[str] | None]],
    ) -> list[bytes | Exception]:
        """Generate multiple images in parallel with progress tracking.
        
        Args:
            prompts: List of tuples containing (prompt, system_prompt, reference_image,
                    article_pdfs, article_texts)
        
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
            timeout=DEFAULT_TIMEOUT,
            limits=limits,
        ) as client:
            with tqdm(total=total, desc="API calls", unit="call") as pbar:

                async def _wrap_with_progress(
                    prompt: str,
                    sys_prompt: str | None,
                    ref: bytes | None,
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
                            client, prompt, sys_prompt, ref, context
                        )
                    finally:
                        pbar.update(1)

                tasks = [
                    _wrap_with_progress(prompt, sys_prompt, ref, article_pdfs, article_texts)
                    for prompt, sys_prompt, ref, article_pdfs, article_texts in prompts
                ]
                return list(await asyncio.gather(*tasks, return_exceptions=True))


class VolcengineClient:
    """Ark (火山方舟) Seedream via ``POST .../images/generations``.

    Matches the OpenAI-compatible ``client.images.generate`` flow:

    - **Text-to-image:** ``model``, ``prompt``, ``size`` (e.g. ``2K``),
      ``response_format`` (``url`` / ``b64_json``), ``watermark`` (same as
      SDK ``extra_body`` for Ark-specific fields).

    - **Image-to-image / style reference:** pass reference bytes (e.g. the
      slide style PNG/JPEG). The client adds ``image`` as a list of data URLs,
      same as Ark's SDK when you pass reference images (e.g. via ``extra_body``).
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
        """Build ``data:image/...;base64,...`` for Ark ``image`` (png or jpeg from magic bytes)."""
        if len(image_bytes) >= 3 and image_bytes[:3] == b"\xff\xd8\xff":
            mime = "image/jpeg"
        elif len(image_bytes) >= 8 and image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            mime = "image/png"
        else:
            mime = "image/png"
        b64 = base64.standard_b64encode(image_bytes).decode("ascii")
        return f"data:{mime};base64,{b64}"

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
        reference_image: bytes | None = None,
        assistant_context: str | None = None,
    ) -> bytes:
        @retry(
            stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
            wait=wait_fixed(DEFAULT_RETRY_WAIT),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            retry=retry_if_exception_type(
                (
                    httpx.HTTPStatusError,
                    httpx.ConnectError,
                    httpx.TimeoutException,
                    ValueError,
                    json.JSONDecodeError,
                )
            ),
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
                if reference_image is not None:
                    payload["image"] = [self._data_url_for_image(reference_image)]
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
        prompts: list[tuple[str, str | None, bytes | None, list[bytes] | None, list[str] | None]],
    ) -> list[bytes | Exception]:
        total = len(prompts)
        limits = httpx.Limits(
            max_connections=self.max_concurrent,
            max_keepalive_connections=self.max_concurrent,
        )
        async with httpx.AsyncClient(
            proxy=self._proxy,
            timeout=DEFAULT_TIMEOUT,
            limits=limits,
        ) as client:
            with tqdm(total=total, desc="API calls", unit="call") as pbar:

                async def _wrap_with_progress(
                    prompt: str,
                    sys_prompt: str | None,
                    ref: bytes | None,
                    article_pdfs: list[bytes] | None,
                    article_texts: list[str] | None,
                ) -> bytes | Exception:
                    try:
                        context = None
                        if article_texts:
                            context = "\n\n---\n\n".join(article_texts)
                        return await self._generate_single_image(
                            client, prompt, sys_prompt, ref, context
                        )
                    finally:
                        pbar.update(1)

                tasks = [
                    _wrap_with_progress(prompt, sys_prompt, ref, article_pdfs, article_texts)
                    for prompt, sys_prompt, ref, article_pdfs, article_texts in prompts
                ]
                return list(await asyncio.gather(*tasks, return_exceptions=True))
