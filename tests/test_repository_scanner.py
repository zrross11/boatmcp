"""Tests for repository scanner."""

from pathlib import Path

import pytest

from boatmcp.services.repository import RepositoryScanner


@pytest.mark.asyncio
async def test_scan_python_project(python_project_dir: Path) -> None:
    """Test scanning a Python project."""
    scanner = RepositoryScanner()

    result = await scanner.scan_repository(str(python_project_dir))

    assert result.success
    assert result.analysis is not None
    assert result.analysis.project_type == "python"
    assert result.analysis.language == "python"
    assert result.analysis.framework == "flask"
    assert result.analysis.dependencies is not None and "flask" in result.analysis.dependencies
    assert result.analysis.entry_points is not None and len(result.analysis.entry_points) > 0


@pytest.mark.asyncio
async def test_scan_go_project(go_project_dir: Path) -> None:
    """Test scanning a Go project."""
    scanner = RepositoryScanner()

    result = await scanner.scan_repository(str(go_project_dir))

    assert result.success
    assert result.analysis is not None
    assert result.analysis.project_type == "go"
    assert result.analysis.language == "go"
    assert result.analysis.package_manager == "go"
    assert result.analysis.entry_points is not None and len(result.analysis.entry_points) > 0


@pytest.mark.asyncio
async def test_scan_nonexistent_directory() -> None:
    """Test scanning a non-existent directory."""
    scanner = RepositoryScanner()

    result = await scanner.scan_repository("/nonexistent/path")

    assert not result.success
    assert result.error is not None and "does not exist" in result.error


@pytest.mark.asyncio
async def test_scan_file_instead_of_directory(python_project_dir: Path) -> None:
    """Test scanning a file instead of directory."""
    scanner = RepositoryScanner()

    file_path = python_project_dir / "app.py"
    result = await scanner.scan_repository(str(file_path))

    assert not result.success
    assert result.error is not None and "not a directory" in result.error
