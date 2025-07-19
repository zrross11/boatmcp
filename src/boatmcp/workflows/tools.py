"""MCP tools for workflow orchestration."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastmcp import FastMCP

if TYPE_CHECKING:
    from ..core.config import BoatMCPConfig

from .deployment import MinikubeDeploymentWorkflow
from .schemas import DeploymentWorkflowRequest


def register_workflow_tools(mcp: FastMCP[Any], config: "BoatMCPConfig") -> None:
    """Register workflow-related MCP tools."""

    # Use config instead of environment variable
    enable_internal_tools = config.internal_tools

    workflow_manager = MinikubeDeploymentWorkflow()

    # Primary workflow tool (always visible)
    @mcp.tool()
    async def minikube_deployment_workflow(
        project_path: str,
        app_name: str,
        namespace: str = "default",
        image_tag: str = "latest",
        port: int = 80,
        optimize_for_size: bool = False,
        multi_stage: bool = False,
        custom_instructions: list[str] | None = None,
        minikube_profile: str = "boatmcp-cluster",
    ) -> str:
        """
        Execute a complete minikube deployment workflow from project to production.

        This one-stop-shop workflow orchestrates the entire deployment process:
        1. Analyzes project and generates optimized Dockerfile
        2. Builds Docker image locally
        3. Loads image into minikube cluster
        4. Generates Helm charts tailored to the application
        5. Deploys the application to minikube using Helm

        Args:
            project_path: Path to the project root directory
            app_name: Name for the application (used for image, chart, and release names)
            namespace: Kubernetes namespace to deploy to
            image_tag: Tag for the Docker image
            port: Port the application runs on
            optimize_for_size: Whether to optimize Dockerfile for smaller image size
            multi_stage: Whether to use multi-stage builds in Dockerfile
            custom_instructions: Optional list of custom Dockerfile requirements
            minikube_profile: Name of the minikube cluster profile to use

        Returns:
            Detailed status message with workflow execution results
        """
        try:
            # Ensure we're working with absolute path
            abs_project_path = Path(project_path).resolve()

            # Create workflow request
            request = DeploymentWorkflowRequest(
                project_path=abs_project_path,
                app_name=app_name,
                namespace=namespace,
                image_tag=image_tag,
                port=port,
                optimize_for_size=optimize_for_size,
                multi_stage=multi_stage,
                custom_instructions=custom_instructions,
                minikube_profile=minikube_profile,
            )

            # Execute the workflow
            result = await workflow_manager.execute_workflow(request)

            # Format response message
            if result.success:
                output = []
                output.append(
                    "🚀 **Minikube Deployment Workflow Completed Successfully!**"
                )
                output.append(f"📱 **Application:** {result.app_name}")
                output.append(f"🏷️  **Image Tag:** {result.image_tag}")
                output.append(f"📂 **Namespace:** {result.namespace}")
                output.append(f"📁 **Project Path:** {abs_project_path}")

                if result.dockerfile_path:
                    output.append(f"🐳 **Dockerfile:** {result.dockerfile_path}")

                if result.chart_path:
                    output.append(f"⚓ **Helm Chart:** {result.chart_path}")

                output.append("\n✅ **Completed Steps:**")
                for i, step in enumerate(result.steps_completed or [], 1):
                    output.append(f"   {i}. {step.replace('_', ' ').title()}")

                output.append(
                    "\n🎯 **Your application is now deployed and running in minikube!**"
                )
                output.append(
                    f"🔍 **To view your deployment:** `kubectl get pods -n {result.namespace}`"
                )
                output.append(
                    f"🌐 **To access your app:** `minikube service {result.app_name} -n {result.namespace} -p {minikube_profile}`"
                )

                if result.warnings:
                    output.append("\n⚠️  **Warnings:**")
                    for warning in result.warnings:
                        output.append(f"   - {warning}")

                return "\n".join(output)
            else:
                output = []
                output.append("❌ **Minikube Deployment Workflow Failed**")
                output.append(f"📱 **Application:** {result.app_name}")
                output.append(f"📂 **Namespace:** {result.namespace}")
                output.append(f"📁 **Project Path:** {abs_project_path}")

                if result.steps_completed:
                    output.append("\n✅ **Steps Completed Before Failure:**")
                    for i, step in enumerate(result.steps_completed or [], 1):
                        output.append(f"   {i}. {step.replace('_', ' ').title()}")

                output.append(f"\n💥 **Error:** {result.error}")
                output.append("\n🔧 **Troubleshooting Tips:**")
                output.append("   - Ensure minikube is running: `minikube status`")
                output.append("   - Check Docker is available: `docker --version`")
                output.append("   - Verify project structure contains necessary files")

                return "\n".join(output)

        except Exception as e:
            return f"❌ Workflow execution failed with unexpected error: {str(e)}"

    # Internal progress tool (gated behind environment variable)
    if enable_internal_tools:

        @mcp.tool()
        async def get_workflow_progress() -> str:
            """
            Get the current progress of the minikube deployment workflow.

            Returns:
                Progress information including current step, percentage complete, and completed steps
            """
            try:
                progress = workflow_manager.get_progress()

                output = []
                output.append("📊 **Workflow Progress**")
                output.append(
                    f"🎯 **Current Step:** {progress['current_step']} of {progress['total_steps']}"
                )
                output.append(f"📈 **Progress:** {progress['percentage']:.1f}%")

                if progress["completed_steps"]:
                    output.append("\n✅ **Completed Steps:**")
                    for i, step_result in enumerate(progress["completed_steps"], 1):
                        # Extract the key info from step result
                        if "✅" in step_result:
                            status = "✅ Completed"
                        elif "❌" in step_result:
                            status = "❌ Failed"
                        else:
                            status = "🔄 In Progress"

                        output.append(f"   {i}. {status}")

                return "\n".join(output)

            except Exception as e:
                return f"❌ Error getting workflow progress: {str(e)}"
