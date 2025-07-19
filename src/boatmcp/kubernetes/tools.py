"""Kubernetes-related MCP tools (Helm and Minikube)."""

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from .deployer import HelmDeployer
from .helm import HelmGenerator
from .minikube import MinikubeManager
from .schemas import HelmDeploymentRequest, HelmGenerationRequest


def register_kubernetes_tools(mcp: FastMCP[Any]) -> None:
    """Register all Kubernetes-related MCP tools."""

    # Initialize services
    helm_generator = HelmGenerator()
    helm_deployer = HelmDeployer()
    minikube_manager = MinikubeManager()

    @mcp.tool()
    async def generate_helm_chart(
        project_path: str,
        chart_name: str,
        app_version: str = "1.0.0",
        chart_version: str = "0.1.0",
        image_name: str | None = None,
        image_tag: str = "latest",
        port: int = 80,
        namespace: str = "default"
    ) -> str:
        """
        Generate a Helm chart for a project.

        Args:
            project_path: Path to the project root directory
            chart_name: Name for the Helm chart
            app_version: Version of the application
            chart_version: Version of the Helm chart
            image_name: Name of the Docker image (defaults to chart_name)
            image_tag: Tag for the Docker image
            port: Port the application runs on
            namespace: Kubernetes namespace

        Returns:
            Status message with Helm chart generation results
        """
        try:
            # Ensure we're working with absolute path
            abs_project_path = Path(project_path).resolve()

            # Use chart_name as image_name if not provided
            if image_name is None:
                image_name = chart_name

            # Prepare generation request
            request = HelmGenerationRequest(
                project_path=abs_project_path,
                chart_name=chart_name,
                app_version=app_version,
                chart_version=chart_version,
                image_name=image_name,
                image_tag=image_tag,
                port=port,
                namespace=namespace
            )

            # Generate Helm chart (without analysis for now)
            result = await helm_generator.generate_helm_chart(request, None)

            if not result.success:
                return f"❌ Failed to generate Helm chart: {result.error}"

            output = []
            output.append("✅ Helm chart generated successfully!")
            output.append(f"📁 Chart location: {result.chart_path}")
            output.append(f"📦 Chart name: {chart_name}")
            output.append(f"🏷️  App version: {app_version}")
            output.append(f"🐳 Image: {image_name}:{image_tag}")
            output.append(f"🔌 Port: {port}")
            output.append(f"📂 Namespace: {namespace}")

            if result.warnings:
                output.append("⚠️  Warnings:")
                for warning in result.warnings:
                    output.append(f"   - {warning}")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error generating Helm chart: {str(e)}"

    @mcp.tool()
    async def deploy_helm_chart(
        chart_path: str,
        release_name: str,
        namespace: str = "default",
        wait: bool = True,
        timeout: int = 300,
        image_tag: str | None = None
    ) -> str:
        """
        Deploy a Helm chart to the minikube cluster.

        Args:
            chart_path: Path to the Helm chart directory
            release_name: Name for the Helm release
            namespace: Kubernetes namespace to deploy to
            wait: Whether to wait for the deployment to complete
            timeout: Timeout in seconds for the deployment
            image_tag: Optional image tag override

        Returns:
            Status message with deployment results
        """
        try:
            # Ensure we're working with absolute path
            abs_chart_path = Path(chart_path).resolve()

            # Prepare deployment request
            values_overrides = {}
            if image_tag:
                values_overrides["image.tag"] = image_tag

            request = HelmDeploymentRequest(
                chart_path=abs_chart_path,
                release_name=release_name,
                namespace=namespace,
                values_overrides=values_overrides,
                wait=wait,
                timeout=timeout
            )

            # Deploy Helm chart
            result = await helm_deployer.deploy_helm_chart(request)

            if not result.success:
                return f"❌ Failed to deploy Helm chart: {result.error}"

            output = []
            output.append("✅ Helm chart deployed successfully!")
            output.append(f"🚀 Release name: {result.release_name}")
            output.append(f"📂 Namespace: {result.namespace}")
            output.append(f"📁 Chart path: {abs_chart_path}")

            if result.warnings:
                output.append("⚠️  Warnings:")
                for warning in result.warnings:
                    output.append(f"   - {warning}")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error deploying Helm chart: {str(e)}"

    @mcp.tool()
    async def uninstall_helm_chart(
        release_name: str,
        namespace: str = "default"
    ) -> str:
        """
        Uninstall a Helm chart release from the minikube cluster.

        Args:
            release_name: Name of the Helm release to uninstall
            namespace: Kubernetes namespace the release is in

        Returns:
            Status message with uninstall results
        """
        try:
            # Uninstall Helm chart
            result = await helm_deployer.uninstall_helm_chart(release_name, namespace)

            if not result.success:
                return f"❌ Failed to uninstall Helm chart: {result.error}"

            output = []
            output.append("✅ Helm chart uninstalled successfully!")
            output.append(f"🗑️  Release name: {result.release_name}")
            output.append(f"📂 Namespace: {result.namespace}")

            if result.warnings:
                output.append("⚠️  Warnings:")
                for warning in result.warnings:
                    output.append(f"   - {warning}")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error uninstalling Helm chart: {str(e)}"

    @mcp.tool()
    async def create_minikube_cluster(
        profile: str = "boatmcp-cluster",
        cpus: int = 2,
        memory: str = "2048mb",
        disk_size: str = "20gb",
        driver: str = "docker"
    ) -> str:
        """
        Create a new minikube cluster for local Kubernetes development.

        Args:
            profile: Name of the minikube profile/cluster
            cpus: Number of CPUs to allocate
            memory: Amount of memory to allocate
            disk_size: Disk size for the cluster
            driver: Minikube driver to use (docker, virtualbox, etc.)

        Returns:
            Status message with cluster creation results
        """
        return await minikube_manager.create_cluster(
            profile=profile,
            cpus=cpus,
            memory=memory,
            disk_size=disk_size,
            driver=driver
        )

    @mcp.tool()
    async def delete_minikube_cluster(profile: str, purge: bool = False) -> str:
        """
        Delete a minikube cluster.

        Args:
            profile: Name of the minikube profile/cluster to delete
            purge: Whether to purge all cached images and configs

        Returns:
            Status message with deletion results
        """
        return await minikube_manager.delete_cluster(profile=profile, purge=purge)
