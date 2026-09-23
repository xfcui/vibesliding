"""Tests for MiniMax speech synthesis through the shared retry and rate limit."""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest

from src.core.config import MiniMaxTtsConfig
from src.core.minimax_tts import synthesize_speech_parallel

CONFIG = MiniMaxTtsConfig(api_key="fake-key", tts_model="speech-test", tts_voice="voice-test")
OK_BODY = {"base_resp": {"status_code": 0}, "data": {"audio": b"hi".hex()}}


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("asyncio.sleep", AsyncMock())


@pytest.mark.asyncio
async def test_synthesize_retries_transient_errors(respx_mock) -> None:
    route = respx_mock.post(f"{CONFIG.BASE_URL}/t2a_v2").mock(
        side_effect=[httpx.Response(500), httpx.Response(200, json=OK_BODY)]
    )
    results = await synthesize_speech_parallel(CONFIG, ["hello"])
    assert results == [b"hi"]
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_synthesize_fails_fast_on_permanent_errors(respx_mock) -> None:
    route = respx_mock.post(f"{CONFIG.BASE_URL}/t2a_v2").mock(
        return_value=httpx.Response(401, json={"error": "unauthorized"})
    )
    results = await synthesize_speech_parallel(CONFIG, ["hello", "again"])
    assert all(isinstance(result, httpx.HTTPStatusError) for result in results)
    assert route.call_count == 2
