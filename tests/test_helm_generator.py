"""Tests for Helm chart generation functionality."""

from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from boatmcp.schemas.helm import (
    HelmDeploymentRequest,
    HelmGenerationRequest,
)
from boatmcp.schemas.repository import FileInfo, ProjectAnalysis
from boatmcp.services.helm.helm_deployer import HelmDeployer
from boatmcp.services.helm.helm_generator import HelmGenerator


def get_mock_repository_analysis(
    overrides: dict[str, Any] | None = None
) -> ProjectAnalysis:
    """Create a mock repository analysis with sensible defaults."""
    base_analysis = ProjectAnalysis(
        root_path=Path("/test/project"),
        project_type="python",
        language="python",
        framework="fastapi",
        package_manager="pip",
        dependencies=["fastapi", "uvicorn"],
        entry_points=["app.py"],
        source_files=[
            FileInfo(path=Path("/test/project/app.py"), size=1000)
        ],
        config_files=[
            FileInfo(path=Path("/test/project/requirements.txt"), size=100)
        ],
        static_files=[]
    )

    if overrides:
        return replace(base_analysis, **overrides)
    return base_analysis


def get_mock_helm_request(
    overrides: dict[str, Any] | None = None
) -> HelmGenerationRequest:
    """Create a mock helm generation request with sensible defaults."""
    base_request = HelmGenerationRequest(
        project_path=Path("/test/project"),
        chart_name="test-app",
        app_version="1.0.0",
        image_name="test-app",
        image_tag="latest"
    )

    if overrides:
        return replace(base_request, **overrides)
    return base_request


def get_mock_helm_deployment_request(
    overrides: dict[str, Any] | None = None
) -> HelmDeploymentRequest:
    """Create a mock helm deployment request with sensible defaults."""
    base_request = HelmDeploymentRequest(
        chart_path=Path("/test/project/helm/test-app"),
        release_name="test-app",
        namespace="default"
    )

    if overrides:
        return replace(base_request, **overrides)
    return base_request


