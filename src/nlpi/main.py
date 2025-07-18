"""Main entry point for nlpi MCP server."""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional

from .services import RepositoryScanner, DockerfileGenerator
from .schemas.docker import DockerfileGenerationRequest


# Initialize FastMCP server
mcp = FastMCP("nlpi")

# Initialize services
repository_scanner = RepositoryScanner()
dockerfile_generator = DockerfileGenerator()


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
        
        # Format the analysis results
        output = []
        output.append(f"✅ Repository scanned successfully!")
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
        output.append(f"   - Source files: {len(analysis.source_files)}")
        output.append(f"   - Config files: {len(analysis.config_files)}")
        output.append(f"   - Static files: {len(analysis.static_files)}")
        
        # List scanned files for verification
        output.append(f"\n📄 Scanned files:")
        for file_info in (analysis.source_files + analysis.config_files)[:10]:  # Show first 10 files
            rel_path = file_info.path.relative_to(analysis.root_path)
            output.append(f"   - {rel_path}")
        if len(analysis.source_files + analysis.config_files) > 10:
            output.append(f"   ... and {len(analysis.source_files + analysis.config_files) - 10} more files")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"❌ Error scanning repository: {str(e)}"


@mcp.tool()
async def generate_dockerfile(
    project_path: str,
    output_path: Optional[str] = None,
    optimize_for_size: bool = False,
    multi_stage: bool = False,
    custom_instructions: Optional[str] = None
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
        output.append(f"✅ Dockerfile generated successfully!")
        output.append(f"📁 Location: {result.dockerfile_path}")
        output.append(f"🏷️  Based on: {analysis.project_type} project")
        
        if analysis.framework:
            output.append(f"🚀 Framework: {analysis.framework}")
        
        if result.warnings:
            output.append(f"⚠️  Warnings:")
            for warning in result.warnings:
                output.append(f"   - {warning}")
        
        output.append(f"\n📋 Generated Dockerfile:")
        output.append("=" * 50)
        output.append(result.dockerfile_content)
        output.append("=" * 50)
        
        return "\n".join(output)
        
    except Exception as e:
        return f"❌ Error generating Dockerfile: {str(e)}"


@mcp.tool()
async def create_minikube_cluster(
    profile: str = "nlpi-cluster",
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
            output.append(f"\n📋 Cluster details:")
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
            output.append(f"\n📋 Deletion details:")
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
    dockerfile_path: Optional[str] = None
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
            output.append(f"✅ Docker image built successfully!")
            output.append(f"🏷️  Image: {image_name}:{image_tag}")
            output.append(f"📁 Context: {project_dir}")
            output.append(f"📄 Dockerfile: {dockerfile}")
            output.append(f"\n📋 Build output:")
            output.append(result.stdout[-1000:])  # Last 1000 chars to avoid too much output
            return "\n".join(output)
        else:
            return f"❌ Failed to build Docker image: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"❌ Timeout building Docker image (exceeded 10 minutes)"
    except Exception as e:
        return f"❌ Error building Docker image: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')