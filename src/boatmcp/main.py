"""Main entry point for BoatMCP server."""

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from .schemas.docker import DockerfileGenerationRequest
from .schemas.helm import HelmDeploymentRequest, HelmGenerationRequest
from .services import DockerfileGenerator, RepositoryScanner
from .services.helm import HelmDeployer, HelmGenerator

# Initialize FastMCP server
mcp: FastMCP[Any] = FastMCP("boatmcp")

# Initialize services
repository_scanner = RepositoryScanner()
dockerfile_generator = DockerfileGenerator()
helm_generator = HelmGenerator()
helm_deployer = HelmDeployer()


@mcp.tool()
async def scan_repository(path: str) -> str:
    """
    Scan a repository to analyze its structure, dependencies, and project type.

    Args:
        path: Path to the repository root directory

    Returns:
        Detailed analysis of the repository structure and contents
    """
    try:
        # Ensure we're working with absolute path
        abs_path = Path(path).resolve()
        result = await repository_scanner.scan_repository(str(abs_path))

        if not result.success:
            return f"❌ Failed to scan repository: {result.error}"

        analysis = result.analysis
        if analysis is None:
            return "❌ Failed to scan repository: No analysis data returned"

        # Format the analysis results
        output = []
        output.append("✅ Repository scanned successfully!")
        output.append(f"📁 Project root: {analysis.root_path}")
        output.append(f"🏷️  Project type: {analysis.project_type}")
        output.append(f"💻 Language: {analysis.language}")

        if analysis.framework:
            output.append(f"🚀 Framework: {analysis.framework}")

        if analysis.package_manager:
            output.append(f"📦 Package manager: {analysis.package_manager}")

        if analysis.dependencies:
            output.append(f"📋 Dependencies ({len(analysis.dependencies)}): {', '.join(analysis.dependencies[:5])}")
            if len(analysis.dependencies) > 5:
                output.append(f"    ... and {len(analysis.dependencies) - 5} more")

        if analysis.entry_points:
            output.append(f"🎯 Entry points: {', '.join(analysis.entry_points)}")

        output.append(f"📊 Files analyzed: {result.files_scanned}")
        output.append(f"   - Source files: {len(analysis.source_files or [])}")
        output.append(f"   - Config files: {len(analysis.config_files or [])}")
        output.append(f"   - Static files: {len(analysis.static_files or [])}")

        # List scanned files for verification
        output.append("\n📄 Scanned files:")
        all_files = (analysis.source_files or []) + (analysis.config_files or [])
        for file_info in all_files[:10]:  # Show first 10 files
            rel_path = file_info.path.relative_to(analysis.root_path)
            output.append(f"   - {rel_path}")
        if len(all_files) > 10:
            output.append(f"   ... and {len(all_files) - 10} more files")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error scanning repository: {str(e)}"


