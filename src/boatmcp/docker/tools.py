"""Docker-related MCP tools."""

import subprocess
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from ..utils import read_project_files
from .generator import DockerfileGenerator
from .schemas import DockerfileGenerationRequest


def register_docker_tools(mcp: FastMCP[Any]) -> None:
    """Register all Docker-related MCP tools."""

    @mcp.tool()
    async def analyze_project(project_path: str) -> str:
        """
        Analyze a project directory and return all relevant file contents for Dockerfile generation.

        Args:
            project_path: Path to the project root directory

        Returns:
            Structured project analysis with file contents for Claude to generate Dockerfile
        """
        try:
            # Ensure we're working with absolute path
            abs_project_path = Path(project_path).resolve()

            if not abs_project_path.exists():
                return f"❌ Project path does not exist: {project_path}"

            if not abs_project_path.is_dir():
                return f"❌ Project path is not a directory: {project_path}"

            # Read all project files
            try:
                project_files = read_project_files(str(abs_project_path))
            except Exception as e:
                return f"❌ Failed to read project files: {str(e)}"

            if not project_files:
                return f"❌ No relevant files found in project directory: {project_path}"

            # Analyze file types and project characteristics
            file_extensions = set()
            has_requirements_txt = False
            has_package_json = False
            has_go_mod = False
            has_cargo_toml = False

            for file_path in project_files.keys():
                if "." in file_path:
                    ext = "." + file_path.split(".")[-1]
                    file_extensions.add(ext)

                if file_path.lower() == "requirements.txt":
                    has_requirements_txt = True
                elif file_path.lower() == "package.json":
                    has_package_json = True
                elif file_path.lower() == "go.mod":
                    has_go_mod = True
                elif file_path.lower() == "cargo.toml":
                    has_cargo_toml = True

            # Determine likely project type
            project_type = "unknown"
            if has_requirements_txt or ".py" in file_extensions:
                project_type = "python"
            elif has_package_json or ".js" in file_extensions or ".ts" in file_extensions:
                project_type = "node.js"
            elif has_go_mod or ".go" in file_extensions:
                project_type = "go"
            elif has_cargo_toml or ".rs" in file_extensions:
                project_type = "rust"

            # Format the response for Claude
            output = []
            output.append("🔍 **Project Analysis Complete**")
            output.append(f"📁 **Project Path:** {abs_project_path}")
            output.append(f"🏷️  **Detected Type:** {project_type}")
            output.append(f"📊 **Files Found:** {len(project_files)}")
            output.append(f"📋 **Extensions:** {', '.join(sorted(file_extensions))}")

            output.append("\n📄 **Project Files:**")
            output.append("=" * 60)

            for file_path, content in project_files.items():
                output.append(f"\n**{file_path}:**")
                output.append("```")
                output.append(content.strip())
                output.append("```")

            output.append("=" * 60)
            output.append("\n💡 **Next Steps:**")
            output.append("Based on this analysis, please generate a production-ready Dockerfile.")
            output.append("Once you've created the Dockerfile, use the 'save_dockerfile' tool to save it.")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error analyzing project: {str(e)}"

    @mcp.tool()
    async def save_dockerfile(project_path: str, dockerfile_content: str) -> str:
        """
        Save a Dockerfile to the project root directory.

        Args:
            project_path: Path to the project root directory
            dockerfile_content: Content of the Dockerfile to save

        Returns:
            Status message indicating success or failure
        """
        try:
            # Ensure we're working with absolute path
            abs_project_path = Path(project_path).resolve()

            if not abs_project_path.exists():
                return f"❌ Project path does not exist: {project_path}"

            if not abs_project_path.is_dir():
                return f"❌ Project path is not a directory: {project_path}"

            # Write Dockerfile to project root
            dockerfile_path = abs_project_path / "Dockerfile"

            with open(dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)

            return f"✅ Dockerfile saved successfully to: {dockerfile_path}"

        except Exception as e:
            return f"❌ Error saving Dockerfile: {str(e)}"

    @mcp.tool()
    async def generate_dockerfile(
        project_path: str,
        optimize_for_size: bool = False,
        multi_stage: bool = False,
        custom_instructions: list[str] | None = None,
        save_to_project: bool = True
    ) -> str:
        """
        Generate a Dockerfile for a project with automatic project type detection.

        Args:
            project_path: Path to the project root directory
            optimize_for_size: Whether to optimize the Dockerfile for smaller image size
            multi_stage: Whether to use multi-stage builds (where applicable)
            custom_instructions: Optional list of custom Dockerfile instructions to append
            save_to_project: Whether to save the Dockerfile to the project directory

        Returns:
            Generated Dockerfile content and status information
        """
        try:
            # Ensure we're working with absolute path
            abs_project_path = Path(project_path).resolve()

            if not abs_project_path.exists():
                return f"❌ Project path does not exist: {project_path}"

            if not abs_project_path.is_dir():
                return f"❌ Project path is not a directory: {project_path}"

            # Create generation request
            output_path = abs_project_path / "Dockerfile" if save_to_project else None
            request = DockerfileGenerationRequest(
                project_path=abs_project_path,
                output_path=output_path,
                custom_instructions=custom_instructions or [],
                optimize_for_size=optimize_for_size,
                multi_stage=multi_stage
            )

            # Generate Dockerfile
            generator = DockerfileGenerator()
            result = await generator.generate_dockerfile(request)

            if result.success:
                output = []
                output.append("✅ Dockerfile generated successfully!")
                output.append(f"📁 Project: {abs_project_path}")

                if save_to_project:
                    output.append(f"💾 Saved to: {result.dockerfile_path}")

                output.append("\n📄 Generated Dockerfile:")
                output.append("=" * 50)
                output.append(result.dockerfile_content or "")
                output.append("=" * 50)

                return "\n".join(output)
            else:
                return f"❌ Failed to generate Dockerfile: {result.error}"

        except Exception as e:
            return f"❌ Error generating Dockerfile: {str(e)}"

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
