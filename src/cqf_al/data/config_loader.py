"""Project configuration and credential loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from decouple import Config, RepositoryEnv


class ProjectConfigError(RuntimeError):
    """Raised when project configuration or credentials are invalid."""


@dataclass(frozen=True)
class AlpacaCredentials:
    """Alpaca API credentials loaded from the local .env file."""

    api_key: str
    secret_key: str


def find_project_root(start: Path | None = None) -> Path:
    """Find the repository root by locating pyproject.toml."""

    current = (start or Path.cwd()).resolve()

    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate

    raise ProjectConfigError(
        "Could not locate project root containing pyproject.toml."
    )


def load_project_config(
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load and minimally validate the project YAML configuration."""

    root = find_project_root()

    path = (
        Path(config_path).expanduser().resolve()
        if config_path is not None
        else root / "config" / "base.yaml"
    )

    if not path.exists():
        raise ProjectConfigError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ProjectConfigError("Configuration must be a YAML mapping.")

    required_sections = {
        "project",
        "safety",
        "broker",
        "market",
        "instruments",
        "data",
        "sample",
        "execution",
        "risk",
        "validation",
    }

    missing_sections = required_sections.difference(config)
    if missing_sections:
        raise ProjectConfigError(
            f"Missing configuration sections: {sorted(missing_sections)}"
        )

    broker = config["broker"]
    required_broker_keys = {
        "provider",
        "paper",
        "credentials_file",
        "api_key_env",
        "secret_key_env",
    }

    missing_broker_keys = required_broker_keys.difference(broker)
    if missing_broker_keys:
        raise ProjectConfigError(
            f"Missing broker keys: {sorted(missing_broker_keys)}"
        )

    data = config["data"]
    required_data_keys = {
        "raw_storage_dir",
        "processed_storage_dir",
        "metadata_storage_dir",
        "storage_format",
        "allow_raw_overwrite",
    }

    missing_data_keys = required_data_keys.difference(data)
    if missing_data_keys:
        raise ProjectConfigError(
            f"Missing data keys: {sorted(missing_data_keys)}"
        )

    if config["safety"]["allow_live_trading"]:
        raise ProjectConfigError(
            "Live trading must remain disabled during project development."
        )

    if not broker["paper"]:
        raise ProjectConfigError("Broker must be configured for paper mode.")

    return config


def load_alpaca_credentials(
    config: dict[str, Any] | None = None,
) -> AlpacaCredentials:
    """Load Alpaca credentials without exposing them in logs."""

    project_config = config or load_project_config()
    root = find_project_root()

    broker = project_config["broker"]
    env_path = root / broker["credentials_file"]

    if not env_path.exists():
        raise ProjectConfigError(f"Credentials file not found: {env_path}")

    env = Config(RepositoryEnv(str(env_path)))

    api_key_name = broker["api_key_env"]
    secret_key_name = broker["secret_key_env"]

    try:
        api_key = env(api_key_name)
        secret_key = env(secret_key_name)
    except Exception as exc:
        raise ProjectConfigError(
            "Required Alpaca credentials are missing from .env."
        ) from exc

    if not api_key.strip() or not secret_key.strip():
        raise ProjectConfigError("Alpaca credentials cannot be empty.")

    return AlpacaCredentials(
        api_key=api_key.strip(),
        secret_key=secret_key.strip(),
    )


def resolve_data_directories(
    config: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Resolve configured data directories relative to the repository."""

    project_config = config or load_project_config()
    root = find_project_root()
    data = project_config["data"]

    return {
        "raw": root / data["raw_storage_dir"],
        "processed": root / data["processed_storage_dir"],
        "metadata": root / data["metadata_storage_dir"],
    }