@mcp.tool()
async def generate_dockerfile(
    project_path: str,
    output_path: str | None = None,
    optimize_for_size: bool = False,
    multi_stage: bool = False,
    custom_instructions: str | None = None
) -> str:
    """
    Generate a Dockerfile based on intelligent analysis of the project structure.

    Args:
        project_path: Path to the project root directory
        output_path: Optional path where to save the Dockerfile (defaults to project_path/Dockerfile)
        optimize_for_size: Whether to optimize for smaller image size
        multi_stage: Whether to use multi-stage build (for supported languages)
        custom_instructions: Optional custom Dockerfile instructions to append

    Returns:
        Status message with Dockerfile generation results
    """
    try:
        # Ensure we're working with absolute path
        abs_project_path = Path(project_path).resolve()

        # First scan the repository
        scan_result = await repository_scanner.scan_repository(str(abs_project_path))

        if not scan_result.success:
            return f"❌ Failed to scan project: {scan_result.error}"

        analysis = scan_result.analysis
        if analysis is None:
            return "❌ Failed to scan project: No analysis data returned"

        # Prepare generation request
        custom_instructions_list = []
        if custom_instructions:
            custom_instructions_list = [line.strip() for line in custom_instructions.split('\n') if line.strip()]

        # If output_path is provided, make it absolute. Otherwise, default to scanned directory
        final_output_path = None
        if output_path:
            final_output_path = Path(output_path).resolve()

        request = DockerfileGenerationRequest(
            project_path=abs_project_path,
            output_path=final_output_path,
            optimize_for_size=optimize_for_size,
            multi_stage=multi_stage,
            custom_instructions=custom_instructions_list
        )

        # Generate Dockerfile
        result = await dockerfile_generator.generate_dockerfile(request, analysis)

        if not result.success:
            return f"❌ Failed to generate Dockerfile: {result.error}"

        output = []
        output.append("✅ Dockerfile generated successfully!")
        output.append(f"📁 Location: {result.dockerfile_path}")
        output.append(f"🏷️  Based on: {analysis.project_type} project")

        if analysis.framework:
            output.append(f"🚀 Framework: {analysis.framework}")

        if result.warnings:
            output.append("⚠️  Warnings:")
            for warning in result.warnings:
                output.append(f"   - {warning}")

        output.append("\n📋 Generated Dockerfile:")
        output.append("=" * 50)
        output.append(result.dockerfile_content or "")
        output.append("=" * 50)

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error generating Dockerfile: {str(e)}"


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
    import subprocess

    try:
        cmd = [
            "minikube", "start",
            "--profile", profile,
            "--cpus", str(cpus),
            "--memory", memory,
            "--disk-size", disk_size,
            "--driver", driver
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            output = []
            output.append(f"✅ Minikube cluster '{profile}' created successfully!")
            output.append(f"🖥️  Driver: {driver}")
            output.append(f"💻 CPUs: {cpus}")
            output.append(f"💾 Memory: {memory}")
            output.append(f"💿 Disk: {disk_size}")
            output.append("\n📋 Cluster details:")
            output.append(result.stdout)
            return "\n".join(output)
        else:
            return f"❌ Failed to create minikube cluster '{profile}': {result.stderr}"

    except subprocess.TimeoutExpired:
        return f"❌ Timeout creating minikube cluster '{profile}' (exceeded 5 minutes)"
    except Exception as e:
        return f"❌ Error creating minikube cluster '{profile}': {str(e)}"


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
    import subprocess

    try:
        cmd = ["minikube", "delete", "--profile", profile]
        if purge:
            cmd.append("--purge")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            output = []
            output.append(f"✅ Minikube cluster '{profile}' deleted successfully!")
            if purge:
                output.append("🗑️  Cached images and configs purged")
            output.append("\n📋 Deletion details:")
            output.append(result.stdout)
            return "\n".join(output)
        else:
            return f"❌ Failed to delete minikube cluster '{profile}': {result.stderr}"

    except subprocess.TimeoutExpired:
        return f"❌ Timeout deleting minikube cluster '{profile}' (exceeded 2 minutes)"
    except Exception as e:
        return f"❌ Error deleting minikube cluster '{profile}': {str(e)}"


@mcp.tool()
async def build_docker_image(
    project_path: str,
    image_name: str,
    image_tag: str = "latest",
    dockerfile_path: str | None = None
) -> str:
    """
    Build a Docker image from a project directory.

    Args:
        project_path: Path to the project root directory
        image_name: Name for the Docker image
        image_tag: Tag for the Docker image
        dockerfile_path: Optional path to Dockerfile (defaults to project_path/Dockerfile)

    Returns:
        Status message with build results
    """
    import subprocess

    try:
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory does not exist: {project_path}"

        dockerfile = Path(dockerfile_path) if dockerfile_path else project_dir / "Dockerfile"
        if not dockerfile.exists():
            return f"❌ Dockerfile not found: {dockerfile}"

        # Build the image
        cmd = [
            "docker", "build",
            "-t", f"{image_name}:{image_tag}",
            "-f", str(dockerfile),
            str(project_dir)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            output = []
            output.append("✅ Docker image built successfully!")
            output.append(f"🏷️  Image: {image_name}:{image_tag}")
            output.append(f"📁 Context: {project_dir}")
            output.append(f"📄 Dockerfile: {dockerfile}")
            output.append("\n📋 Build output:")
            output.append(result.stdout[-1000:])  # Last 1000 chars to avoid too much output
            return "\n".join(output)
        else:
            return f"❌ Failed to build Docker image: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "❌ Timeout building Docker image (exceeded 10 minutes)"
    except Exception as e:
        return f"❌ Error building Docker image: {str(e)}"


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

        # First scan the repository
        scan_result = await repository_scanner.scan_repository(str(abs_project_path))

        if not scan_result.success:
            return f"❌ Failed to scan project: {scan_result.error}"

        analysis = scan_result.analysis
        if analysis is None:
            return "❌ Failed to scan project: No analysis data returned"

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

        # Generate Helm chart
        result = await helm_generator.generate_helm_chart(request, analysis)

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


def main() -> None:
    """Main entry point for the BoatMCP server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
