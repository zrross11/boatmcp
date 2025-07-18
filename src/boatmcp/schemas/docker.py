"""Docker-related schemas."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass(frozen=True)
class DockerfileInstruction:
    """A single Dockerfile instruction."""
    instruction: str
    arguments: str
    comment: Optional[str] = None


@dataclass(frozen=True)
class DockerfileTemplate:
    """Template for generating Dockerfiles."""
    base_image: str
    instructions: List[DockerfileInstruction]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.instructions is None:
            object.__setattr__(self, 'instructions', [])
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class DockerfileGenerationRequest:
    """Request for Dockerfile generation."""
    project_path: Path
    output_path: Optional[Path] = None
    custom_instructions: Optional[List[str]] = None
    optimize_for_size: bool = False
    multi_stage: bool = False
    
    def __post_init__(self):
        if self.custom_instructions is None:
            object.__setattr__(self, 'custom_instructions', [])


@dataclass(frozen=True)
class DockerfileGenerationResult:
    """Result of Dockerfile generation."""
    success: bool
    dockerfile_path: Optional[Path] = None
    dockerfile_content: Optional[str] = None
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            object.__setattr__(self, 'warnings', [])