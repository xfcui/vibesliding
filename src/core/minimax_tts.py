"""MiniMax TTS client — Chinese-native voice synthesis with voice cloning."""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any, Final

import httpx

from src.core.api_client import (
    DEFAULT_MIN_REQUEST_INTERVAL,
    AsyncRateLimiter,
    _image_api_retry,
    _run_parallel_api_calls,
)
from src.core.config import MiniMaxTtsConfig
from src.core.validate import CJK_CHAR_PATTERN

_UPLOAD_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(30.0, read=120.0)
_TTS_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(30.0, read=120.0)
_CLONE_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(30.0, read=120.0)


def _check_response(data: dict[str, Any], context: str) -> None:
    """Raise on non-zero MiniMax status_code."""
    resp = data.get("base_resp", {})
    code = resp.get("status_code", -1)
    if code != 0:
        msg = resp.get("status_msg", "unknown error")
        raise RuntimeError(f"MiniMax {context} failed (code {code}): {msg}")


def language_boost_for(text: str) -> str:
    """``Chinese`` for CJK text; otherwise let MiniMax detect the language."""
    return "Chinese" if CJK_CHAR_PATTERN.search(text) else "auto"


def _voice_id_from_path(ref_path: Path) -> str:
    """Deterministic voice_id derived from the reference audio content hash."""
    content_hash = hashlib.md5(ref_path.read_bytes()).hexdigest()[:12]
    return f"vibesliding_{content_hash}"


@_image_api_retry()
async def _upload_file(
    client: httpx.AsyncClient,
    file_path: Path,
    purpose: str,
    *,
    api_key: str,
    base_url: str,
) -> int:
    """Upload a file and return the file_id."""
    url = f"{base_url}/files/upload"
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f)}
        data = {"purpose": purpose}
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            data=data,
            files=files,
            timeout=_UPLOAD_TIMEOUT,
        )
    response.raise_for_status()
    result = response.json()
    _check_response(result, f"file upload ({purpose})")
    file_id = result.get("file", {}).get("file_id")
    if not file_id:
        raise RuntimeError(f"MiniMax file upload returned no file_id: {result}")
    return int(file_id)


@_image_api_retry()
async def _clone_voice(
    client: httpx.AsyncClient,
    *,
    file_id: int,
    voice_id: str,
    model: str,
    api_key: str,
    base_url: str,
) -> None:
    """Create a cloned voice from an uploaded audio file."""
    url = f"{base_url}/voice_clone"
    payload: dict[str, Any] = {
        "file_id": file_id,
        "voice_id": voice_id,
    }
    response = await client.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=_CLONE_TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()
    _check_response(result, "voice clone")


async def setup_cloned_voice(
    config: MiniMaxTtsConfig,
    reference_audio: Path,
) -> str:
    """Upload reference audio + clone voice, return the usable voice_id.

    If the voice was already cloned (same audio hash), returns the same id.
    """
    voice_id = _voice_id_from_path(reference_audio)
    async with httpx.AsyncClient() as client:
        file_id = await _upload_file(
            client,
            reference_audio,
            "voice_clone",
            api_key=config.api_key or "",
            base_url=config.BASE_URL,
        )
        try:
            await _clone_voice(
                client,
                file_id=file_id,
                voice_id=voice_id,
                model=config.tts_model,
                api_key=config.api_key or "",
                base_url=config.BASE_URL,
            )
        except RuntimeError as exc:
            if "duplicate" not in str(exc).lower():
                raise
    return voice_id


async def synthesize_speech_parallel(
    config: MiniMaxTtsConfig,
    texts: list[str],
    *,
    voice_id: str | None = None,
    desc: str = "Speech synthesis",
    max_concurrent: int = 4,
) -> list[bytes | Exception]:
    """Synthesize multiple texts in parallel with shared retries, rate limit, and tqdm."""
    semaphore = asyncio.Semaphore(max_concurrent)
    rate_limiter = AsyncRateLimiter(DEFAULT_MIN_REQUEST_INTERVAL)
    resolved_voice = voice_id or config.tts_voice
    url = f"{config.BASE_URL}/t2a_v2"

    @_image_api_retry()
    async def _synthesize(client: httpx.AsyncClient, text: str) -> bytes:
        await rate_limiter.acquire()
        async with semaphore:
            payload: dict[str, Any] = {
                "model": config.tts_model,
                "text": text,
                "voice_setting": {
                    "voice_id": resolved_voice,
                    "speed": 1.0,
                    "vol": 1.0,
                    "pitch": 0,
                },
                "audio_setting": {
                    "sample_rate": 32000,
                    "bitrate": 128000,
                    "format": "mp3",
                    "channel": 1,
                },
                "language_boost": language_boost_for(text),
                "output_format": "hex",
            }
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=_TTS_TIMEOUT,
            )
            response.raise_for_status()
            result = response.json()
            _check_response(result, "TTS synthesis")
            hex_audio = result.get("data", {}).get("audio")
            if not hex_audio:
                raise RuntimeError("MiniMax TTS returned no audio data")
            return bytes.fromhex(hex_audio)

    async def _run_one(client: httpx.AsyncClient, index: int) -> tuple[int, bytes | Exception]:
        try:
            return index, await _synthesize(client, texts[index])
        except Exception as exc:
            return index, exc

    return await _run_parallel_api_calls(
        total=len(texts),
        max_concurrent=max_concurrent,
        proxy=None,
        desc=desc,
        unit="call",
        run_one=_run_one,
        missing_error="Missing speech result",
    )
