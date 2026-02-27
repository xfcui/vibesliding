"""OpenRouter API client with SOCKS5 proxy, parallel execution, and retry."""

from __future__ import annotations

import asyncio
import base64
import json
import re
from typing import Any, Final, Optional, Union, List, Tuple

import httpx
from tqdm import tqdm
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

# Constants
DEFAULT_MODEL: Final[str] = "google/gemini-3.1-flash-image-preview"
DEFAULT_MAX_CONCURRENT: Final[int] = 36
DEFAULT_TIMEOUT: Final[float] = 120.0
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_RETRY_WAIT: Final[int] = 1
DATA_URL_PATTERN: Final[re.Pattern] = re.compile(r"data:image/[^;]+;base64,(.+)")


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
        self._semaphore = asyncio.Semaphore(max_concurrent)

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
            async with self._semaphore:
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
