"""Configuration loading from .env file with env/CLI overrides."""

import os
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG_PATH = Path(".env")


@dataclass
class Config:
    """Resolved configuration for OpenRouter and output."""

    api_key: str | None
    proxy: str | None
    model: str
    max_concurrent: int
    output_dir: Path

    def validate(self) -> None:
        """Raise ValueError if required fields are missing or invalid."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "OpenRouter API key is required. Set it via --api-key, "
                "OPENROUTER_API_KEY env var, or in .env under [openrouter] api_key."
            )
        if self.max_concurrent < 1:
            raise ValueError("max_concurrent must be at least 1")


def _load_raw_config(config_path: Path | None = None) -> dict[str, str | int | None]:
    """Load raw settings from .env file."""
    config_path = config_path or DEFAULT_CONFIG_PATH
    result: dict[str, str | int | None] = {
        "api_key": None,
        "proxy": None,
        "model": None,
        "max_concurrent": None,
    }

    if config_path.exists():
        parser = ConfigParser()
        parser.read(config_path)
        if parser.has_section("openrouter"):
            section = parser["openrouter"]
            if section.get("api_key"):
                result["api_key"] = section.get("api_key", "").strip() or None
            if section.get("proxy"):
                result["proxy"] = section.get("proxy", "").strip() or None
            if section.get("model"):
                result["model"] = section.get("model", "").strip() or None
            if section.get("max_concurrent"):
                try:
                    result["max_concurrent"] = int(section.get("max_concurrent", ""))
                except ValueError:
                    pass

    if os.getenv("OPENROUTER_PROXY"):
        result["proxy"] = os.getenv("OPENROUTER_PROXY")
    if os.getenv("OPENROUTER_MODEL"):
        result["model"] = os.getenv("OPENROUTER_MODEL")
    if os.getenv("OPENROUTER_MAX_CONCURRENT"):
        try:
            result["max_concurrent"] = int(os.getenv("OPENROUTER_MAX_CONCURRENT", ""))
        except ValueError:
            pass

    return result


def load_config(
    config_path: Path | None = None,
    output_dir: Path | None = None,
    api_key_override: str | None = None,
) -> Config:
    """Load full Config. API key: api_key_override > env > .env."""
    raw = _load_raw_config(config_path)
    key = get_api_key(api_key_override, config_path)
    proxy = raw.get("proxy")
    model = raw.get("model")
    max_concurrent = raw.get("max_concurrent")
    
    # Validate required fields from .env
    if not model:
        raise ValueError(
            "Model is required. Set it in .env under [openrouter] model or via OPENROUTER_MODEL env var."
        )
    if not max_concurrent:
        raise ValueError(
            "max_concurrent is required. Set it in .env under [openrouter] max_concurrent or via OPENROUTER_MAX_CONCURRENT env var."
        )
    
    out = output_dir or Path("./output")
    return Config(
        api_key=key,
        proxy=proxy,
        model=str(model),
        max_concurrent=int(max_concurrent),
        output_dir=out,
    )


def get_api_key(
    cli_value: str | None = None,
    config_path: Path | None = None,
) -> str | None:
    """Resolve API key: CLI > OPENROUTER_API_KEY env > .env file."""
    if cli_value and cli_value.strip():
        return cli_value.strip()
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    raw = _load_raw_config(config_path)
    return raw.get("api_key") or None
