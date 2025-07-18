"""Repository scanning functionality."""

from pathlib import Path

from ...schemas.repository import ScanResult
from .analyzer import RepositoryAnalyzer


class RepositoryScanner:
    """Scans and analyzes repositories."""

    def __init__(self) -> None:
        self.analyzer = RepositoryAnalyzer()

    async def scan_repository(self, path: str) -> ScanResult:
        """Scan a repository and return analysis results."""
        try:
            project_path = Path(path).resolve()

            if not project_path.exists():
                return ScanResult(
                    success=False,
                    error=f"Path does not exist: {project_path}"
                )

            if not project_path.is_dir():
                return ScanResult(
                    success=False,
                    error=f"Path is not a directory: {project_path}"
                )

            # Perform analysis
            analysis = self.analyzer.analyze_project(project_path)

            return ScanResult(
                success=True,
                analysis=analysis,
                files_scanned=len(analysis.source_files or []) + len(analysis.config_files or []) + len(analysis.static_files or [])
            )

        except Exception as e:
            return ScanResult(
                success=False,
                error=f"Error scanning repository: {str(e)}"
            )
