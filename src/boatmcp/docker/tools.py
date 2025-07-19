"""Docker-related MCP tools."""

import os
import subprocess
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from ..core.analysis import ProjectAnalysis, analyze_project, format_analysis_with_files
from .generator import generate_dockerfile_content, save_dockerfile


def register_docker_tools(mcp: FastMCP[Any]) -> None:
    """Register all Docker-related MCP tools."""

    # Check if internal tools should be enabled
    enable_internal_tools = (
        os.getenv("BOATMCP_INTERNAL_TOOLS", "false").lower() == "true"
    )

    # Internal tools (gated behind environment variable)
    if enable_internal_tools:

        @mcp.tool()
        async def build_docker_image(
            project_path: str,
            image_name: str,
            image_tag: str = "latest",
            dockerfile_path: str | None = None,
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

                dockerfile = (
                    Path(dockerfile_path)
                    if dockerfile_path
                    else project_dir / "Dockerfile"
                )
                if not dockerfile.exists():
                    return f"❌ Dockerfile not found: {dockerfile}"

                # Build the image
                cmd = [
                    "docker",
                    "build",
                    "-t",
                    f"{image_name}:{image_tag}",
                    "-f",
                    str(dockerfile),
                    str(project_dir),
                ]

                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=600
                )

                if result.returncode == 0:
                    output = []
                    output.append("✅ Docker image built successfully!")
                    output.append(f"🏷️  Image: {image_name}:{image_tag}")
                    output.append(f"📁 Context: {project_dir}")
                    output.append(f"📄 Dockerfile: {dockerfile}")
                    output.append("\n📋 Build output:")
                    output.append(
                        result.stdout[-1000:]
                    )  # Last 1000 chars to avoid too much output
                    return "\n".join(output)
                else:
                    return f"❌ Failed to build Docker image: {result.stderr}"

            except subprocess.TimeoutExpired:
                return "❌ Timeout building Docker image (exceeded 10 minutes)"
            except Exception as e:
                return f"❌ Error building Docker image: {str(e)}"

        @mcp.tool()
        async def analyze_project_for_dockerfile(
            project_path: str,
            optimize_for_size: bool = False,
            multi_stage: bool = False,
            custom_instructions: list[str] | None = None,
        ) -> str:
            """
            Analyze a project structure and return detailed information for Dockerfile generation.

            This tool performs comprehensive project analysis and returns structured information
            that can be used to generate a custom, production-ready Dockerfile.

            Args:
                project_path: Path to the project root directory
                optimize_for_size: Whether to optimize for smaller image size
                multi_stage: Whether to use multi-stage builds (where applicable)
                custom_instructions: Optional list of custom requirements or instructions

            Returns:
                Structured project analysis data for Dockerfile generation
            """
            try:
                # Analyze the project
                analysis = await analyze_project(project_path)

                # Add configuration information to the response
                config = []
                if optimize_for_size:
                    config.append("Size optimization enabled")
                if multi_stage:
                    config.append("Multi-stage build requested")
                if custom_instructions:
                    config.append(
                        f"Custom requirements: {', '.join(custom_instructions)}"
                    )

                # Format the analysis with file contents
                result = format_analysis_with_files(analysis)

                if config:
                    result += f"\n\n⚙️  **Configuration:** {', '.join(config)}"

                return result

            except ValueError as e:
                return f"❌ {str(e)}"
            except Exception as e:
                return f"❌ Error analyzing project: {str(e)}"

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
                output.append(
                    "Use this path or navigate to a subdirectory for Docker operations."
                )
                output.append(
                    "For example: `generate_dockerfile('/path/to/your/project')`"
                )

                return "\n".join(output)

            except Exception as e:
                return f"❌ Error getting current directory: {str(e)}"

        @mcp.tool()
        async def generate_dockerfile(
            project_path: str,
            port: int = 80,
            optimize_for_size: bool = False,
            multi_stage: bool = False,
            custom_instructions: list[str] | None = None,
            save_to_project: bool = True,
        ) -> str:
            """
            Generate a Dockerfile for a project and optionally save it.

            Args:
                project_path: Path to the project root directory
                port: Port the application will expose
                optimize_for_size: Whether to optimize for smaller image size
                multi_stage: Whether to use multi-stage builds
                custom_instructions: Optional custom build instructions
                save_to_project: Whether to save the Dockerfile to the project directory

            Returns:
                Generated Dockerfile content and save status
            """
            try:
                # Analyze the project
                analysis = await analyze_project(project_path)

                # Generate Dockerfile content
                dockerfile_content = generate_dockerfile_content(
                    analysis=analysis,
                    port=port,
                    optimize_for_size=optimize_for_size,
                    multi_stage=multi_stage,
                    custom_instructions=custom_instructions,
                )

                output = []
                output.append("🐳 **Dockerfile Generated**")
                output.append(f"📁 **Project:** {analysis.project_path}")
                output.append(f"🏷️  **Type:** {analysis.project_type}")
                output.append(f"🔌 **Port:** {port}")

                if optimize_for_size or multi_stage or custom_instructions:
                    config = []
                    if optimize_for_size:
                        config.append("size-optimized")
                    if multi_stage:
                        config.append("multi-stage")
                    if custom_instructions:
                        config.append(f"custom: {', '.join(custom_instructions)}")
                    output.append(f"⚙️  **Options:** {', '.join(config)}")

                output.append("\n📄 **Dockerfile Content:**")
                output.append("```dockerfile")
                output.append(dockerfile_content.strip())
                output.append("```")

                # Save to project if requested
                if save_to_project:
                    save_result = await save_dockerfile(
                        analysis.project_path, dockerfile_content
                    )
                    output.append(f"\n{save_result}")

                return "\n".join(output)

            except ValueError as e:
                return f"❌ {str(e)}"
            except Exception as e:
                return f"❌ Error generating Dockerfile: {str(e)}"

        @mcp.tool()
        async def save_dockerfile_content(
            project_path: str, dockerfile_content: str
        ) -> str:
            """
            Save a Dockerfile to the project root directory.

            Args:
                project_path: Path to the project root directory
                dockerfile_content: Content of the Dockerfile to save

            Returns:
                Status message indicating success or failure
            """
            try:
                abs_project_path = Path(project_path).resolve()
                return await save_dockerfile(abs_project_path, dockerfile_content)

            except Exception as e:
                return f"❌ Error saving Dockerfile: {str(e)}"

        @mcp.tool()
        async def get_dockerfile_template_info(
            project_path: str,
            port: int = 80,
            optimize_for_size: bool = False,
            multi_stage: bool = False,
            custom_instructions: list[str] | None = None,
        ) -> str:
            """
            Get detailed information about Dockerfile template selection and parameters.

            This tool provides transparency into the Dockerfile generation process by showing:
            - Project analysis results that drive template selection
            - Which template will be used and why
            - Parameter values that will be substituted
            - Template selection logic explanation

            Args:
                project_path: Path to the project root directory
                port: Port the application will expose
                optimize_for_size: Whether to optimize for smaller image size
                multi_stage: Whether to use multi-stage builds
                custom_instructions: Optional custom build instructions

            Returns:
                Detailed template information and analysis results
            """
            try:
                # Analyze the project
                analysis = await analyze_project(project_path)

                # Determine template selection logic
                template_reason = _get_dockerfile_template_selection_reason(
                    analysis, optimize_for_size, multi_stage
                )

                # Get template parameters
                template_params = {
                    "project_type": analysis.project_type,
                    "port": port,
                    "optimize_for_size": optimize_for_size,
                    "multi_stage": multi_stage,
                    "custom_instructions": custom_instructions or [],
                }

                output = []
                output.append("🔍 **Dockerfile Template Analysis**")
                output.append(f"📁 **Project Path:** {analysis.project_path}")
                output.append(f"🏷️  **Project Type:** {analysis.project_type}")
                output.append(f"📊 **Files Analyzed:** {analysis.total_files}")

                # Show dependency files found
                deps_found = [
                    name for name, found in analysis.dependency_files.items() if found
                ]
                if deps_found:
                    output.append(f"📦 **Dependencies Found:** {', '.join(deps_found)}")

                output.append(
                    f"📋 **File Extensions:** {', '.join(sorted(analysis.file_extensions))}"
                )

                # Template selection explanation
                output.append(f"\n🎯 **Template Selection:** {template_reason}")

                # Parameters that will be used
                output.append("\n⚙️  **Template Parameters:**")
                for key, value in template_params.items():
                    if isinstance(value, list):
                        value_str = f"[{', '.join(value)}]" if value else "[]"
                    else:
                        value_str = str(value)
                    output.append(f"   • {key}: {value_str}")

                # Show detected main files
                main_files = _detect_main_files(analysis)
                if main_files:
                    output.append(
                        f"\n📄 **Detected Main Files:** {', '.join(main_files)}"
                    )

                return "\n".join(output)

            except ValueError as e:
                return f"❌ {str(e)}"
            except Exception as e:
                return f"❌ Error analyzing Dockerfile template: {str(e)}"

        @mcp.tool()
        async def preview_dockerfile(
            project_path: str,
            port: int = 80,
            optimize_for_size: bool = False,
            multi_stage: bool = False,
            custom_instructions: list[str] | None = None,
        ) -> str:
            """
            Preview the Dockerfile that would be generated without saving it.

            This tool shows exactly what Dockerfile content would be generated with the given
            parameters, allowing verification before actual file creation.

            Args:
                project_path: Path to the project root directory
                port: Port the application will expose
                optimize_for_size: Whether to optimize for smaller image size
                multi_stage: Whether to use multi-stage builds
                custom_instructions: Optional custom build instructions

            Returns:
                Generated Dockerfile content preview with analysis context
            """
            try:
                # Analyze the project
                analysis = await analyze_project(project_path)

                # Generate Dockerfile content
                dockerfile_content = generate_dockerfile_content(
                    analysis=analysis,
                    port=port,
                    optimize_for_size=optimize_for_size,
                    multi_stage=multi_stage,
                    custom_instructions=custom_instructions,
                )

                output = []
                output.append("🐳 **Dockerfile Preview**")
                output.append(f"📁 **Project:** {analysis.project_path}")
                output.append(f"🏷️  **Type:** {analysis.project_type}")
                output.append(f"🔌 **Port:** {port}")

                if optimize_for_size or multi_stage or custom_instructions:
                    config = []
                    if optimize_for_size:
                        config.append("size-optimized")
                    if multi_stage:
                        config.append("multi-stage")
                    if custom_instructions:
                        config.append(f"custom: {', '.join(custom_instructions)}")
                    output.append(f"⚙️  **Options:** {', '.join(config)}")

                output.append("\n📄 **Generated Dockerfile:**")
                output.append("```dockerfile")
                output.append(dockerfile_content.strip())
                output.append("```")

                output.append(
                    "\n💡 **Note:** This is a preview only. Use 'generate_dockerfile' to save to project."
                )

                return "\n".join(output)

            except ValueError as e:
                return f"❌ {str(e)}"
            except Exception as e:
                return f"❌ Error previewing Dockerfile: {str(e)}"

        @mcp.tool()
        async def get_dockerfile_templates() -> str:
            """
            Get information about available Dockerfile templates and generation logic.

            This tool provides insight into how Dockerfile generation works by showing:
            - Available project types and their templates
            - Template selection logic
            - Customization options available

            Returns:
                Detailed information about Dockerfile template system
            """
            try:
                output = []
                output.append("📋 **Dockerfile Template System**")
                output.append("\n🎯 **Supported Project Types:**")

                # Document supported project types and their characteristics
                project_types = {
                    "python": {
                        "detection": "requirements.txt, pyproject.toml, or .py files",
                        "base_images": "python:3.11 (standard), python:3.11-slim (optimized)",
                        "main_files": "app.py, main.py, server.py, manage.py",
                        "features": "pip dependency installation, COPY optimization",
                    },
                    "node.js": {
                        "detection": "package.json or .js/.ts files",
                        "base_images": "node:18 (standard), node:18-alpine (optimized)",
                        "main_files": "index.js, app.js, server.js, main.js",
                        "features": "npm ci installation, package.json handling",
                    },
                    "go": {
                        "detection": "go.mod or .go files",
                        "base_images": "golang:{detected_version} (standard), golang:{detected_version}-alpine (optimized)",
                        "main_files": "main.go, cmd/main.go",
                        "features": "Multi-stage builds supported, dependency caching, auto-detects system Go version",
                    },
                    "rust": {
                        "detection": "Cargo.toml or .rs files",
                        "base_images": "rust:1.70 (standard), rust:1.70-slim (optimized)",
                        "main_files": "main.rs, src/main.rs",
                        "features": "Multi-stage builds supported, cargo optimization",
                    },
                    "java": {
                        "detection": "pom.xml, build.gradle, or .java files",
                        "base_images": "openjdk:11 (standard), openjdk:11-jre-slim (optimized)",
                        "main_files": "Main.java, Application.java, App.java",
                        "features": "Maven/Gradle support, multi-stage builds",
                    },
                    "generic": {
                        "detection": "fallback for unknown project types",
                        "base_images": "alpine:latest",
                        "main_files": "any executable file",
                        "features": "basic file copying",
                    },
                }

                for proj_type, info in project_types.items():
                    output.append(f"\n**{proj_type.upper()}:**")
                    output.append(f"   🔍 Detection: {info['detection']}")
                    output.append(f"   🐳 Base Images: {info['base_images']}")
                    output.append(f"   📄 Main Files: {info['main_files']}")
                    output.append(f"   ⚡ Features: {info['features']}")

                output.append("\n🛠️  **Template Customization Options:**")
                output.append("   • **optimize_for_size**: Use slim/alpine base images")
                output.append(
                    "   • **multi_stage**: Use multi-stage builds (Go, Rust, Java)"
                )
                output.append("   • **port**: Customize exposed port (default: 80)")
                output.append("   • **custom_instructions**: Add custom build steps")

                output.append("\n🔄 **Template Selection Logic:**")
                output.append("   1. Analyze project files and dependencies")
                output.append(
                    "   2. Detect project type by dependency files (preferred)"
                )
                output.append("   3. Fall back to file extension analysis")
                output.append(
                    "   4. Select appropriate base image based on optimization flags"
                )
                output.append(
                    "   5. Choose build strategy (single-stage vs multi-stage)"
                )
                output.append(
                    "   6. Configure main application file and startup command"
                )

                output.append("\n💡 **Usage Tips:**")
                output.append(
                    "   • Use 'get_dockerfile_template_info' to see what template will be selected"
                )
                output.append(
                    "   • Use 'preview_dockerfile' to see generated content before saving"
                )
                output.append(
                    "   • Use 'generate_dockerfile' to create and save the final Dockerfile"
                )

                return "\n".join(output)

            except Exception as e:
                return f"❌ Error getting Dockerfile templates: {str(e)}"


