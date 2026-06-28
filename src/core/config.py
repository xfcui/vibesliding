"""Configuration loading from .env file with env/CLI overrides."""

from __future__ import annotations

import os
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

# Constants
DEFAULT_CONFIG_PATH: Final[Path] = Path(".env")
OPENROUTER_SECTION: Final[str] = "openrouter"
VOLCENGINE_SECTION: Final[str] = "volcengine"
VALYU_SECTION: Final[str] = "valyu"
MINIMAX_SECTION: Final[str] = "minimax"
Provider = Literal["openrouter", "volcengine"]
TtsProvider = Literal["openrouter", "minimax"]
DeepResearchMode = Literal["fast", "standard", "heavy", "max"]
VALYU_DATASOURCE_CATEGORIES: Final[tuple[str, ...]] = (
    "research",
    "healthcare",
    "patents",
    "markets",
    "company",
    "economic",
    "predictions",
    "legal",
    "politics",
    "cybersecurity",
    "transportation",
)


def _normalize_ini_for_configparser(text: str) -> str:
    """Wrap leading key=value lines (before the first section header) in [DEFAULT].

    Python's ConfigParser rejects keys that appear before any [section].
    """
    lines = text.splitlines()
    first_section = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("[")),
        len(lines),
    )
    preamble = lines[:first_section]
    if not any(
        line.strip() and not line.strip().startswith("#") for line in preamble
    ):
        return text
    rest = "\n".join(lines[first_section:])
    head = "\n".join(preamble)
    if rest.strip():
        return f"[DEFAULT]\n{head}\n\n{rest}"
    return f"[DEFAULT]\n{head}"


@dataclass
class Config:
    """Resolved configuration for image API and output."""

    provider: Provider
    api_key: str | None
    proxy: str | None
    model: str
    max_concurrent: int
    output_dir: Path
    volcengine_base_url: str | None = None
    # Defaults match Ark text-to-image samples (OpenAI-compatible images.generate).
    volcengine_image_size: str = "2K"
    volcengine_response_format: str = "url"
    volcengine_watermark: bool = True
    volcengine_proxy: str | None = None
    # Optional; GET /credits typically requires an OpenRouter Management API key.
    openrouter_management_api_key: str | None = None

    def validate(self) -> None:
        """Validate configuration parameters.

        Raises:
            ValueError: If required fields are missing or have invalid values.
        """
        if not self.api_key or not self.api_key.strip():
            if self.provider == "volcengine":
                raise ValueError(
                    "Volcengine API key is required. Set it via --api-key, "
                    "VOLCENGINE_API_KEY or ARK_API_KEY env var, or in .env under "
                    "[volcengine] api_key."
                )
            raise ValueError(
                "OpenRouter API key is required. Set it via --api-key, "
                "OPENROUTER_API_KEY env var, or in .env under [openrouter] api_key."
            )
        if self.max_concurrent < 1:
            raise ValueError(f"max_concurrent must be at least 1, got: {self.max_concurrent}")


def _parse_csv_list(raw: str | None) -> tuple[str, ...]:
    if not raw or not raw.strip():
        return ()
    return tuple(part.strip().lower() for part in raw.split(",") if part.strip())


def _validate_valyu_categories(categories: tuple[str, ...]) -> None:
    if not categories:
        return
    unknown = [c for c in categories if c not in VALYU_DATASOURCE_CATEGORIES]
    if unknown:
        valid = ", ".join(VALYU_DATASOURCE_CATEGORIES)
        raise ValueError(
            f"Unknown Valyu datasource categories: {', '.join(unknown)}. "
            f"Valid categories: {valid}"
        )


@dataclass
class MiniMaxTtsConfig:
    """Configuration for MiniMax TTS voice synthesis."""

    api_key: str | None
    tts_model: str
    tts_voice: str

    BASE_URL: str = "https://api.minimax.io/v1"


