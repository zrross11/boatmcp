"""Shared project analysis utilities."""

from dataclasses import dataclass
from pathlib import Path

from .file_reader import read_project_files


@dataclass(frozen=True)
class ProjectAnalysis:
    """Results of project analysis."""

    project_path: Path
    project_type: str
    file_extensions: set[str]
    total_files: int
    dependency_files: dict[str, bool]
    project_files: dict[str, str]


async def analyze_project(project_path: str) -> ProjectAnalysis:
    """
    Analyze a project structure and return comprehensive information.

    Args:
        project_path: Path to the project root directory

    Returns:
        ProjectAnalysis object with all discovered information

    Raises:
        ValueError: If project path doesn't exist or contains no files
    """
    abs_project_path = Path(project_path).resolve()

    if not abs_project_path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")

    if not abs_project_path.is_dir():
        raise ValueError(f"Project path is not a directory: {project_path}")

    # Read all project files
    project_files = read_project_files(str(abs_project_path))

    if not project_files:
        raise ValueError(
            f"No relevant files found in project directory: {project_path}"
        )

    # Analyze file types and project characteristics
    file_extensions = set()
    dependency_files = {
        "requirements.txt": False,
        "package.json": False,
        "go.mod": False,
        "Cargo.toml": False,
        "pom.xml": False,
        "build.gradle": False,
        "Gemfile": False,
        "composer.json": False,
    }

    for file_path in project_files.keys():
        if "." in file_path:
            ext = "." + file_path.split(".")[-1]
            file_extensions.add(ext)

        # Check for dependency files
        file_lower = file_path.lower()
        if file_lower in dependency_files:
            dependency_files[file_lower] = True
        elif file_path in dependency_files:  # Case-sensitive check
            dependency_files[file_path] = True

    # Determine project type
    project_type = _detect_project_type(file_extensions, dependency_files)

    return ProjectAnalysis(
        project_path=abs_project_path,
        project_type=project_type,
        file_extensions=file_extensions,
        total_files=len(project_files),
        dependency_files=dependency_files,
        project_files=project_files,
    )


def _detect_project_type(
    file_extensions: set[str], dependency_files: dict[str, bool]
) -> str:
    """Detect project type based on files and extensions."""

    # Check dependency files first (more reliable)
    if dependency_files.get("requirements.txt") or dependency_files.get(
        "pyproject.toml"
    ):
        return "python"
    elif dependency_files.get("package.json"):
        return "node.js"
    elif dependency_files.get("go.mod"):
        return "go"
    elif dependency_files.get("Cargo.toml"):
        return "rust"
    elif dependency_files.get("pom.xml") or dependency_files.get("build.gradle"):
        return "java"
    elif dependency_files.get("Gemfile"):
        return "ruby"
    elif dependency_files.get("composer.json"):
        return "php"

    # Fallback to file extensions
    if ".py" in file_extensions:
        return "python"
    elif ".js" in file_extensions or ".ts" in file_extensions:
        return "node.js"
    elif ".go" in file_extensions:
        return "go"
    elif ".rs" in file_extensions:
        return "rust"
    elif ".java" in file_extensions:
        return "java"
    elif ".rb" in file_extensions:
        return "ruby"
    elif ".php" in file_extensions:
        return "php"

    return "unknown"


def format_analysis_summary(analysis: ProjectAnalysis) -> str:
    """Format project analysis into a readable summary."""

    output = []
    output.append("📊 **Project Analysis Results**")
    output.append(f"📁 **Project Path:** {analysis.project_path}")
    output.append(f"🏷️  **Detected Type:** {analysis.project_type}")
    output.append(
        f"📋 **File Extensions:** {', '.join(sorted(analysis.file_extensions))}"
    )
    output.append(f"📄 **Total Files:** {analysis.total_files}")

    # Add dependency files information
    found_deps = [name for name, found in analysis.dependency_files.items() if found]
    if found_deps:
        output.append(f"\n📦 **Dependency Files:** {', '.join(found_deps)}")

    return "\n".join(output)


def format_analysis_with_files(analysis: ProjectAnalysis) -> str:
    """Format project analysis with full file contents."""

    output = [format_analysis_summary(analysis)]

    # Add project files content
    output.append("\n📄 **Project Files:**")
    output.append("=" * 50)

    for file_path, content in analysis.project_files.items():
        output.append(f"\n**{file_path}:**")
        output.append("```")
        output.append(content.strip())
        output.append("```")

    output.append("=" * 50)

    return "\n".join(output)
