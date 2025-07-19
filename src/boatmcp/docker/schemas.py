"""Docker-related schemas."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DockerfileGenerationRequest:
    """Request for Dockerfile generation."""
    project_path: Path
    output_path: Path | None = None
    custom_instructions: list[str] | None = None
    optimize_for_size: bool = False
    multi_stage: bool = False

    def __post_init__(self) -> None:
        if self.custom_instructions is None:
            object.__setattr__(self, 'custom_instructions', [])


@dataclass(frozen=True)
class DockerfileGenerationResult:
    """Result of Dockerfile generation."""
    success: bool
    dockerfile_path: Path | None = None
    dockerfile_content: str | None = None
    error: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            object.__setattr__(self, 'warnings', [])