@dataclass
class OutlineConfig:
    """Configuration for idea-to-outline (Valyu + OpenRouter text)."""

    valyu_api_key: str | None
    valyu_mode: DeepResearchMode
    valyu_categories: tuple[str, ...]
    openrouter_api_key: str | None
    txt_model: str
    proxy: str | None
    max_concurrent: int
    valyu_proxy: str | None = None

    def validate_research(self) -> None:
        if not self.valyu_api_key or not self.valyu_api_key.strip():
            raise ValueError(
                "Valyu API key is required. Set it via --valyu-api-key, "
                "VALYU_API_KEY env var, or in .env under [valyu] api_key."
            )
        _validate_valyu_categories(self.valyu_categories)

    def validate_outline(self) -> None:
        if not self.openrouter_api_key or not self.openrouter_api_key.strip():
            raise ValueError(
                "OpenRouter API key is required. Set it via --api-key, "
                "OPENROUTER_API_KEY env var, or in .env under [openrouter] api_key."
            )
        if not self.txt_model or not self.txt_model.strip():
            raise ValueError(
                "Text model is required. Set it in .env under [openrouter] txt_model "
                "or [volcengine] txt_model, or via OPENROUTER_TXT_MODEL / "
                "VOLCENGINE_TXT_MODEL env var."
            )
        if self.max_concurrent < 1:
            raise ValueError(
                f"max_concurrent must be at least 1, got: {self.max_concurrent}"
            )

    def validate(self) -> None:
        self.validate_research()
        self.validate_outline()


def _parser_from_env_path(config_path: Path) -> ConfigParser:
    parser = ConfigParser()
    if not config_path.exists():
        return parser
    raw_text = config_path.read_text(encoding="utf-8")
    parser.read_string(_normalize_ini_for_configparser(raw_text))
    return parser


