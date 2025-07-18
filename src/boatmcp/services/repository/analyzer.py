"""Repository analysis functionality."""

import json
import re
from pathlib import Path
from typing import Any

from ...schemas.repository import FileInfo, ProjectAnalysis


class RepositoryAnalyzer:
    """Analyzes project structure and determines project type."""

    # File patterns for different project types
    PROJECT_INDICATORS = {
        "python": {
            "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "setup.cfg"],
            "dirs": ["venv", ".venv", "__pycache__"],
            "extensions": [".py"],
        },
        "go": {
            "files": ["go.mod", "go.sum", "Gopkg.toml", "main.go"],
            "dirs": ["vendor"],
            "extensions": [".go"],
        },
        "node": {
            "files": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
            "dirs": ["node_modules", "dist", "build"],
            "extensions": [".js", ".ts", ".tsx", ".jsx"],
        },
        "java": {
            "files": ["pom.xml", "build.gradle", "build.xml"],
            "dirs": ["target", "build", "src/main/java"],
            "extensions": [".java", ".kt"],
        },
        "rust": {
            "files": ["Cargo.toml", "Cargo.lock"],
            "dirs": ["target"],
            "extensions": [".rs"],
        },
    }

    FRAMEWORK_INDICATORS = {
        "python": {
            "flask": ["from flask", "import flask", "Flask("],
            "django": ["from django", "import django", "DJANGO_SETTINGS_MODULE"],
            "fastapi": ["from fastapi", "import fastapi", "FastAPI("],
            "tornado": ["from tornado", "import tornado"],
        },
        "go": {
            "gin": ["github.com/gin-gonic/gin"],
            "echo": ["github.com/labstack/echo"],
            "fiber": ["github.com/gofiber/fiber"],
        },
        "node": {
            "express": ["express", "app.listen"],
            "react": ["react", "ReactDOM"],
            "vue": ["vue", "Vue"],
            "angular": ["@angular", "angular"],
        },
    }

    def analyze_project(self, project_path: Path) -> ProjectAnalysis:
        """Analyze a project and return structured analysis."""
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Project path does not exist or is not a directory: {project_path}")

        # Collect all files
        all_files = self._collect_files(project_path)

        # Determine project type
        project_type = self._determine_project_type(all_files)

        # Analyze based on project type
        if project_type == "python":
            return self._analyze_python_project(project_path, all_files)
        elif project_type == "go":
            return self._analyze_go_project(project_path, all_files)
        elif project_type == "node":
            return self._analyze_node_project(project_path, all_files)
        elif project_type == "java":
            return self._analyze_java_project(project_path, all_files)
        elif project_type == "rust":
            return self._analyze_rust_project(project_path, all_files)
        else:
            return self._analyze_unknown_project(project_path, all_files)

    def _collect_files(self, project_path: Path) -> list[FileInfo]:
        """Collect all files in the project directory only (no parent directories)."""
        files = []

        # Skip common directories that shouldn't be scanned
        skip_dirs = {
            ".git", ".venv", "venv", "node_modules", "target", "build", "dist",
            "__pycache__", ".pytest_cache", ".mypy_cache", "vendor"
        }

        # Only scan files within the project directory, not parent directories
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                # Ensure the file is within the project directory boundaries
                try:
                    file_path.relative_to(project_path)
                except ValueError:
                    # File is outside the project directory, skip it
                    continue

                # Skip files in ignored directories
                if any(part in skip_dirs for part in file_path.parts):
                    continue

                # Skip binary files larger than 1MB
                if file_path.stat().st_size > 1024 * 1024:
                    continue

                file_info = FileInfo(
                    path=file_path,
                    size=file_path.stat().st_size,
                    is_binary=self._is_binary_file(file_path)
                )

                # Read content for text files under 100KB
                if not file_info.is_binary and file_info.size < 100 * 1024:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        file_info = FileInfo(
                            path=file_path,
                            size=file_info.size,
                            content=content,
                            is_binary=False
                        )
                    except (UnicodeDecodeError, PermissionError):
                        pass

                files.append(file_info)

        return files

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except (PermissionError, OSError):
            return True

    def _determine_project_type(self, files: list[FileInfo]) -> str:
        """Determine project type based on files."""
        scores = {}

        for project_type, indicators in self.PROJECT_INDICATORS.items():
            score = 0

            for file_info in files:
                file_name = file_info.path.name
                file_ext = file_info.path.suffix

                # Check for indicator files
                if file_name in indicators["files"]:
                    score += 10

                # Check for extensions
                if file_ext in indicators["extensions"]:
                    score += 1

            scores[project_type] = score

        # Return the project type with highest score
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores, key=lambda x: scores[x])
        return "unknown"

    def _analyze_python_project(self, project_path: Path, files: list[FileInfo]) -> ProjectAnalysis:
        """Analyze a Python project."""
        dependencies = []
        entry_points = []
        framework = None
        package_manager = None

        # Determine package manager
        config_files = [f for f in files if f.path.name in ["requirements.txt", "pyproject.toml", "Pipfile", "setup.py"]]
        if any(f.path.name == "pyproject.toml" for f in config_files):
            package_manager = "uv/pip"
        elif any(f.path.name == "Pipfile" for f in config_files):
            package_manager = "pipenv"
        elif any(f.path.name == "requirements.txt" for f in config_files):
            package_manager = "pip"

        # Extract dependencies
        for file_info in files:
            if file_info.path.name == "requirements.txt" and file_info.content:
                dependencies.extend(self._parse_requirements_txt(file_info.content))
            elif file_info.path.name == "pyproject.toml" and file_info.content:
                dependencies.extend(self._parse_pyproject_toml(file_info.content))

        # Detect framework
        for file_info in files:
            if file_info.content and file_info.path.suffix == ".py":
                for fw, indicators in self.FRAMEWORK_INDICATORS["python"].items():
                    if any(indicator in file_info.content for indicator in indicators):
                        framework = fw
                        break
                if framework:
                    break

        # Find entry points
        for file_info in files:
            if file_info.path.name in ["main.py", "app.py", "server.py"] or \
               (file_info.content and "if __name__ == '__main__':" in file_info.content):
                entry_points.append(str(file_info.path.relative_to(project_path)))

        source_files = [f for f in files if f.path.suffix == ".py"]
        static_files = [f for f in files if f.path.suffix in [".html", ".css", ".js", ".json"]]

        return ProjectAnalysis(
            root_path=project_path,
            project_type="python",
            language="python",
            framework=framework,
            package_manager=package_manager,
            dependencies=dependencies,
            entry_points=entry_points,
            config_files=config_files,
            source_files=source_files,
            static_files=static_files
        )

    def _analyze_go_project(self, project_path: Path, files: list[FileInfo]) -> ProjectAnalysis:
        """Analyze a Go project."""
        dependencies = []
        entry_points = []
        framework = None

        # Parse go.mod for dependencies
        for file_info in files:
            if file_info.path.name == "go.mod" and file_info.content:
                dependencies.extend(self._parse_go_mod(file_info.content))

        # Detect framework
        for file_info in files:
            if file_info.content and file_info.path.suffix == ".go":
                for fw, indicators in self.FRAMEWORK_INDICATORS["go"].items():
                    if any(indicator in file_info.content for indicator in indicators):
                        framework = fw
                        break
                if framework:
                    break

        # Find entry points (main.go or files with main function)
        for file_info in files:
            if file_info.path.name == "main.go" or \
               (file_info.content and "func main()" in file_info.content):
                entry_points.append(str(file_info.path.relative_to(project_path)))

        config_files = [f for f in files if f.path.name in ["go.mod", "go.sum"]]
        source_files = [f for f in files if f.path.suffix == ".go"]
        static_files = [f for f in files if f.path.suffix in [".html", ".css", ".js", ".json"]]

        return ProjectAnalysis(
            root_path=project_path,
            project_type="go",
            language="go",
            framework=framework,
            package_manager="go",
            dependencies=dependencies,
            entry_points=entry_points,
            config_files=config_files,
            source_files=source_files,
            static_files=static_files
        )

    def _analyze_node_project(self, project_path: Path, files: list[FileInfo]) -> ProjectAnalysis:
        """Analyze a Node.js project."""
        dependencies = []
        entry_points = []
        framework = None
        package_manager = "npm"

        # Determine package manager
        if any(f.path.name == "yarn.lock" for f in files):
            package_manager = "yarn"
        elif any(f.path.name == "pnpm-lock.yaml" for f in files):
            package_manager = "pnpm"

        # Parse package.json
        for file_info in files:
            if file_info.path.name == "package.json" and file_info.content:
                pkg_data = self._parse_package_json(file_info.content)
                if pkg_data:
                    dependencies.extend(pkg_data.get("dependencies", []))
                    if "main" in pkg_data:
                        entry_points.append(pkg_data["main"])

        # Detect framework
        for file_info in files:
            if file_info.content and file_info.path.suffix in [".js", ".ts", ".tsx", ".jsx"]:
                for fw, indicators in self.FRAMEWORK_INDICATORS["node"].items():
                    if any(indicator in file_info.content for indicator in indicators):
                        framework = fw
                        break
                if framework:
                    break

        config_files = [f for f in files if f.path.name in ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"]]
        source_files = [f for f in files if f.path.suffix in [".js", ".ts", ".tsx", ".jsx"]]
        static_files = [f for f in files if f.path.suffix in [".html", ".css", ".json"]]

        return ProjectAnalysis(
            root_path=project_path,
            project_type="node",
            language="javascript",
            framework=framework,
            package_manager=package_manager,
            dependencies=dependencies,
            entry_points=entry_points,
            config_files=config_files,
            source_files=source_files,
            static_files=static_files
        )

    def _analyze_java_project(self, project_path: Path, files: list[FileInfo]) -> ProjectAnalysis:
        """Analyze a Java project."""
        # Basic Java project analysis
        config_files = [f for f in files if f.path.name in ["pom.xml", "build.gradle", "build.xml"]]
        source_files = [f for f in files if f.path.suffix in [".java", ".kt"]]
        static_files = [f for f in files if f.path.suffix in [".html", ".css", ".js", ".json"]]

        return ProjectAnalysis(
            root_path=project_path,
            project_type="java",
            language="java",
            config_files=config_files,
            source_files=source_files,
            static_files=static_files
        )

    def _analyze_rust_project(self, project_path: Path, files: list[FileInfo]) -> ProjectAnalysis:
        """Analyze a Rust project."""
        # Basic Rust project analysis
        config_files = [f for f in files if f.path.name in ["Cargo.toml", "Cargo.lock"]]
        source_files = [f for f in files if f.path.suffix == ".rs"]
        static_files = [f for f in files if f.path.suffix in [".html", ".css", ".js", ".json"]]

        return ProjectAnalysis(
            root_path=project_path,
            project_type="rust",
            language="rust",
            package_manager="cargo",
            config_files=config_files,
            source_files=source_files,
            static_files=static_files
        )

    def _analyze_unknown_project(self, project_path: Path, files: list[FileInfo]) -> ProjectAnalysis:
        """Analyze an unknown project type."""
        return ProjectAnalysis(
            root_path=project_path,
            project_type="unknown",
            language="unknown",
            config_files=[],
            source_files=[],
            static_files=[]
        )

    def _parse_requirements_txt(self, content: str) -> list[str]:
        """Parse requirements.txt content."""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove version specifiers
                dep = re.split(r'[>=<!=]', line)[0].strip()
                if dep:
                    deps.append(dep)
        return deps

    def _parse_pyproject_toml(self, content: str) -> list[str]:
        """Parse pyproject.toml content for dependencies."""
        deps = []
        try:
            import tomllib
            data = tomllib.loads(content)
            if "project" in data and "dependencies" in data["project"]:
                for dep in data["project"]["dependencies"]:
                    dep_name = re.split(r'[>=<!=]', dep)[0].strip()
                    if dep_name:
                        deps.append(dep_name)
        except Exception:
            pass
        return deps

    def _parse_go_mod(self, content: str) -> list[str]:
        """Parse go.mod content."""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('require'):
                # Extract module name
                parts = line.split()
                if len(parts) >= 2:
                    deps.append(parts[1])
        return deps

    def _parse_package_json(self, content: str) -> dict[str, Any] | None:
        """Parse package.json content."""
        try:
            data = json.loads(content)
            # Ensure it's a dictionary
            if isinstance(data, dict):
                return data
            return None
        except json.JSONDecodeError:
            return None
