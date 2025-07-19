"""Kubernetes-related schemas (Helm and Minikube)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HelmGenerationRequest:
    """Request for Helm chart generation."""
    project_path: Path
    chart_name: str
    app_version: str = "1.0.0"
    chart_version: str = "0.1.0"
    image_name: str = "app"
    image_tag: str = "latest"
    port: int = 80
    namespace: str = "default"
    custom_values: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.custom_values is None:
            object.__setattr__(self, 'custom_values', {})


@dataclass(frozen=True)
class HelmGenerationResult:
    """Result of Helm chart generation."""
    success: bool
    chart_path: Path | None = None
    error: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            object.__setattr__(self, 'warnings', [])


@dataclass(frozen=True)
class HelmDeploymentRequest:
    """Request for deploying Helm chart to minikube."""
    chart_path: Path
    release_name: str
    namespace: str = "default"
    values_overrides: dict[str, Any] | None = None
    wait: bool = True
    timeout: int = 300

    def __post_init__(self) -> None:
        if self.values_overrides is None:
            object.__setattr__(self, 'values_overrides', {})


@dataclass(frozen=True)
class HelmDeploymentResult:
    """Result of Helm deployment."""
    success: bool
    release_name: str | None = None
    namespace: str | None = None
    error: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            object.__setattr__(self, 'warnings', [])
