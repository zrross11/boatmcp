"""Docker-related MCP tools."""

import subprocess
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from ..utils import read_project_files


def register_docker_tools(mcp: FastMCP[Any]) -> None:
    """Register all Docker-related MCP tools."""


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

    @mcp.tool()
    async def generate_dockerfile(
        project_path: str,
        optimize_for_size: bool = False,
        multi_stage: bool = False,
        custom_instructions: list[str] | None = None
    ) -> str:
        """
        Analyze a project and provide detailed information for Claude to generate an optimized Dockerfile.

        This tool performs project analysis and returns structured information that Claude can use
        to generate a custom, production-ready Dockerfile tailored to the specific project.

        Args:
            project_path: Path to the project root directory
            optimize_for_size: Whether to optimize the Dockerfile for smaller image size
            multi_stage: Whether to use multi-stage builds (where applicable)
            custom_instructions: Optional list of custom requirements or instructions

        Returns:
            Detailed project analysis for Claude to generate a custom Dockerfile
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

            # Build the generation prompt with requirements
            output = []
            output.append("🎯 **Dockerfile Generation Request**")
            output.append(f"📁 **Project Path:** {abs_project_path}")

            # Add generation requirements
            requirements = []
            if optimize_for_size:
                requirements.append("🏋️ **Size Optimization:** Use alpine/slim base images and minimize layers")
            if multi_stage:
                requirements.append("🏗️ **Multi-stage Build:** Use multi-stage builds for smaller final images")
            if custom_instructions:
                requirements.append(f"📝 **Custom Instructions:** {', '.join(custom_instructions)}")

            if requirements:
                output.append("\n🎛️ **Generation Requirements:**")
                output.extend(requirements)

            # Add project analysis
            output.append("\n🔍 **Project Analysis Complete**")
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

            # Add generation instructions for Claude
            output.append("\n🤖 **Instructions for Claude:**")
            output.append("Please generate a clean, production-ready Dockerfile based on the project analysis above.")
            output.append("**IMPORTANT: Keep the Dockerfile readable but functional - avoid unnecessary lines and comments.**")
            output.append("\nConsider the following best practices:")
            output.append("- Use appropriate base images for the detected project type")
            output.append("- Implement proper layer caching (copy dependency files first)")
            output.append("- Set appropriate working directory and expose ports")
            output.append("- Include security best practices (non-root user if applicable)")
            output.append("- Add health checks if appropriate for the application type")
            output.append("- Optimize for the specified requirements (size, multi-stage, etc.)")
            output.append("- Focus on essential instructions only - no excessive comments or explanatory text")

            output.append("\nOnce you've generated the Dockerfile, use the 'save_dockerfile' tool to save it to the project.")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error preparing Dockerfile generation: {str(e)}"

    @mcp.tool()
    async def get_current_directory() -> str:
        """
        Get the current working directory to help identify project paths.

        Returns:
            Current working directory path and basic information about the directory contents
        """
        try:
            current_dir = Path.cwd()

            # Get directory contents for context
            contents: list[str] = []
            try:
                for item in current_dir.iterdir():
                    if item.is_dir():
                        contents.append(f"📁 {item.name}/")
                    else:
                        contents.append(f"📄 {item.name}")
            except PermissionError:
                contents = ["❌ Permission denied reading directory contents"]

            # Sort contents for better readability
            contents.sort()

            output: list[str] = []
            output.append("📍 **Current Working Directory**")
            output.append(f"🗂️ **Path:** {current_dir}")
            output.append(f"📊 **Items Found:** {len(contents)}")
            output.append("\n📋 **Directory Contents:**")
            output.append("=" * 40)

            # Limit output to first 20 items to avoid overwhelming output
            display_contents: list[str] = contents[:20]
            for content_item in display_contents:
                output.append(content_item)

            if len(contents) > 20:
                output.append(f"... and {len(contents) - 20} more items")

            output.append("=" * 40)
            output.append("\n💡 **Usage Tip:**")
            output.append("Use this path or navigate to a subdirectory for Docker operations.")
            output.append("For example: `generate_dockerfile('/path/to/your/project')`")

            return "\n".join(output)

        except Exception as e:
            return f"❌ Error getting current directory: {str(e)}"

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
