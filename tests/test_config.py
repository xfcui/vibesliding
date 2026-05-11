"""Tests for .env parsing and provider-specific config loading."""

from pathlib import Path

import pytest

from src.config import _normalize_ini_for_configparser, load_config


def test_normalize_prepends_default_section() -> None:
    raw = "max_concurrent = 10\n\n[openrouter]\napi_key = k\n"
    norm = _normalize_ini_for_configparser(raw)
    assert norm.startswith("[DEFAULT]")
    assert "max_concurrent = 10" in norm
    assert "[openrouter]" in norm


def test_normalize_noop_when_first_line_is_section() -> None:
    raw = "[openrouter]\nmax_concurrent = 10\n"
    assert _normalize_ini_for_configparser(raw) == raw


def test_provider_required_when_unspecified(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = sk-test\nmodel = google/test-model\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Provider is required"):
        load_config(config_path=env, output_dir=tmp_path / "o")


def test_openrouter_loads_when_provider_in_preamble(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "provider = openrouter\n"
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = sk-test\nmodel = google/test-model\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.provider == "openrouter"
    assert c.api_key == "sk-test"
    assert c.model == "google/test-model"


def test_load_volcengine_from_tmp(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 4\n"
        "provider = volcengine\n\n"
        "[volcengine]\n"
        "api_key = ark-test\n"
        "model = doubao-seedream-5-0-260128\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "out")
    assert c.provider == "volcengine"
    assert c.api_key == "ark-test"
    assert c.model == "doubao-seedream-5-0-260128"
    assert c.max_concurrent == 4
    assert c.proxy is None
    assert c.volcengine_image_size == "2K"
    assert c.volcengine_response_format == "url"
    assert c.volcengine_watermark is True
    assert c.volcengine_proxy is None


def test_openrouter_proxy_from_preamble(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "proxy = socks5://127.0.0.1:1080\n"
        "max_concurrent = 36\n"
        "provider = openrouter\n\n"
        "[openrouter]\n"
        "api_key = sk-test\n"
        "model = google/test\n"
        "use_proxy = true\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.provider == "openrouter"
    assert c.proxy == "socks5://127.0.0.1:1080"


def test_openrouter_use_proxy_false_ignores_preamble(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "proxy = socks5://127.0.0.1:1080\n"
        "max_concurrent = 2\n"
        "provider = openrouter\n\n"
        "[openrouter]\n"
        "api_key = sk-test\n"
        "model = m\n"
        "use_proxy = false\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.proxy is None


def test_volcengine_use_proxy_false_ignores_preamble_proxy(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n"
        "proxy = socks5://bad.example:1080\n\n"
        "[volcengine]\napi_key = k\nmodel = m\nuse_proxy = false\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.volcengine_proxy is None


def test_volcengine_ark_api_key_in_preamble(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n"
        "ARK_API_KEY = ark-from-default\n\n"
        "[volcengine]\nmodel = m\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.api_key == "ark-from-default"


def test_load_volcengine_watermark_false(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n\n"
        "[volcengine]\napi_key = k\nmodel = m\nwatermark = false\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.volcengine_watermark is False


def test_load_volcengine_invalid_response_format(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n\n"
        "[volcengine]\napi_key = k\nmodel = m\nresponse_format = raw\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="response_format"):
        load_config(config_path=env, output_dir=tmp_path / "o")


def test_ark_api_key_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VOLCENGINE_API_KEY", raising=False)
    monkeypatch.setenv("ARK_API_KEY", "from-ark-env")
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n\n[volcengine]\nmodel = m\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.api_key == "from-ark-env"


def test_load_openrouter_proxy_from_section(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 2\n"
        "provider = openrouter\n\n"
        "[openrouter]\n"
        "api_key = sk-test\n"
        "model = google/gemini-test\n"
        "proxy = http://127.0.0.1:9\n"
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.provider == "openrouter"
    assert c.proxy == "http://127.0.0.1:9"


def test_volcengine_missing_max_raises(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "[volcengine]\napi_key = x\nmodel = m\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="max_concurrent"):
        load_config(
            config_path=env,
            output_dir=tmp_path / "o",
            provider_override="volcengine",
        )
