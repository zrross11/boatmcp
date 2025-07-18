"""Tests for repository scanner."""

import pytest
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from nlpi.services.repository import RepositoryScanner


@pytest.mark.asyncio
async def test_scan_python_project(python_project_dir):
    """Test scanning a Python project."""
    scanner = RepositoryScanner()
    
    result = await scanner.scan_repository(str(python_project_dir))
    
    assert result.success
    assert result.analysis is not None
    assert result.analysis.project_type == "python"
    assert result.analysis.language == "python"
    assert result.analysis.framework == "flask"
    assert "flask" in result.analysis.dependencies
    assert len(result.analysis.entry_points) > 0


@pytest.mark.asyncio
async def test_scan_go_project(go_project_dir):
    """Test scanning a Go project."""
    scanner = RepositoryScanner()
    
    result = await scanner.scan_repository(str(go_project_dir))
    
    assert result.success
    assert result.analysis is not None
    assert result.analysis.project_type == "go"
    assert result.analysis.language == "go"
    assert result.analysis.package_manager == "go"
    assert len(result.analysis.entry_points) > 0


@pytest.mark.asyncio
async def test_scan_nonexistent_directory():
    """Test scanning a non-existent directory."""
    scanner = RepositoryScanner()
    
    result = await scanner.scan_repository("/nonexistent/path")
    
    assert not result.success
    assert "does not exist" in result.error


@pytest.mark.asyncio
async def test_scan_file_instead_of_directory(python_project_dir):
    """Test scanning a file instead of directory."""
    scanner = RepositoryScanner()
    
    file_path = python_project_dir / "app.py"
    result = await scanner.scan_repository(str(file_path))
    
    assert not result.success
    assert "not a directory" in result.error