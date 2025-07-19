"""Configuration loading and management for BoatMCP."""

import os
from pathlib import Path
from typing import cast

import yaml

from .types import JSONDict


class BoatMCPConfig:
    """Configuration class for BoatMCP server settings."""

    def __init__(self, config_data: JSONDict) -> None:
        """Initialize configuration from config data.

        Args:
            config_data: Parsed configuration dictionary
        """
        self._config = config_data

    @property
    def internal_tools(self) -> bool:
        """Whether internal development tools should be enabled."""
        return bool(self._config.get("server", {}).get("internal_tools", False))

    @property
    def transport(self) -> str:
        """MCP server transport type."""
        return str(self._config.get("server", {}).get("transport", "stdio"))

    @property
    def docker_enabled(self) -> bool:
        """Whether Docker tools are enabled."""
        return bool(self._config.get("tools", {}).get("docker", {}).get("enabled", True))

    @property
    def kubernetes_enabled(self) -> bool:
        """Whether Kubernetes tools are enabled."""
        return bool(self._config.get("tools", {}).get("kubernetes", {}).get("enabled", True))

    @property
    def workflows_enabled(self) -> bool:
        """Whether workflow tools are enabled."""
        return bool(self._config.get("tools", {}).get("workflows", {}).get("enabled", True))

    @property
    def default_minikube_profile(self) -> str:
        """Default minikube profile name."""
        return str(
            self._config.get("tools", {})
            .get("kubernetes", {})
            .get("default_minikube_profile", "boatmcp-cluster")
        )


def load_config(config_path: Path | None = None) -> BoatMCPConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, looks for config.yaml in project root.

    Returns:
        BoatMCPConfig instance with loaded settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file has invalid YAML syntax
    """
    if config_path is None:
        # Look for config.yaml in the project root (where the script is run from)
        config_path = Path.cwd() / "config.yaml"

    if not config_path.exists():
        # Fallback to environment variable behavior if no config file
        return BoatMCPConfig({
            "server": {
                "internal_tools": os.getenv("BOATMCP_INTERNAL_TOOLS", "false").lower() == "true",
                "transport": "stdio"
            },
            "tools": {
                "docker": {"enabled": True},
                "kubernetes": {"enabled": True, "default_minikube_profile": "boatmcp-cluster"},
                "workflows": {"enabled": True}
            }
        })

    try:
        with open(config_path, encoding="utf-8") as f:
            config_data = cast(JSONDict, yaml.safe_load(f) or {})
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in config file {config_path}: {e}") from e

    return BoatMCPConfig(config_data)
