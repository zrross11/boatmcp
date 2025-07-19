"""Minikube deployment workflow orchestration."""

import subprocess
from typing import Any

from ..core.analysis import analyze_project
from ..docker.generator import generate_dockerfile_content, save_dockerfile
from ..kubernetes.generator import deploy_helm_chart, generate_helm_chart
from ..kubernetes.minikube import load_image_into_minikube
from .schemas import DeploymentWorkflowRequest, DeploymentWorkflowResult


class MinikubeDeploymentWorkflow:
    """Orchestrates the complete minikube deployment workflow."""

    def __init__(self) -> None:
        self._current_step = 0
        self._total_steps = 5
        self._step_results: list[str] = []

    async def execute_workflow(
        self, request: DeploymentWorkflowRequest
    ) -> DeploymentWorkflowResult:
        """
        Execute the complete minikube deployment workflow.

        Args:
            request: Workflow configuration and parameters

        Returns:
            Result of the workflow execution
        """
        try:
            # Validate project path
            if not request.project_path.exists():
                return DeploymentWorkflowResult(
                    success=False,
                    app_name=request.app_name,
                    namespace=request.namespace,
                    image_tag=request.image_tag,
                    error=f"Project path does not exist: {request.project_path}",
                )

            self._current_step = 0
            self._step_results = []
            steps_completed: list[str] = []

            # Step 1: Generate Dockerfile
            dockerfile_result = await self._generate_dockerfile(request)
            self._current_step += 1
            self._step_results.append(dockerfile_result)

            if "❌" in dockerfile_result:
                return DeploymentWorkflowResult(
                    success=False,
                    app_name=request.app_name,
                    namespace=request.namespace,
                    image_tag=request.image_tag,
                    steps_completed=steps_completed,
                    error=dockerfile_result,
                )

            steps_completed.append("generate_dockerfile")

            # Step 2: Build Docker image
            image_result = await self._build_docker_image(request)
            self._current_step += 1
            self._step_results.append(image_result)

            if "❌" in image_result:
                return DeploymentWorkflowResult(
                    success=False,
                    app_name=request.app_name,
                    namespace=request.namespace,
                    image_tag=request.image_tag,
                    steps_completed=steps_completed,
                    error=image_result,
                )

            steps_completed.append("build_docker_image")

            # Step 3: Load image into minikube
            load_result = await self._load_image_to_minikube(request)
            self._current_step += 1
            self._step_results.append(load_result)

            if "❌" in load_result:
                return DeploymentWorkflowResult(
                    success=False,
                    app_name=request.app_name,
                    namespace=request.namespace,
                    image_tag=request.image_tag,
                    steps_completed=steps_completed,
                    error=load_result,
                )

            steps_completed.append("load_image_to_minikube")

            # Step 4: Generate Helm chart
            helm_gen_result = await self._generate_helm_chart(request)
            self._current_step += 1
            self._step_results.append(helm_gen_result)

            if "❌" in helm_gen_result:
                return DeploymentWorkflowResult(
                    success=False,
                    app_name=request.app_name,
                    namespace=request.namespace,
                    image_tag=request.image_tag,
                    steps_completed=steps_completed,
                    error=helm_gen_result,
                )

            steps_completed.append("generate_helm_chart")

            # Step 5: Deploy Helm chart
            deploy_result = await self._deploy_helm_chart(request)
            self._current_step += 1
            self._step_results.append(deploy_result)

            if "❌" in deploy_result:
                return DeploymentWorkflowResult(
                    success=False,
                    app_name=request.app_name,
                    namespace=request.namespace,
                    image_tag=request.image_tag,
                    steps_completed=steps_completed,
                    error=deploy_result,
                )

            steps_completed.append("deploy_helm_chart")

            # Workflow completed successfully
            return DeploymentWorkflowResult(
                success=True,
                app_name=request.app_name,
                namespace=request.namespace,
                image_tag=request.image_tag,
                steps_completed=steps_completed,
                dockerfile_path=request.project_path / "Dockerfile",
                chart_path=request.project_path / "helm" / request.app_name,
            )

        except Exception as e:
            return DeploymentWorkflowResult(
                success=False,
                app_name=request.app_name,
                namespace=request.namespace,
                image_tag=request.image_tag,
                error=f"Workflow execution failed: {str(e)}",
            )

    def get_progress(self) -> dict[str, Any]:
        """Get current workflow progress information."""
        return {
            "current_step": self._current_step,
            "total_steps": self._total_steps,
            "percentage": (self._current_step / self._total_steps) * 100,
            "completed_steps": self._step_results.copy(),
        }

    async def _generate_dockerfile(self, request: DeploymentWorkflowRequest) -> str:
        """Generate Dockerfile for the project."""
        try:
            # Analyze the project
            analysis = await analyze_project(str(request.project_path))

            # Generate Dockerfile content
            dockerfile_content = generate_dockerfile_content(
                analysis=analysis,
                port=request.port,
                optimize_for_size=request.optimize_for_size,
                multi_stage=request.multi_stage,
                custom_instructions=request.custom_instructions,
            )

            # Save Dockerfile
            save_result = await save_dockerfile(
                request.project_path, dockerfile_content
            )

            if "✅" in save_result:
                return f"✅ Dockerfile generated successfully for {analysis.project_type} project"
            else:
                return save_result

        except Exception as e:
            return f"❌ Failed to generate Dockerfile: {str(e)}"

    async def _build_docker_image(self, request: DeploymentWorkflowRequest) -> str:
        """Build Docker image from the project."""
        try:
            dockerfile_path = request.project_path / "Dockerfile"
            if not dockerfile_path.exists():
                return f"❌ Dockerfile not found: {dockerfile_path}"

            # Build the image using docker command
            image_name = f"{request.app_name}:{request.image_tag}"
            cmd = [
                "docker",
                "build",
                "-t",
                image_name,
                "-f",
                str(dockerfile_path),
                str(request.project_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                return f"✅ Docker image built successfully: {image_name}"
            else:
                return f"❌ Failed to build Docker image: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "❌ Timeout building Docker image (exceeded 10 minutes)"
        except Exception as e:
            return f"❌ Failed to build Docker image: {str(e)}"

    async def _load_image_to_minikube(self, request: DeploymentWorkflowRequest) -> str:
        """Load the built image into minikube cluster."""
        try:
            image_name = f"{request.app_name}:{request.image_tag}"
            return await load_image_into_minikube(
                image_name=image_name, profile=request.minikube_profile
            )
        except Exception as e:
            return f"❌ Failed to load image into minikube: {str(e)}"

    async def _generate_helm_chart(self, request: DeploymentWorkflowRequest) -> str:
        """Generate Helm chart for the application."""
        try:
            result = generate_helm_chart(
                project_path=request.project_path,
                chart_name=request.app_name,
                app_version="1.0.0",
                chart_version="0.1.0",
                image_name=request.app_name,
                image_tag=request.image_tag,
                port=request.port,
                namespace=request.namespace,
            )

            if result["success"]:
                return f"✅ Helm chart generated successfully: {result['chart_path']}"
            else:
                return f"❌ Failed to generate Helm chart: {result['error']}"

        except Exception as e:
            return f"❌ Failed to generate Helm chart: {str(e)}"

    async def _deploy_helm_chart(self, request: DeploymentWorkflowRequest) -> str:
        """Deploy the Helm chart to minikube cluster."""
        try:
            chart_path = request.project_path / "helm" / request.app_name

            values_overrides = {}
            if request.image_tag:
                values_overrides["image.tag"] = request.image_tag

            result = deploy_helm_chart(
                chart_path=chart_path,
                release_name=request.app_name,
                namespace=request.namespace,
                values_overrides=values_overrides,
                wait=True,
                timeout=300,
            )

            if result["success"]:
                return f"✅ Helm chart deployed successfully: {result['release_name']}"
            else:
                return f"❌ Failed to deploy Helm chart: {result['error']}"

        except Exception as e:
            return f"❌ Failed to deploy Helm chart: {str(e)}"
