"""Configuration loading from .env file with env/CLI overrides."""

import os
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Constants
DEFAULT_CONFIG_PATH: Final[Path] = Path(".env")
CONFIG_SECTION: Final[str] = "openrouter"


@dataclass
class Config:
    """Resolved configuration for OpenRouter and output."""

    api_key: str | None
    proxy: str | None
    model: str
    max_concurrent: int
    output_dir: Path

    def validate(self) -> None:
        """Validate configuration parameters.
        
        Raises:
            ValueError: If required fields are missing or have invalid values.
        """
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "OpenRouter API key is required. Set it via --api-key, "
                "OPENROUTER_API_KEY env var, or in .env under [openrouter] api_key."
            )
        if self.max_concurrent < 1:
            raise ValueError(f"max_concurrent must be at least 1, got: {self.max_concurrent}")


def _load_raw_config(config_path: Path | None = None) -> dict[str, str | int | None]:
    """Load raw settings from .env file using ConfigParser.
    
    Args:
        config_path: Path to .env file, defaults to DEFAULT_CONFIG_PATH
    
    Returns:
        Dictionary with configuration values from file and environment variables
    """
    config_path = config_path or DEFAULT_CONFIG_PATH
    result: dict[str, str | int | None] = {
        "api_key": None,
        "proxy": None,
        "model": None,
        "max_concurrent": None,
    }

    # Load from .env file if it exists
    if config_path.exists():
        parser = ConfigParser()
        parser.read(config_path)
        
        if parser.has_section(CONFIG_SECTION):
            section = parser[CONFIG_SECTION]
            
            # Extract string values
            for key in ("api_key", "proxy", "model"):
                value = section.get(key, "").strip()
                if value:
                    result[key] = value
            
            # Extract integer value
            max_concurrent_str = section.get("max_concurrent", "").strip()
            if max_concurrent_str:
                try:
                    result["max_concurrent"] = int(max_concurrent_str)
                except ValueError:
                    pass  # Ignore invalid values

    # Environment variables override .env file
    env_overrides = {
        "proxy": "OPENROUTER_PROXY",
        "model": "OPENROUTER_MODEL",
    }
    
    for key, env_var in env_overrides.items():
        env_value = os.getenv(env_var)
        if env_value:
            result[key] = env_value
    
    # Handle max_concurrent separately due to type conversion
    max_concurrent_env = os.getenv("OPENROUTER_MAX_CONCURRENT")
    if max_concurrent_env:
        try:
            result["max_concurrent"] = int(max_concurrent_env)
        except ValueError:
            pass  # Ignore invalid values

    return result


def load_config(
    config_path: Path | None = None,
    output_dir: Path | None = None,
    api_key_override: str | None = None,
    proxy_override: str | None = None,
) -> Config:
    """Load and validate full configuration.
    
    Priority: 
    - api_key: api_key_override > OPENROUTER_API_KEY env > .env file
    - proxy: proxy_override > OPENROUTER_PROXY env > .env file
    
    Args:
        config_path: Path to .env configuration file
        output_dir: Output directory path
        api_key_override: API key override from CLI
        proxy_override: Proxy override from CLI
    
    Returns:
        Validated Config object
        
    Raises:
        ValueError: If required configuration is missing or invalid
    """
    raw = _load_raw_config(config_path)
    api_key = get_api_key(api_key_override, config_path)
    
    # Resolve proxy with priority: CLI > env > .env file
    proxy = proxy_override if proxy_override else raw.get("proxy")
    
    # Validate required fields
    model = raw.get("model")
    if not model:
        raise ValueError(
            "Model is required. Set it in .env under [openrouter] model "
            "or via OPENROUTER_MODEL env var."
        )
    
    max_concurrent = raw.get("max_concurrent")
    if not max_concurrent:
        raise ValueError(
            "max_concurrent is required. Set it in .env under [openrouter] max_concurrent "
            "or via OPENROUTER_MAX_CONCURRENT env var."
        )
    
    return Config(
        api_key=api_key,
        proxy=proxy,
        model=str(model),
        max_concurrent=int(max_concurrent),
        output_dir=output_dir or Path("./output"),
    )


def get_api_key(
    cli_value: str | None = None,
    config_path: Path | None = None,
) -> str | None:
    """Resolve API key with priority: CLI > OPENROUTER_API_KEY env > .env file.
    
    Args:
        cli_value: API key from CLI argument
        config_path: Path to .env configuration file
    
    Returns:
        Resolved API key or None if not found
    """
    # Priority 1: CLI argument
    if cli_value and cli_value.strip():
        return cli_value.strip()
    
    # Priority 2: Environment variable
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    
    # Priority 3: .env file
    raw = _load_raw_config(config_path)
    api_key = raw.get("api_key")
    return api_key if isinstance(api_key, str) else None
