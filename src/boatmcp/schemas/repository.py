"""Repository scanning and analysis schemas."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class FileInfo:
    """Information about a scanned file."""
    path: Path
    size: int
    content: str | None = None
    is_binary: bool = False


@dataclass(frozen=True)
class ProjectAnalysis:
    """Analysis results for a project."""
    root_path: Path
    project_type: Literal["python", "go", "node", "java", "rust", "unknown"]
    language: str
    framework: str | None = None
    package_manager: str | None = None
    dependencies: list[str] | None = None
    entry_points: list[str] | None = None
    config_files: list[FileInfo] | None = None
    source_files: list[FileInfo] | None = None
    static_files: list[FileInfo] | None = None

    def __post_init__(self) -> None:
        if self.dependencies is None:
            object.__setattr__(self, 'dependencies', [])
        if self.entry_points is None:
            object.__setattr__(self, 'entry_points', [])
        if self.config_files is None:
            object.__setattr__(self, 'config_files', [])
        if self.source_files is None:
            object.__setattr__(self, 'source_files', [])
        if self.static_files is None:
            object.__setattr__(self, 'static_files', [])


@dataclass(frozen=True)
class ScanResult:
    """Result of repository scanning operation."""
    success: bool
    analysis: ProjectAnalysis | None = None
    error: str | None = None
    files_scanned: int = 0
