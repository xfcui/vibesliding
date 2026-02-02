"""OpenRouter API client with SOCKS5 proxy, parallel execution, and retry."""

import asyncio
import base64
import json
import re
from typing import Any

import httpx
from tqdm import tqdm
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)


class OpenRouterClient:
    """Async client for OpenRouter image generation with optional proxy and retry."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        proxy: str | None = None,
        model: str = "google/gemini-3-pro-image-preview",
        max_concurrent: int = 36,
    ):
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
        """Extract image bytes from OpenRouter chat completion response."""
        try:
            choices = data.get("choices") or []
            if not choices:
                raise ValueError("No choices in response")
            message = choices[0].get("message") or {}
            images = message.get("images") or []
            if not images:
                raise ValueError("No images in response")
            first = images[0]
            url = first.get("image_url", {}).get("url") or first.get("imageUrl", {}).get("url")
            if not url:
                raise ValueError("No image URL in first image")
            # Parse data URL: data:image/png;base64,<payload>
            match = re.match(r"data:image/[^;]+;base64,(.+)", url)
            if not match:
                raise ValueError("Image URL is not a base64 data URL")
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
        """Generate a single image with retry logic."""

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_fixed(1),
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
        prompts: list[tuple[str, str | None, bytes | None, bytes | None, str | None]],
    ) -> list[bytes | Exception]:
        """Generate multiple images in parallel. Shows progress with tqdm."""
        total = len(prompts)
        async with httpx.AsyncClient(
            proxy=self._proxy,
            timeout=120.0,
        ) as client:
            with tqdm(total=total, desc="API calls", unit="call") as pbar:

                async def wrap(
                    prompt: str,
                    sys_prompt: str | None,
                    ref: bytes | None,
                    article_pdf: bytes | None,
                    article_text: str | None,
                ):
                    try:
                        # Combine article_pdf and article_text into context string for assistant
                        context = None
                        if article_pdf or article_text:
                            # For now, we only use article_text as context
                            # PDF content would need to be extracted first
                            context = article_text
                        return await self._generate_single_image(
                            client, prompt, sys_prompt, ref, context
                        )
                    finally:
                        pbar.update(1)

                tasks = [
                    wrap(prompt, sys_prompt, ref, article_pdf, article_text)
                    for prompt, sys_prompt, ref, article_pdf, article_text in prompts
                ]
                return list(await asyncio.gather(*tasks, return_exceptions=True))
