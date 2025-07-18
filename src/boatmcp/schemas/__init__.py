"""Schemas for BoatMCP project."""

from .repository import FileInfo, ProjectAnalysis, ScanResult
from .docker import DockerfileInstruction, DockerfileTemplate, DockerfileGenerationRequest, DockerfileGenerationResult

__all__ = [
    "FileInfo",
    "ProjectAnalysis", 
    "ScanResult",
    "DockerfileInstruction",
    "DockerfileTemplate",
    "DockerfileGenerationRequest",
    "DockerfileGenerationResult",
]