class TestHelmGenerator:
    @pytest.fixture
    def helm_generator(self) -> HelmGenerator:
        return HelmGenerator()

    @pytest.mark.asyncio
    async def test_generate_helm_chart_creates_chart_directory(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that helm chart generation creates the helm directory structure."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({
            "project_path": project_path,
            "chart_name": "test-app"
        })

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        assert result.chart_path == project_path / "helm" / "test-app"
        assert (project_path / "helm" / "test-app").exists()
        assert (project_path / "helm" / "test-app" / "Chart.yaml").exists()
        assert (project_path / "helm" / "test-app" / "values.yaml").exists()
        assert (project_path / "helm" / "test-app" / "templates").exists()

    @pytest.mark.asyncio
    async def test_generate_helm_chart_creates_chart_yaml(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that Chart.yaml is created with correct content."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({
            "project_path": project_path,
            "chart_name": "my-app",
            "app_version": "2.0.0"
        })

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        chart_yaml = (project_path / "helm" / "my-app" / "Chart.yaml").read_text()
        assert "name: my-app" in chart_yaml
        assert "version: 0.1.0" in chart_yaml
        assert "appVersion: 2.0.0" in chart_yaml

    @pytest.mark.asyncio
    async def test_generate_helm_chart_creates_values_yaml(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that values.yaml is created with correct image configuration."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({
            "project_path": project_path,
            "image_name": "custom-app",
            "image_tag": "v1.2.3"
        })

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        values_yaml = (project_path / "helm" / "test-app" / "values.yaml").read_text()
        assert "repository: custom-app" in values_yaml
        assert "tag: v1.2.3" in values_yaml

    @pytest.mark.asyncio
    async def test_generate_helm_chart_creates_deployment_template(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that deployment template is created."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({"project_path": project_path})

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        deployment_path = project_path / "helm" / "test-app" / "templates" / "deployment.yaml"
        assert deployment_path.exists()
        deployment_content = deployment_path.read_text()
        assert "kind: Deployment" in deployment_content
        assert "{{ .Values.image.repository }}" in deployment_content

    @pytest.mark.asyncio
    async def test_generate_helm_chart_creates_service_template(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that service template is created."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({"project_path": project_path})

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        service_path = project_path / "helm" / "test-app" / "templates" / "service.yaml"
        assert service_path.exists()
        service_content = service_path.read_text()
        assert "kind: Service" in service_content

    @pytest.mark.asyncio
    async def test_generate_helm_chart_overwrites_existing_chart(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that existing chart files are overwritten."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        # Create existing helm directory with a file
        helm_dir = project_path / "helm" / "test-app"
        helm_dir.mkdir(parents=True)
        (helm_dir / "Chart.yaml").write_text("old content")

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({"project_path": project_path})

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        chart_content = (helm_dir / "Chart.yaml").read_text()
        assert "old content" not in chart_content
        assert "name: test-app" in chart_content

    @pytest.mark.asyncio
    async def test_generate_helm_chart_handles_custom_port(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test that custom port is used in templates."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({
            "project_path": project_path,
            "port": 8080
        })

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert result.success
        values_content = (project_path / "helm" / "test-app" / "values.yaml").read_text()
        assert "port: 8080" in values_content

    @pytest.mark.asyncio
    async def test_generate_helm_chart_handles_project_path_not_exist(self, helm_generator: HelmGenerator, tmp_path: Path) -> None:
        """Test error handling when project path doesn't exist."""
        project_path = tmp_path / "nonexistent"

        analysis = get_mock_repository_analysis({"root_path": project_path})
        request = get_mock_helm_request({"project_path": project_path})

        result = await helm_generator.generate_helm_chart(request, analysis)

        assert not result.success
        assert result.error is not None and "Project path does not exist" in result.error


class TestHelmDeployer:
    @pytest.fixture
    def helm_deployer(self) -> HelmDeployer:
        return HelmDeployer()

    @pytest.mark.asyncio
    async def test_deploy_helm_chart_success(self, helm_deployer: HelmDeployer, tmp_path: Path) -> None:
        """Test successful Helm chart deployment."""
        chart_path = tmp_path / "helm" / "test-app"
        chart_path.mkdir(parents=True)
        (chart_path / "Chart.yaml").write_text("name: test-app\nversion: 0.1.0")

        request = get_mock_helm_deployment_request({"chart_path": chart_path})

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Release 'test-app' deployed successfully"
            mock_run.return_value.stderr = ""

            result = await helm_deployer.deploy_helm_chart(request)

            assert result.success
            assert result.release_name == "test-app"
            assert result.namespace == "default"
            assert "deployed successfully" in mock_run.return_value.stdout

    @pytest.mark.asyncio
    async def test_deploy_helm_chart_handles_chart_not_exist(self, helm_deployer: HelmDeployer, tmp_path: Path) -> None:
        """Test error handling when chart path doesn't exist."""
        chart_path = tmp_path / "nonexistent"

        request = get_mock_helm_deployment_request({"chart_path": chart_path})

        result = await helm_deployer.deploy_helm_chart(request)

        assert not result.success
        assert result.error is not None and "Chart path does not exist" in result.error

    @pytest.mark.asyncio
    async def test_deploy_helm_chart_handles_deployment_failure(self, helm_deployer: HelmDeployer, tmp_path: Path) -> None:
        """Test error handling when helm deployment fails."""
        chart_path = tmp_path / "helm" / "test-app"
        chart_path.mkdir(parents=True)
        (chart_path / "Chart.yaml").write_text("name: test-app\nversion: 0.1.0")

        request = get_mock_helm_deployment_request({"chart_path": chart_path})

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Error: deployment failed"

            result = await helm_deployer.deploy_helm_chart(request)

            assert not result.success
            assert result.error is not None and "deployment failed" in result.error

    @pytest.mark.asyncio
    async def test_deploy_helm_chart_with_custom_values(self, helm_deployer: HelmDeployer, tmp_path: Path) -> None:
        """Test deployment with custom values override."""
        chart_path = tmp_path / "helm" / "test-app"
        chart_path.mkdir(parents=True)
        (chart_path / "Chart.yaml").write_text("name: test-app\nversion: 0.1.0")

        request = get_mock_helm_deployment_request({
            "chart_path": chart_path,
            "values_overrides": {"image.tag": "v1.2.3", "service.port": 8080}
        })

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Release deployed"
            mock_run.return_value.stderr = ""

            result = await helm_deployer.deploy_helm_chart(request)

            assert result.success
            # Check that the helm command included the custom values
            call_args = mock_run.call_args[0][0]
            assert "--set" in call_args
            assert "image.tag=v1.2.3" in call_args
            assert "service.port=8080" in call_args
