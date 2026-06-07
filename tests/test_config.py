"""Tests for .env parsing and provider-specific config loading."""

from pathlib import Path

import pytest

from src.core.config import _normalize_ini_for_configparser, load_config, load_outline_config


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
        "[openrouter]\napi_key = sk-test\nimg_model = google/test-model\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Provider is required"):
        load_config(config_path=env, output_dir=tmp_path / "o")


def test_openrouter_loads_when_provider_in_preamble(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "provider = openrouter\n"
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = sk-test\nimg_model = google/test-model\n",
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
        "img_model = doubao-seedream-5-0-260128\n"
        "txt_model = doubao-1-5-pro-32k-250115\n",
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
        "img_model = google/test\n"
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
        "img_model = m\n"
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
        "[volcengine]\napi_key = k\nimg_model = m\nuse_proxy = false\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.volcengine_proxy is None


def test_volcengine_ark_api_key_in_preamble(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n"
        "ARK_API_KEY = ark-from-default\n\n"
        "[volcengine]\nimg_model = m\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.api_key == "ark-from-default"


def test_load_volcengine_watermark_false(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n\n"
        "[volcengine]\napi_key = k\nimg_model = m\nwatermark = false\n",
        encoding="utf-8",
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.volcengine_watermark is False


def test_load_volcengine_invalid_response_format(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n\n"
        "[volcengine]\napi_key = k\nimg_model = m\nresponse_format = raw\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="response_format"):
        load_config(config_path=env, output_dir=tmp_path / "o")


def test_ark_api_key_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VOLCENGINE_API_KEY", raising=False)
    monkeypatch.setenv("ARK_API_KEY", "from-ark-env")
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\nprovider = volcengine\n\n[volcengine]\nimg_model = m\n",
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
        "img_model = google/gemini-test\n"
        "proxy = http://127.0.0.1:9\n"
    )
    c = load_config(config_path=env, output_dir=tmp_path / "o")
    assert c.provider == "openrouter"
    assert c.proxy == "http://127.0.0.1:9"


def test_load_outline_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VALYU_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_TXT_MODEL", raising=False)
    monkeypatch.delenv("VALYU_MODE", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 3\n\n"
        "[openrouter]\n"
        "api_key = or-key\n"
        "txt_model = anthropic/claude-sonnet-4\n"
        "img_model = google/image-model\n"
        "use_proxy = false\n\n"
        "[valyu]\n"
        "api_key = valyu-key\n"
        "mode = heavy\n",
        encoding="utf-8",
    )
    c = load_outline_config(config_path=env)
    assert c.valyu_api_key == "valyu-key"
    assert c.valyu_mode == "heavy"
    assert c.valyu_categories == ()
    assert c.openrouter_api_key == "or-key"
    assert c.txt_model == "anthropic/claude-sonnet-4"
    assert c.max_concurrent == 3


def test_load_outline_config_cli_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VALYU_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = or\nimg_model = m\n"
        "[valyu]\napi_key = v\n",
        encoding="utf-8",
    )
    c = load_outline_config(
        config_path=env,
        valyu_api_key_override="cli-valyu",
        openrouter_api_key_override="cli-or",
        txt_model_override="openai/gpt-4",
        valyu_mode_override="fast",
        valyu_categories_override="research, markets",
    )
    assert c.valyu_api_key == "cli-valyu"
    assert c.openrouter_api_key == "cli-or"
    assert c.txt_model == "openai/gpt-4"
    assert c.valyu_mode == "fast"
    assert c.valyu_categories == ("research", "markets")


def test_load_outline_config_valyu_categories_from_env_section(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VALYU_CATEGORIES", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = or\ntxt_model = m\n"
        "[valyu]\napi_key = v\ncategories = research,healthcare\n",
        encoding="utf-8",
    )
    c = load_outline_config(config_path=env)
    assert c.valyu_categories == ("research", "healthcare")


def test_load_outline_config_rejects_unknown_valyu_categories(
    tmp_path: Path,
) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = or\ntxt_model = m\n"
        "[valyu]\napi_key = v\ncategories = not-a-category\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unknown Valyu datasource categories"):
        load_outline_config(config_path=env)


def test_load_outline_config_volcengine_txt_model_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_TXT_MODEL", raising=False)
    monkeypatch.delenv("VOLCENGINE_TXT_MODEL", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "max_concurrent = 1\n\n"
        "[openrouter]\napi_key = or\n"
        "[volcengine]\napi_key = ve\n"
        "txt_model = doubao-1-5-pro-32k-250115\n"
        "[valyu]\napi_key = v\n",
        encoding="utf-8",
    )
    c = load_outline_config(config_path=env)
    assert c.txt_model == "doubao-1-5-pro-32k-250115"


def test_volcengine_missing_max_raises(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "[volcengine]\napi_key = x\nimg_model = m\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="max_concurrent"):
        load_config(
            config_path=env,
            output_dir=tmp_path / "o",
            provider_override="volcengine",
        )


def test_valyu_proxy_bypass_by_default(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "proxy = socks5://127.0.0.1:1080\n"
        "provider = openrouter\n\n"
        "[openrouter]\n"
        "api_key = sk-or\n"
        "txt_model = claude\n"
        "use_proxy = true\n"
        "[valyu]\n"
        "api_key = v-key\n",
        encoding="utf-8",
    )
    c = load_outline_config(config_path=env)
    assert c.proxy == "socks5://127.0.0.1:1080"
    assert c.valyu_proxy is None  # Bypassed by default!


def test_valyu_proxy_opt_in(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "proxy = socks5://127.0.0.1:1080\n"
        "provider = openrouter\n\n"
        "[openrouter]\n"
        "api_key = sk-or\n"
        "txt_model = claude\n"
        "use_proxy = true\n"
        "[valyu]\n"
        "api_key = v-key\n"
        "use_proxy = true\n",
        encoding="utf-8",
    )
    c = load_outline_config(config_path=env)
    assert c.proxy == "socks5://127.0.0.1:1080"
    assert c.valyu_proxy == "socks5://127.0.0.1:1080"

