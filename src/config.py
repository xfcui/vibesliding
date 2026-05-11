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
Provider = Literal["openrouter", "volcengine"]


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
        "model": None,
        "max_concurrent": None,
        "use_proxy": None,
    }
    if not parser.has_section(OPENROUTER_SECTION):
        return out
    section = parser[OPENROUTER_SECTION]
    for key in ("api_key", "management_api_key", "proxy", "model", "use_proxy"):
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
        "model": None,
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
        "model",
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
    if os.getenv("OPENROUTER_MODEL"):
        data["model"] = os.getenv("OPENROUTER_MODEL")
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

    def resolve_max_concurrent(file_mc: int | None) -> int | None:
        if file_mc is not None:
            return file_mc
        return default_mc

    if provider == "openrouter":
        raw = openrouter
        api_key = _resolve_openrouter_api_key(api_key_override, path)
        proxy_section = raw.get("proxy")
        proxy_from_section = (
            proxy_section.strip()
            if isinstance(proxy_section, str) and proxy_section.strip()
            else None
        )
        proxy_from_file = proxy_from_section or _default_str(parser, "proxy")

        use_proxy_or = _coerce_bool_file_or_env(
            raw.get("use_proxy") if isinstance(raw.get("use_proxy"), str) else None,
            "OPENROUTER_USE_PROXY",
            default=True,
        )

        if proxy_override:
            proxy = proxy_override
        elif os.getenv("OPENROUTER_PROXY"):
            proxy = os.getenv("OPENROUTER_PROXY")
        elif use_proxy_or and proxy_from_file:
            proxy = proxy_from_file
        else:
            proxy = None
        model = raw.get("model") or os.getenv("OPENROUTER_MODEL")
        max_concurrent = resolve_max_concurrent(
            raw.get("max_concurrent") if isinstance(raw.get("max_concurrent"), int) else None
        )
        if os.getenv("OPENROUTER_MAX_CONCURRENT"):
            try:
                max_concurrent = int(os.getenv("OPENROUTER_MAX_CONCURRENT", ""))
            except ValueError:
                pass
        if not model:
            raise ValueError(
                "Model is required. Set it in .env under [openrouter] model "
                "or via OPENROUTER_MODEL env var."
            )
        if not max_concurrent or max_concurrent < 1:
            raise ValueError(
                "max_concurrent is required (>= 1). Set it in [DEFAULT] or [openrouter] "
                "max_concurrent or OPENROUTER_MAX_CONCURRENT."
            )
        mgmt_env = (os.getenv("OPENROUTER_MANAGEMENT_API_KEY") or "").strip()
        mgmt_file = raw.get("management_api_key")
        mgmt_key = mgmt_env or (
            mgmt_file.strip()
            if isinstance(mgmt_file, str) and mgmt_file.strip()
            else None
        )
        return Config(
            provider=provider,
            api_key=api_key,
            proxy=proxy if isinstance(proxy, str) else None,
            model=str(model),
            max_concurrent=int(max_concurrent),
            output_dir=output_dir or Path("./output"),
            openrouter_management_api_key=mgmt_key,
        )

    # Volcengine: proxy optional (see use_proxy / VOLCENGINE_PROXY).
    api_key = _resolve_volcengine_api_key(api_key_override, path)
    model = volcengine.get("model") or os.getenv("VOLCENGINE_MODEL")
    max_concurrent = resolve_max_concurrent(
        _int_from_section(parser[VOLCENGINE_SECTION], "max_concurrent")
        if parser.has_section(VOLCENGINE_SECTION)
        else None
    )
    if os.getenv("VOLCENGINE_MAX_CONCURRENT"):
        try:
            max_concurrent = int(os.getenv("VOLCENGINE_MAX_CONCURRENT", ""))
        except ValueError:
            pass
    if not model:
        raise ValueError(
            "Model is required. Set it in .env under [volcengine] model "
            "or via VOLCENGINE_MODEL env var."
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