def _int_from_section(section: dict[str, str], key: str) -> int | None:
    s = section.get(key, "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _load_openrouter_from_parser(parser: ConfigParser) -> dict[str, str | int | None]:
    out: dict[str, str | int | None] = {
        "api_key": None,
        "management_api_key": None,
        "proxy": None,
        "img_model": None,
        "txt_model": None,
        "max_concurrent": None,
        "use_proxy": None,
    }
    if not parser.has_section(OPENROUTER_SECTION):
        return out
    section = parser[OPENROUTER_SECTION]
    for key in (
        "api_key",
        "management_api_key",
        "proxy",
        "img_model",
        "txt_model",
        "use_proxy",
    ):
        value = section.get(key, "").strip()
        if value:
            out[key] = value
    mc = _int_from_section(section, "max_concurrent")
    if mc is not None:
        out["max_concurrent"] = mc
    return out


def _load_volcengine_from_parser(parser: ConfigParser) -> dict[str, str | None]:
    out: dict[str, str | None] = {
        "api_key": None,
        "img_model": None,
        "txt_model": None,
        "base_url": None,
        "image_size": None,
        "response_format": None,
        "watermark": None,
        "proxy": None,
        "use_proxy": None,
    }
    if not parser.has_section(VOLCENGINE_SECTION):
        return out
    section = parser[VOLCENGINE_SECTION]
    for key in (
        "api_key",
        "img_model",
        "txt_model",
        "base_url",
        "image_size",
        "response_format",
        "watermark",
        "proxy",
        "use_proxy",
    ):
        value = section.get(key, "").strip()
        if value:
            out[key] = value
    return out


def _load_valyu_from_parser(parser: ConfigParser) -> dict[str, str | None]:
    out: dict[str, str | None] = {
        "api_key": None,
        "mode": None,
        "categories": None,
        "use_proxy": None,
        "proxy": None,
    }
    if not parser.has_section(VALYU_SECTION):
        return out
    section = parser[VALYU_SECTION]
    for key in ("api_key", "mode", "categories", "use_proxy", "proxy"):
        value = section.get(key, "").strip()
        if value:
            out[key] = value
    return out


def _load_minimax_from_parser(parser: ConfigParser) -> dict[str, str | None]:
    out: dict[str, str | None] = {
        "api_key": None,
        "tts_model": None,
        "tts_voice": None,
    }
    if not parser.has_section(MINIMAX_SECTION):
        return out
    section = parser[MINIMAX_SECTION]
    for key in out:
        value = section.get(key, "").strip()
        if value:
            out[key] = value
    return out


def _coerce_bool_file_or_env(
    file_val: str | None,
    env_name: str,
    *,
    default: bool,
) -> bool:
    env_raw = os.getenv(env_name)
    if env_raw is not None and env_raw.strip():
        return env_raw.strip().lower() in ("1", "true", "yes", "on")
    if file_val is not None and file_val.strip():
        return file_val.strip().lower() in ("1", "true", "yes", "on")
    return default


def _default_max_concurrent(parser: ConfigParser) -> int | None:
    """Reads ``max_concurrent`` from the implicit DEFAULT options (file ``[DEFAULT]`` section)."""
    return _int_from_section(parser.defaults(), "max_concurrent")


def _default_provider(parser: ConfigParser) -> str | None:
    """Reads ``provider`` from DEFAULT options; ``has_section('DEFAULT')`` is always false in ConfigParser."""
    v = (parser.defaults().get("provider") or "").strip().lower()
    return v or None


def _default_str(parser: ConfigParser, key: str) -> str | None:
    """Read string option from preamble / ``[DEFAULT]`` (e.g. global ``proxy``, ``max_concurrent``)."""
    v = (parser.defaults().get(key) or "").strip()
    return v or None


def _first_nonempty_str(*values: str | None) -> str | None:
    """Return the first non-empty stripped string among *values*."""
    for value in values:
        if value and value.strip():
            return value.strip()
    return None


def _resolve_max_concurrent_with_env(
    *,
    section_mc: int | None,
    env_name: str,
    default_mc: int | None,
) -> int | None:
    """Resolve max_concurrent from section, DEFAULT fallback, then env override."""
    mc = section_mc if section_mc is not None else default_mc
    env_raw = os.getenv(env_name)
    if env_raw:
        try:
            mc = int(env_raw)
        except ValueError:
            pass
    return mc


def _load_raw_config(config_path: Path | None = None) -> dict[str, str | int | None]:
    """Load raw OpenRouter-oriented settings (backward compatibility for get_api_key)."""
    config_path = config_path or DEFAULT_CONFIG_PATH
    parser = _parser_from_env_path(config_path)
    data = _load_openrouter_from_parser(parser)
    dm = _default_max_concurrent(parser)
    if dm is not None and data.get("max_concurrent") is None:
        data["max_concurrent"] = dm

    if os.getenv("OPENROUTER_PROXY"):
        data["proxy"] = os.getenv("OPENROUTER_PROXY")
    if os.getenv("OPENROUTER_IMG_MODEL"):
        data["img_model"] = os.getenv("OPENROUTER_IMG_MODEL")
    max_concurrent_env = os.getenv("OPENROUTER_MAX_CONCURRENT")
    if max_concurrent_env:
        try:
            data["max_concurrent"] = int(max_concurrent_env)
        except ValueError:
            pass
    return data


def load_config(
    config_path: Path | None = None,
    output_dir: Path | None = None,
    api_key_override: str | None = None,
    proxy_override: str | None = None,
    provider_override: Provider | None = None,
) -> Config:
    """Load and validate full configuration.

    Priority:
    - provider: CLI ``--provider`` > IMAGE_PROVIDER env > preamble ``provider`` (required
      if not set via those sources — set keys/model under ``[openrouter]``, proxy follows ``use_proxy``).
    - api_key: Uses OpenRouter or Volcengine env/section based on provider
    - openrouter_management_api_key (optional): ``OPENROUTER_MANAGEMENT_API_KEY`` or
      ``[openrouter] management_api_key`` — used only for ``GET /credits`` (Management key).
    - proxy (OpenRouter): CLI > OPENROUTER_PROXY env > [openrouter] proxy > preamble ``proxy``,
      unless ``use_proxy`` is false in ``[openrouter]`` (or OPENROUTER_USE_PROXY=0).
    - proxy (Volcengine): optional — ``VOLCENGINE_PROXY`` env > ``[volcengine]`` proxy > preamble,
      only when ``use_proxy`` is true (``[volcengine]`` or VOLCENGINE_USE_PROXY). Default off.

    Args:
        config_path: Path to .env configuration file
        output_dir: Output directory path
        api_key_override: API key override from CLI
        proxy_override: Proxy override from CLI
        provider_override: Force openrouter or volcengine

    Returns:
        Validated Config object

    Raises:
        ValueError: If required configuration is missing or invalid
    """
    path = config_path or DEFAULT_CONFIG_PATH
    parser = _parser_from_env_path(path)

    prov: str | None = provider_override
    if not prov:
        prov = (os.getenv("IMAGE_PROVIDER") or "").strip().lower() or None
    if not prov:
        prov = _default_provider(parser)
    if not prov:
        raise ValueError(
            "Provider is required. Set --provider, IMAGE_PROVIDER, or "
            "provider in .env (preamble before first [section])."
        )
    if prov not in ("openrouter", "volcengine"):
        raise ValueError(
            f"Invalid provider {prov!r}. Use 'openrouter' or 'volcengine' "
            "(--provider, IMAGE_PROVIDER, or provider in .env preamble)."
        )
    provider: Provider = prov  # type: ignore[assignment]

    openrouter = _load_openrouter_from_parser(parser)
    volcengine = _load_volcengine_from_parser(parser)
    default_mc = _default_max_concurrent(parser)

    if provider == "openrouter":
        raw = openrouter
        api_key = _resolve_openrouter_api_key(api_key_override, path)
        proxy = _resolve_openrouter_proxy(parser, proxy_override=proxy_override)
        model = _first_nonempty_str(
            raw.get("img_model") if isinstance(raw.get("img_model"), str) else None,
            os.getenv("OPENROUTER_IMG_MODEL"),
        )
        max_concurrent = _resolve_max_concurrent_with_env(
            section_mc=raw.get("max_concurrent") if isinstance(raw.get("max_concurrent"), int) else None,
            env_name="OPENROUTER_MAX_CONCURRENT",
            default_mc=default_mc,
        )
        if not model:
            raise ValueError(
                "Image model is required. Set it in .env under [openrouter] img_model "
                "or via OPENROUTER_IMG_MODEL env var."
            )
        if not max_concurrent or max_concurrent < 1:
            raise ValueError(
                "max_concurrent is required (>= 1). Set it in [DEFAULT] or [openrouter] "
                "max_concurrent or OPENROUTER_MAX_CONCURRENT."
            )
        mgmt_file = raw.get("management_api_key")
        mgmt_key = _first_nonempty_str(
            os.getenv("OPENROUTER_MANAGEMENT_API_KEY"),
            mgmt_file if isinstance(mgmt_file, str) else None,
        )
        return Config(
            provider=provider,
            api_key=api_key,
            proxy=proxy,
            model=str(model),
            max_concurrent=int(max_concurrent),
            output_dir=output_dir or Path("./output"),
            openrouter_management_api_key=mgmt_key,
        )

    # Volcengine: proxy optional (see use_proxy / VOLCENGINE_PROXY).
    api_key = _resolve_volcengine_api_key(api_key_override, path)
    model = _first_nonempty_str(
        volcengine.get("img_model"),
        os.getenv("VOLCENGINE_IMG_MODEL"),
    )
    max_concurrent = _resolve_max_concurrent_with_env(
        section_mc=(
            _int_from_section(parser[VOLCENGINE_SECTION], "max_concurrent")
            if parser.has_section(VOLCENGINE_SECTION)
            else None
        ),
        env_name="VOLCENGINE_MAX_CONCURRENT",
        default_mc=default_mc,
    )
    if not model:
        raise ValueError(
            "Image model is required. Set it in .env under [volcengine] img_model "
            "or via VOLCENGINE_IMG_MODEL env var."
        )
    base_url = volcengine.get("base_url") or os.getenv("VOLCENGINE_BASE_URL")
    image_size = (
        volcengine.get("image_size")
        or os.getenv("VOLCENGINE_IMAGE_SIZE")
        or "2K"
    )
    response_format = (
        volcengine.get("response_format")
        or os.getenv("VOLCENGINE_RESPONSE_FORMAT")
        or "url"
    ).strip().lower()
    if response_format not in ("url", "b64_json"):
        raise ValueError(
            "volcengine response_format must be 'url' or 'b64_json' "
            "([volcengine] response_format or VOLCENGINE_RESPONSE_FORMAT)."
        )
    watermark = _coerce_bool_file_or_env(
        volcengine.get("watermark"),
        "VOLCENGINE_WATERMARK",
        default=True,
    )
    use_proxy_ve = _coerce_bool_file_or_env(
        volcengine.get("use_proxy"),
        "VOLCENGINE_USE_PROXY",
        default=False,
    )
    ve_proxy_section = (volcengine.get("proxy") or "").strip() or None
    ve_proxy_from_file = ve_proxy_section or _default_str(parser, "proxy")

    volcengine_proxy: str | None = None
    if use_proxy_ve:
        if os.getenv("VOLCENGINE_PROXY"):
            volcengine_proxy = os.getenv("VOLCENGINE_PROXY")
        elif ve_proxy_from_file:
            volcengine_proxy = ve_proxy_from_file

    if not max_concurrent or max_concurrent < 1:
        raise ValueError(
            "max_concurrent is required (>= 1). Set it in [DEFAULT] or [volcengine] "
            "max_concurrent or VOLCENGINE_MAX_CONCURRENT."
        )
    mc_val = int(max_concurrent)
    return Config(
        provider=provider,
        api_key=api_key,
        proxy=None,
        model=str(model),
        max_concurrent=mc_val,
        output_dir=output_dir or Path("./output"),
        volcengine_base_url=base_url,
        volcengine_image_size=image_size,
        volcengine_response_format=response_format,
        volcengine_watermark=watermark,
        volcengine_proxy=volcengine_proxy,
    )


def _resolve_openrouter_api_key(
    cli_value: str | None,
    config_path: Path | None,
) -> str | None:
    if cli_value and cli_value.strip():
        return cli_value.strip()
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    raw = _load_raw_config(config_path)
    api_key = raw.get("api_key")
    return api_key if isinstance(api_key, str) else None


def _resolve_volcengine_api_key(
    cli_value: str | None,
    config_path: Path | None,
) -> str | None:
    if cli_value and cli_value.strip():
        return cli_value.strip()
    for var in ("VOLCENGINE_API_KEY", "ARK_API_KEY"):
        env_key = os.getenv(var)
        if env_key and env_key.strip():
            return env_key.strip()
    path = config_path or DEFAULT_CONFIG_PATH
    parser = _parser_from_env_path(path)
    d_ark = (parser.defaults().get("ark_api_key") or "").strip()
    if d_ark:
        return d_ark
    ve = _load_volcengine_from_parser(parser)
    k = ve.get("api_key")
    return k if k else None


def get_api_key(
    cli_value: str | None = None,
    config_path: Path | None = None,
) -> str | None:
    """Resolve OpenRouter API key with priority: CLI > OPENROUTER_API_KEY env > .env [openrouter]."""
    return _resolve_openrouter_api_key(cli_value, config_path)


def _resolve_valyu_api_key(
    cli_value: str | None,
    config_path: Path | None,
) -> str | None:
    if cli_value and cli_value.strip():
        return cli_value.strip()
    env_key = os.getenv("VALYU_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    path = config_path or DEFAULT_CONFIG_PATH
    parser = _parser_from_env_path(path)
    valyu = _load_valyu_from_parser(parser)
    k = valyu.get("api_key")
    return k if k else None


def _resolve_openrouter_proxy(
    parser: ConfigParser,
    *,
    proxy_override: str | None,
) -> str | None:
    openrouter = _load_openrouter_from_parser(parser)
    proxy_section = openrouter.get("proxy")
    proxy_from_section = (
        proxy_section.strip()
        if isinstance(proxy_section, str) and proxy_section.strip()
        else None
    )
    proxy_from_file = proxy_from_section or _default_str(parser, "proxy")
    use_proxy_or = _coerce_bool_file_or_env(
        openrouter.get("use_proxy") if isinstance(openrouter.get("use_proxy"), str) else None,
        "OPENROUTER_USE_PROXY",
        default=True,
    )
    if proxy_override:
        return proxy_override
    if os.getenv("OPENROUTER_PROXY"):
        return os.getenv("OPENROUTER_PROXY")
    if use_proxy_or and proxy_from_file:
        return proxy_from_file
    return None


def _resolve_valyu_proxy(
    parser: ConfigParser,
    *,
    proxy_override: str | None = None,
) -> str | None:
    if proxy_override:
        return proxy_override
    valyu = _load_valyu_from_parser(parser)
    use_proxy_valyu = _coerce_bool_file_or_env(
        valyu.get("use_proxy"),
        "VALYU_USE_PROXY",
        default=False,
    )
    if not use_proxy_valyu:
        return None

    valyu_proxy_section = (valyu.get("proxy") or "").strip() or None
    valyu_proxy_from_file = valyu_proxy_section or _default_str(parser, "proxy")

    if os.getenv("VALYU_PROXY"):
        return os.getenv("VALYU_PROXY")
    return valyu_proxy_from_file


def load_outline_config(
    config_path: Path | None = None,
    *,
    valyu_api_key_override: str | None = None,
    openrouter_api_key_override: str | None = None,
    txt_model_override: str | None = None,
    proxy_override: str | None = None,
    valyu_mode_override: DeepResearchMode | None = None,
    valyu_categories_override: str | None = None,
) -> OutlineConfig:
    """Load configuration for the outline CLI (Valyu + OpenRouter text).

    Does not require image provider settings; only outline-specific keys.
    """
    path = config_path or DEFAULT_CONFIG_PATH
    parser = _parser_from_env_path(path)
    openrouter = _load_openrouter_from_parser(parser)
    volcengine = _load_volcengine_from_parser(parser)
    valyu = _load_valyu_from_parser(parser)
    default_mc = _default_max_concurrent(parser)

    valyu_api_key = _resolve_valyu_api_key(valyu_api_key_override, path)
    openrouter_api_key = _resolve_openrouter_api_key(openrouter_api_key_override, path)

    def _section_txt_model(section: dict[str, str | int | None] | dict[str, str | None]) -> str:
        raw = section.get("txt_model")
        return raw.strip() if isinstance(raw, str) and raw.strip() else ""

    txt_model = (
        (txt_model_override or "").strip()
        or (os.getenv("OPENROUTER_TXT_MODEL") or "").strip()
        or (os.getenv("VOLCENGINE_TXT_MODEL") or "").strip()
        or _section_txt_model(openrouter)
        or _section_txt_model(volcengine)
    )

    mode_raw = (
        (valyu_mode_override or "").strip().lower()
        if valyu_mode_override
        else (
            (os.getenv("VALYU_MODE") or "").strip().lower()
            or (valyu.get("mode") or "").strip().lower()
            or "standard"
        )
    )
    if mode_raw not in ("fast", "standard", "heavy", "max"):
        raise ValueError(
            f"Invalid Valyu mode {mode_raw!r}. Use fast, standard, heavy, or max."
        )
    valyu_mode: DeepResearchMode = mode_raw  # type: ignore[assignment]

    categories_raw = (
        (valyu_categories_override or "").strip()
        or (os.getenv("VALYU_CATEGORIES") or "").strip()
        or (valyu.get("categories") or "").strip()
    )
    valyu_categories = _parse_csv_list(categories_raw)
    _validate_valyu_categories(valyu_categories)

    max_concurrent = _resolve_max_concurrent_with_env(
        section_mc=(
            openrouter.get("max_concurrent")
            if isinstance(openrouter.get("max_concurrent"), int)
            else None
        ),
        env_name="OPENROUTER_MAX_CONCURRENT",
        default_mc=default_mc,
    )
    if not max_concurrent or max_concurrent < 1:
        max_concurrent = 4

    proxy = _resolve_openrouter_proxy(parser, proxy_override=proxy_override)
    valyu_proxy = _resolve_valyu_proxy(parser)

    return OutlineConfig(
        valyu_api_key=valyu_api_key,
        valyu_mode=valyu_mode,
        valyu_categories=valyu_categories,
        openrouter_api_key=openrouter_api_key,
        txt_model=txt_model,
        proxy=proxy,
        max_concurrent=int(max_concurrent),
        valyu_proxy=valyu_proxy,
    )


DEFAULT_MINIMAX_TTS_MODEL: Final[str] = "speech-2.8-hd"
DEFAULT_MINIMAX_TTS_VOICE: Final[str] = "Chinese (Mandarin)_Lyrical_Voice"


def load_minimax_tts_config(
    config_path: Path | None = None,
    *,
    api_key_override: str | None = None,
    tts_model_override: str | None = None,
    tts_voice_override: str | None = None,
) -> MiniMaxTtsConfig:
    """Load MiniMax TTS configuration from .env / env vars / CLI overrides."""
    path = config_path or DEFAULT_CONFIG_PATH
    parser = _parser_from_env_path(path)
    mm = _load_minimax_from_parser(parser)

    api_key = (
        api_key_override
        or os.getenv("MINIMAX_API_KEY")
        or mm.get("api_key")
    )
    tts_model = (
        tts_model_override
        or os.getenv("MINIMAX_TTS_MODEL")
        or mm.get("tts_model")
        or DEFAULT_MINIMAX_TTS_MODEL
    )
    tts_voice = (
        tts_voice_override
        or os.getenv("MINIMAX_TTS_VOICE")
        or mm.get("tts_voice")
        or DEFAULT_MINIMAX_TTS_VOICE
    )
    return MiniMaxTtsConfig(
        api_key=api_key,
        tts_model=tts_model,
        tts_voice=tts_voice,
    )
