"""Schemas for workflow requests and responses."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DeploymentWorkflowRequest:
    """Request for a complete minikube deployment workflow."""

    project_path: Path
    app_name: str
    namespace: str = "default"
    image_tag: str = "latest"
    port: int = 80
    optimize_for_size: bool = False
    multi_stage: bool = False
    custom_instructions: list[str] | None = None
    minikube_profile: str = "boatmcp-cluster"


@dataclass(frozen=True)
class DeploymentWorkflowResult:
    """Result of a deployment workflow execution."""

    success: bool
    app_name: str
    namespace: str
    image_tag: str = "latest"
    steps_completed: list[str] | None = None
    dockerfile_path: Path | None = None
    chart_path: Path | None = None
    error: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        if self.steps_completed is None:
            object.__setattr__(self, "steps_completed", [])
        if self.warnings is None:
            object.__setattr__(self, "warnings", [])
