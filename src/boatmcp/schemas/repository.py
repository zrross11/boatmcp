"""Repository scanning and analysis schemas."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from pathlib import Path


@dataclass(frozen=True)
class FileInfo:
    """Information about a scanned file."""
    path: Path
    size: int
    content: Optional[str] = None
    is_binary: bool = False


@dataclass(frozen=True)
class ProjectAnalysis:
    """Analysis results for a project."""
    root_path: Path
    project_type: Literal["python", "go", "node", "java", "rust", "unknown"]
    language: str
    framework: Optional[str] = None
    package_manager: Optional[str] = None
    dependencies: List[str] = None
    entry_points: List[str] = None
    config_files: List[FileInfo] = None
    source_files: List[FileInfo] = None
    static_files: List[FileInfo] = None
    
    def __post_init__(self):
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
    analysis: Optional[ProjectAnalysis] = None
    error: Optional[str] = None
    files_scanned: int = 0