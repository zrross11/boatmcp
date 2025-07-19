"""Tests for workflow functions."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from boatmcp.workflows.deployment import MinikubeDeploymentWorkflow
from boatmcp.workflows.schemas import (
    DeploymentWorkflowRequest,
)


class TestMinikubeDeploymentWorkflow:
    """Test the minikube deployment workflow."""

    @pytest.fixture
    def workflow(self):
        """Create a workflow instance for testing."""
        return MinikubeDeploymentWorkflow()

    @pytest.fixture
    def workflow_request(self, python_project_dir):
        """Create a deployment workflow request for testing."""
        return DeploymentWorkflowRequest(
            project_path=python_project_dir,
            app_name="test-app",
            namespace="default",
            image_tag="latest",
        )

    @pytest.mark.asyncio
    async def test_complete_workflow_success(self, workflow, workflow_request):
        """Test successful completion of the entire deployment workflow."""
        with patch.multiple(
            workflow,
            _generate_dockerfile=AsyncMock(return_value="✅ Dockerfile generated"),
            _build_docker_image=AsyncMock(return_value="✅ Image built"),
            _load_image_to_minikube=AsyncMock(return_value="✅ Image loaded"),
            _generate_helm_chart=AsyncMock(return_value="✅ Helm chart generated"),
            _deploy_helm_chart=AsyncMock(return_value="✅ Helm chart deployed"),
        ):
            result = await workflow.execute_workflow(workflow_request)

            assert result.success is True
            assert result.app_name == "test-app"
            assert result.namespace == "default"
            assert len(result.steps_completed) == 5
            assert (
                result.dockerfile_path == workflow_request.project_path / "Dockerfile"
            )
            assert (
                result.chart_path == workflow_request.project_path / "helm" / "test-app"
            )

    @pytest.mark.asyncio
    async def test_workflow_failure_at_dockerfile_generation(
        self, workflow, workflow_request
    ):
        """Test workflow failure during Dockerfile generation step."""
        with patch.object(
            workflow,
            "_generate_dockerfile",
            AsyncMock(return_value="❌ Failed to generate Dockerfile"),
        ):
            result = await workflow.execute_workflow(workflow_request)

            assert result.success is False
            assert "Failed to generate Dockerfile" in result.error
            assert len(result.steps_completed) == 0

    @pytest.mark.asyncio
    async def test_workflow_failure_at_image_build(self, workflow, workflow_request):
        """Test workflow failure during image build step."""
        with patch.multiple(
            workflow,
            _generate_dockerfile=AsyncMock(return_value="✅ Dockerfile generated"),
            _build_docker_image=AsyncMock(return_value="❌ Failed to build image"),
        ):
            result = await workflow.execute_workflow(workflow_request)

            assert result.success is False
            assert "Failed to build image" in result.error
            assert len(result.steps_completed) == 1
            assert "generate_dockerfile" in result.steps_completed

    @pytest.mark.asyncio
    async def test_workflow_with_custom_options(self, workflow, python_project_dir):
        """Test workflow with custom configuration options."""
        request = DeploymentWorkflowRequest(
            project_path=python_project_dir,
            app_name="custom-app",
            namespace="production",
            image_tag="v1.2.3",
            port=8080,
            optimize_for_size=True,
            multi_stage=True,
        )

        with patch.multiple(
            workflow,
            _generate_dockerfile=AsyncMock(return_value="✅ Dockerfile generated"),
            _build_docker_image=AsyncMock(return_value="✅ Image built"),
            _load_image_to_minikube=AsyncMock(return_value="✅ Image loaded"),
            _generate_helm_chart=AsyncMock(return_value="✅ Helm chart generated"),
            _deploy_helm_chart=AsyncMock(return_value="✅ Helm chart deployed"),
        ):
            result = await workflow.execute_workflow(request)

            assert result.success is True
            assert result.app_name == "custom-app"
            assert result.namespace == "production"
            assert result.image_tag == "v1.2.3"

    @pytest.mark.asyncio
    async def test_workflow_with_nonexistent_project_path(self, workflow):
        """Test workflow behavior with invalid project path."""
        request = DeploymentWorkflowRequest(
            project_path=Path("/nonexistent/path"),
            app_name="test-app",
            namespace="default",
            image_tag="latest",
        )

        result = await workflow.execute_workflow(request)

        assert result.success is False
        assert "Project path does not exist" in result.error

    @pytest.mark.asyncio
    async def test_get_progress_during_workflow(self, workflow, workflow_request):
        """Test getting progress information during workflow execution."""
        # Mock a partially completed workflow
        workflow._current_step = 2
        workflow._total_steps = 5
        workflow._step_results = ["✅ Dockerfile generated", "✅ Image built"]

        progress = workflow.get_progress()

        assert progress["current_step"] == 2
        assert progress["total_steps"] == 5
        assert progress["percentage"] == 40.0
        assert len(progress["completed_steps"]) == 2