def _get_dockerfile_template_selection_reason(
    analysis: ProjectAnalysis, optimize_for_size: bool, multi_stage: bool
) -> str:
    """Get explanation for why a specific Dockerfile template was selected."""

    project_type = analysis.project_type
    reasons = []

    if project_type == "python":
        if any(analysis.dependency_files.get(f) for f in ["requirements.txt"]):
            reasons.append("Python project with requirements.txt detected")
        else:
            reasons.append("Python project detected by .py file extensions")
    elif project_type == "node.js":
        if analysis.dependency_files.get("package.json"):
            reasons.append("Node.js project with package.json detected")
        else:
            reasons.append("Node.js project detected by .js/.ts file extensions")
    elif project_type == "go":
        if analysis.dependency_files.get("go.mod"):
            reasons.append("Go project with go.mod detected")
        else:
            reasons.append("Go project detected by .go file extensions")
    elif project_type == "rust":
        if analysis.dependency_files.get("Cargo.toml"):
            reasons.append("Rust project with Cargo.toml detected")
        else:
            reasons.append("Rust project detected by .rs file extensions")
    elif project_type == "java":
        if analysis.dependency_files.get("pom.xml"):
            reasons.append("Java Maven project with pom.xml detected")
        elif analysis.dependency_files.get("build.gradle"):
            reasons.append("Java Gradle project with build.gradle detected")
        else:
            reasons.append("Java project detected by .java file extensions")
    else:
        reasons.append(f"Generic template selected (project type: {project_type})")

    # Add optimization reasons
    if optimize_for_size:
        reasons.append("using slim/alpine base images for size optimization")

    if multi_stage and project_type in ["go", "rust", "java"]:
        reasons.append("using multi-stage build for smaller final image")
    elif multi_stage:
        reasons.append("multi-stage requested but not applicable for this project type")

    return "; ".join(reasons)


def _detect_main_files(analysis: ProjectAnalysis) -> list[str]:
    """Detect likely main application files from project analysis."""

    main_files = []
    project_files = analysis.project_files

    # Common main file patterns
    main_patterns = {
        "python": ["app.py", "main.py", "server.py", "manage.py"],
        "node.js": ["index.js", "app.js", "server.js", "main.js"],
        "go": ["main.go", "cmd/main.go"],
        "rust": ["main.rs", "src/main.rs"],
        "java": ["Main.java", "Application.java", "App.java"],
    }

    patterns = main_patterns.get(analysis.project_type, [])

    for pattern in patterns:
        if pattern in project_files:
            main_files.append(pattern)

    return main_files
