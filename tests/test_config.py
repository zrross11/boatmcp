"""Tests for configuration loading and management."""

import tempfile
from pathlib import Path

import pytest
import yaml

from boatmcp.core.config import BoatMCPConfig, load_config


class TestBoatMCPConfig:
    """Test the BoatMCPConfig class."""

    def test_config_with_empty_dict(self):
        """Test config initialization with empty dictionary."""
        config = BoatMCPConfig({})

        assert config.internal_tools is False
        assert config.transport == "stdio"
        assert config.docker_enabled is True
        assert config.kubernetes_enabled is True
        assert config.workflows_enabled is True
        assert config.default_minikube_profile == "boatmcp-cluster"

    def test_config_with_custom_values(self):
        """Test config initialization with custom values."""
        config_data = {
            "server": {
                "internal_tools": True,
                "transport": "http"
            },
            "tools": {
                "docker": {"enabled": False},
                "kubernetes": {
                    "enabled": False,
                    "default_minikube_profile": "custom-profile"
                },
                "workflows": {"enabled": False}
            }
        }

        config = BoatMCPConfig(config_data)

        assert config.internal_tools is True
        assert config.transport == "http"
        assert config.docker_enabled is False
        assert config.kubernetes_enabled is False
        assert config.workflows_enabled is False
        assert config.default_minikube_profile == "custom-profile"

    def test_config_with_partial_values(self):
        """Test config with partial configuration (should use defaults for missing values)."""
        config_data = {
            "server": {
                "internal_tools": True
            },
            "tools": {
                "docker": {"enabled": False}
            }
        }

        config = BoatMCPConfig(config_data)

        assert config.internal_tools is True
        assert config.transport == "stdio"  # default
        assert config.docker_enabled is False
        assert config.kubernetes_enabled is True  # default
        assert config.workflows_enabled is True  # default


class TestLoadConfig:
    """Test the load_config function."""

    def test_load_config_from_file(self):
        """Test loading config from YAML file."""
        config_data = {
            "server": {
                "internal_tools": True,
                "transport": "stdio"
            },
            "tools": {
                "docker": {"enabled": True},
                "kubernetes": {"enabled": True, "default_minikube_profile": "test-cluster"},
                "workflows": {"enabled": True}
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            config = load_config(temp_path)

            assert config.internal_tools is True
            assert config.transport == "stdio"
            assert config.docker_enabled is True
            assert config.kubernetes_enabled is True
            assert config.workflows_enabled is True
            assert config.default_minikube_profile == "test-cluster"
        finally:
            temp_path.unlink()

    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist (should fallback to defaults)."""
        non_existent_path = Path("/non/existent/config.yaml")

        config = load_config(non_existent_path)

        # Should use defaults with internal_tools=False (unless env var set)
        assert config.transport == "stdio"
        assert config.docker_enabled is True
        assert config.kubernetes_enabled is True
        assert config.workflows_enabled is True

    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [[[")
            temp_path = Path(f.name)

        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_path)
        finally:
            temp_path.unlink()

    def test_load_config_none_path(self):
        """Test loading config with None path (should look for config.yaml in cwd)."""
        # This test assumes no config.yaml exists in test environment
        config = load_config(None)

        # Should fallback to environment variable behavior
        assert isinstance(config, BoatMCPConfig)
        assert config.transport == "stdio"

    def test_load_config_with_environment_fallback(self, monkeypatch):
        """Test config fallback to environment variables when file doesn't exist."""
        # Set environment variable
        monkeypatch.setenv("BOATMCP_INTERNAL_TOOLS", "true")

        non_existent_path = Path("/non/existent/config.yaml")
        config = load_config(non_existent_path)

        # Should use environment variable value
        assert config.internal_tools is True
