"""Tests for Dockerfile generator."""

from pathlib import Path

import pytest

from boatmcp.schemas.docker import DockerfileGenerationRequest
from boatmcp.services.docker import DockerfileGenerator
from boatmcp.services.repository import RepositoryScanner


@pytest.mark.asyncio
async def test_generate_dockerfile_python_project(python_project_dir: Path) -> None:
    """Test generating Dockerfile for Python project."""
    scanner = RepositoryScanner()
    generator = DockerfileGenerator()

    # Scan the project first
    scan_result = await scanner.scan_repository(str(python_project_dir))
    assert scan_result.success
    assert scan_result.analysis is not None

    # Generate Dockerfile
    request = DockerfileGenerationRequest(
        project_path=python_project_dir,
        optimize_for_size=True
    )

    result = await generator.generate_dockerfile(request, scan_result.analysis)

    assert result.success
    assert result.dockerfile_content is not None
    assert "FROM python:" in result.dockerfile_content
    assert "COPY requirements.txt" in result.dockerfile_content
    assert "pip install" in result.dockerfile_content
    assert "EXPOSE" in result.dockerfile_content


@pytest.mark.asyncio
async def test_generate_dockerfile_go_project(go_project_dir: Path) -> None:
    """Test generating Dockerfile for Go project."""
    scanner = RepositoryScanner()
    generator = DockerfileGenerator()

    # Scan the project first
    scan_result = await scanner.scan_repository(str(go_project_dir))
    assert scan_result.success
    assert scan_result.analysis is not None

    # Generate Dockerfile
    request = DockerfileGenerationRequest(
        project_path=go_project_dir,
        multi_stage=True
    )

    result = await generator.generate_dockerfile(request, scan_result.analysis)

    assert result.success
    assert result.dockerfile_content is not None
    assert "FROM golang:" in result.dockerfile_content
    assert "go mod download" in result.dockerfile_content
    assert "go build" in result.dockerfile_content
    assert "EXPOSE" in result.dockerfile_content


@pytest.mark.asyncio
async def test_generate_dockerfile_with_custom_instructions(python_project_dir: Path) -> None:
    """Test generating Dockerfile with custom instructions."""
    scanner = RepositoryScanner()
    generator = DockerfileGenerator()

    # Scan the project first
    scan_result = await scanner.scan_repository(str(python_project_dir))
    assert scan_result.success
    assert scan_result.analysis is not None

    # Generate Dockerfile with custom instructions
    request = DockerfileGenerationRequest(
        project_path=python_project_dir,
        custom_instructions=["ENV DEBUG=1", "RUN apt-get update"]
    )

    result = await generator.generate_dockerfile(request, scan_result.analysis)

    assert result.success
    assert result.dockerfile_content is not None
    assert "ENV DEBUG=1" in result.dockerfile_content
    assert "RUN apt-get update" in result.dockerfile_content
