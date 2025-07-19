"""Tests for simplified Dockerfile generator."""

from pathlib import Path

import pytest

from boatmcp.docker import DockerfileGenerationRequest, DockerfileGenerator


class TestDockerfileGenerator:
    """Test suite for DockerfileGenerator."""

    @pytest.mark.asyncio
    async def test_detect_python_project(self, python_project_dir: Path) -> None:
        """Test that Python projects are detected correctly."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(project_path=python_project_dir)

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert result.dockerfile_content is not None
        assert "FROM python:" in result.dockerfile_content
        assert "requirements.txt" in result.dockerfile_content
        assert "pip install" in result.dockerfile_content
        assert "EXPOSE 8000" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_detect_go_project(self, go_project_dir: Path) -> None:
        """Test that Go projects are detected correctly."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(project_path=go_project_dir)

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert result.dockerfile_content is not None
        assert "FROM golang:" in result.dockerfile_content
        assert "go.mod" in result.dockerfile_content
        assert "go build" in result.dockerfile_content
        assert "EXPOSE 8080" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_python_optimize_for_size(self, python_project_dir: Path) -> None:
        """Test Python Dockerfile with size optimization."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(
            project_path=python_project_dir,
            optimize_for_size=True
        )

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert "python:3.11-alpine" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_python_without_size_optimization(self, python_project_dir: Path) -> None:
        """Test Python Dockerfile without size optimization."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(
            project_path=python_project_dir,
            optimize_for_size=False
        )

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert "python:3.11-slim" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_go_multi_stage_build(self, go_project_dir: Path) -> None:
        """Test Go Dockerfile with multi-stage build."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(
            project_path=go_project_dir,
            multi_stage=True
        )

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert "AS builder" in result.dockerfile_content
        assert "FROM alpine:latest" in result.dockerfile_content
        assert "COPY --from=builder" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_custom_instructions(self, python_project_dir: Path) -> None:
        """Test adding custom instructions to Dockerfile."""
        generator = DockerfileGenerator()
        custom_instructions = ["ENV DEBUG=1", "RUN apt-get update"]
        request = DockerfileGenerationRequest(
            project_path=python_project_dir,
            custom_instructions=custom_instructions
        )

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert "# Custom instructions" in result.dockerfile_content
        assert "ENV DEBUG=1" in result.dockerfile_content
        assert "RUN apt-get update" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_generic_project(self, temp_project_dir: Path) -> None:
        """Test generic Dockerfile for unknown project types."""
        # Create a project with no recognizable files
        unknown_project = temp_project_dir / "unknown_project"
        unknown_project.mkdir()
        (unknown_project / "some_file.txt").write_text("Hello world")

        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(project_path=unknown_project)

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert "FROM ubuntu:22.04" in result.dockerfile_content
        assert "COPY . ." in result.dockerfile_content
        assert "Please configure the command" in result.dockerfile_content

    @pytest.mark.asyncio
    async def test_dockerfile_saved_to_project(self, python_project_dir: Path) -> None:
        """Test that Dockerfile is saved to the project directory."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(project_path=python_project_dir)

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert result.dockerfile_path == python_project_dir / "Dockerfile"
        assert (python_project_dir / "Dockerfile").exists()

        # Verify content was written correctly
        written_content = (python_project_dir / "Dockerfile").read_text()
        assert written_content == result.dockerfile_content

    @pytest.mark.asyncio
    async def test_custom_output_path(self, python_project_dir: Path) -> None:
        """Test saving Dockerfile to custom output path."""
        custom_path = python_project_dir / "custom" / "MyDockerfile"
        custom_path.parent.mkdir(exist_ok=True)

        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(
            project_path=python_project_dir,
            output_path=custom_path
        )

        result = await generator.generate_dockerfile(request)

        assert result.success
        assert result.dockerfile_path == custom_path
        assert custom_path.exists()

    @pytest.mark.asyncio
    async def test_nonexistent_project_path(self) -> None:
        """Test error handling for nonexistent project path."""
        generator = DockerfileGenerator()
        request = DockerfileGenerationRequest(project_path=Path("/nonexistent/path"))

        result = await generator.generate_dockerfile(request)

        assert not result.success
        assert result.error is not None
        assert "Error generating Dockerfile" in result.error


class TestProjectTypeDetection:
    """Test suite for project type detection logic."""

    def test_detect_python_with_requirements_txt(self, temp_project_dir: Path) -> None:
        """Test Python detection with requirements.txt."""
        project = temp_project_dir / "python_req"
        project.mkdir()
        (project / "requirements.txt").write_text("flask==2.0.0")

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "python"

    def test_detect_python_with_pyproject_toml(self, temp_project_dir: Path) -> None:
        """Test Python detection with pyproject.toml."""
        project = temp_project_dir / "python_pyproject"
        project.mkdir()
        (project / "pyproject.toml").write_text("[tool.poetry]")

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "python"

    def test_detect_node_with_package_json(self, temp_project_dir: Path) -> None:
        """Test Node.js detection with package.json."""
        project = temp_project_dir / "node_project"
        project.mkdir()
        (project / "package.json").write_text('{"name": "test"}')

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "node"

    def test_detect_go_with_go_mod(self, temp_project_dir: Path) -> None:
        """Test Go detection with go.mod."""
        project = temp_project_dir / "go_project"
        project.mkdir()
        (project / "go.mod").write_text("module test")

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "go"

    def test_detect_java_with_pom_xml(self, temp_project_dir: Path) -> None:
        """Test Java detection with pom.xml."""
        project = temp_project_dir / "java_project"
        project.mkdir()
        (project / "pom.xml").write_text("<project></project>")

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "java"

    def test_detect_rust_with_cargo_toml(self, temp_project_dir: Path) -> None:
        """Test Rust detection with Cargo.toml."""
        project = temp_project_dir / "rust_project"
        project.mkdir()
        (project / "Cargo.toml").write_text("[package]")

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "rust"

    def test_detect_generic_unknown_project(self, temp_project_dir: Path) -> None:
        """Test generic detection for unknown project types."""
        project = temp_project_dir / "unknown_project"
        project.mkdir()
        (project / "random_file.txt").write_text("content")

        generator = DockerfileGenerator()
        project_type = generator._detect_project_type(project)

        assert project_type == "generic"
