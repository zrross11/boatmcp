"""Dockerfile generation utilities."""

import re
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..core.analysis import ProjectAnalysis

# Set up Jinja2 environment
template_dir = Path(__file__).parent.parent / "templates" / "dockerfile"
env = Environment(loader=FileSystemLoader(template_dir))


def generate_dockerfile_content(
    analysis: ProjectAnalysis,
    port: int = 80,
    optimize_for_size: bool = False,
    multi_stage: bool = False,
    custom_instructions: list[str] | None = None,
) -> str:
    """
    Generate Dockerfile content based on project analysis.

    Args:
        analysis: Project analysis results
        port: Port the application will expose
        optimize_for_size: Whether to optimize for smaller image size
        multi_stage: Whether to use multi-stage builds
        custom_instructions: Optional custom build instructions

    Returns:
        Complete Dockerfile content as a string
    """
    project_type = analysis.project_type
    template_name = f"{project_type}.dockerfile.j2"

    # Fallback to generic template if specific one doesn't exist
    if not (template_dir / template_name).exists():
        template_name = "generic.dockerfile.j2"

    template = env.get_template(template_name)

    # Base image selection
    base_images = {
        "python": "python:3.11-slim" if optimize_for_size else "python:3.11",
        "node.js": "node:18-alpine" if optimize_for_size else "node:18",
        "go": f"golang:{_detect_go_version()}{'-alpine' if optimize_for_size else ''}",
        "rust": "rust:1.70-slim" if optimize_for_size else "rust:1.70",
        "java": "openjdk:11-jre-slim" if optimize_for_size else "openjdk:11",
        "generic": "alpine:latest",
    }
    base_image = base_images.get(project_type, "alpine:latest")

    # Main file detection
    main_file_map = {
        "python": "main.py"
        if "main.py" in analysis.project_files
        else "server.py"
        if "server.py" in analysis.project_files
        else "app.py",
        "node.js": "server.js"
        if "server.js" in analysis.project_files
        else "app.js"
        if "app.js" in analysis.project_files
        else "index.js",
    }
    main_file = main_file_map.get(project_type, "app")

    context = {
        "analysis": analysis,
        "port": port,
        "optimize_for_size": optimize_for_size,
        "multi_stage": multi_stage,
        "custom_instructions": custom_instructions,
        "base_image": base_image,
        "main_file": main_file,
        "go_version": _detect_go_version() if project_type == "go" else None,
    }

    return template.render(context)


def _detect_go_version() -> str:
    """
    Detect the user's installed Go version.

    Returns:
        Go version string (e.g., "1.24.4") or default "1.21" if detection fails
    """
    try:
        # Run 'go version' command
        result = subprocess.run(
            ["go", "version"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            # Parse output like "go version go1.24.4 darwin/arm64"
            version_output = result.stdout.strip()
            # Extract version using regex - look for "go" followed by version number
            match = re.search(r"go version go(\d+\.\d+(?:\.\d+)?)", version_output)
            if match:
                return match.group(1)

        # If parsing fails, fall back to default
        return "1.21"

    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        FileNotFoundError,
    ):
        # If go command fails or doesn't exist, use default version
        return "1.21"


async def save_dockerfile(project_path: Path, dockerfile_content: str) -> str:
    """
    Save Dockerfile content to project directory.

    Args:
        project_path: Path to project directory
        dockerfile_content: Content to save

    Returns:
        Success or error message
    """
    try:
        dockerfile_path = project_path / "Dockerfile"

        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        return f"✅ Dockerfile saved successfully to: {dockerfile_path}"

    except Exception as e:
        return f"❌ Error saving Dockerfile: {str(e)}"
