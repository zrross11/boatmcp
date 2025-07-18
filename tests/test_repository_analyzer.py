"""Tests for repository analyzer."""

from dataclasses import replace
from pathlib import Path

import pytest

from boatmcp.schemas.repository import FileInfo
from boatmcp.services.repository.analyzer import RepositoryAnalyzer


def get_mock_file_info(
    overrides: dict | None = None
) -> FileInfo:
    """Create a mock file info with sensible defaults."""
    base_file = FileInfo(
        path=Path("/test/app.py"),
        size=1000,
        content="from flask import Flask\napp = Flask(__name__)",
        is_binary=False
    )

    if overrides:
        return replace(base_file, **overrides)
    return base_file


class TestRepositoryAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return RepositoryAnalyzer()

    def test_determine_project_type_python(self, analyzer):
        """Test determining Python project type."""
        files = [
            get_mock_file_info({"path": Path("/test/requirements.txt")}),
            get_mock_file_info({"path": Path("/test/app.py")}),
        ]

        project_type = analyzer._determine_project_type(files)

        assert project_type == "python"

    def test_determine_project_type_go(self, analyzer):
        """Test determining Go project type."""
        files = [
            get_mock_file_info({
                "path": Path("/test/go.mod"),
                "content": "module myapp\ngo 1.21"
            }),
            get_mock_file_info({
                "path": Path("/test/main.go"),
                "content": "package main\nfunc main() {}"
            }),
        ]

        project_type = analyzer._determine_project_type(files)

        assert project_type == "go"

    def test_determine_project_type_node(self, analyzer):
        """Test determining Node.js project type."""
        files = [
            get_mock_file_info({
                "path": Path("/test/package.json"),
                "content": '{"name": "myapp", "version": "1.0.0"}'
            }),
            get_mock_file_info({
                "path": Path("/test/index.js"),
                "content": "const express = require('express')"
            }),
        ]

        project_type = analyzer._determine_project_type(files)

        assert project_type == "node"

    def test_determine_project_type_unknown(self, analyzer):
        """Test determining unknown project type."""
        files = [
            get_mock_file_info({
                "path": Path("/test/readme.txt"),
                "content": "This is a readme"
            }),
        ]

        project_type = analyzer._determine_project_type(files)

        assert project_type == "unknown"

    def test_analyze_python_project(self, analyzer):
        """Test analyzing a Python project."""
        project_path = Path("/test/project")
        files = [
            get_mock_file_info({
                "path": project_path / "requirements.txt",
                "content": "flask==2.0.0\nrequests>=2.25.0"
            }),
            get_mock_file_info({
                "path": project_path / "app.py",
                "content": "from flask import Flask\napp = Flask(__name__)\n\nif __name__ == '__main__':\n    app.run()"
            }),
        ]

        analysis = analyzer._analyze_python_project(project_path, files)

        assert analysis.project_type == "python"
        assert analysis.language == "python"
        assert analysis.framework == "flask"
        assert analysis.package_manager == "pip"
        assert analysis.dependencies is not None and "flask" in analysis.dependencies
        assert analysis.dependencies is not None and "requests" in analysis.dependencies
        assert analysis.entry_points is not None and len(analysis.entry_points) > 0

    def test_analyze_go_project(self, analyzer):
        """Test analyzing a Go project."""
        project_path = Path("/test/project")
        files = [
            get_mock_file_info({
                "path": project_path / "go.mod",
                "content": "module myapp\ngo 1.21\nrequire github.com/gin-gonic/gin v1.9.0"
            }),
            get_mock_file_info({
                "path": project_path / "main.go",
                "content": "package main\nimport \"github.com/gin-gonic/gin\"\nfunc main() {}"
            }),
        ]

        analysis = analyzer._analyze_go_project(project_path, files)

        assert analysis.project_type == "go"
        assert analysis.language == "go"
        assert analysis.framework == "gin"
        assert analysis.package_manager == "go"
        assert analysis.entry_points is not None and len(analysis.entry_points) > 0

    def test_analyze_project_integration(self, analyzer, tmp_path):
        """Test full project analysis integration."""
        # Create a simple Python project
        project_path = tmp_path / "test_project"
        project_path.mkdir()

        (project_path / "requirements.txt").write_text("flask==2.0.0")
        (project_path / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")

        analysis = analyzer.analyze_project(project_path)

        assert analysis.project_type == "python"
        assert analysis.language == "python"
        assert analysis.framework == "flask"
        assert analysis.root_path == project_path
        assert analysis.source_files is not None and len(analysis.source_files) > 0
        assert analysis.config_files is not None and len(analysis.config_files) > 0

    def test_analyze_project_nonexistent_path(self, analyzer):
        """Test analyzing a non-existent project path."""
        with pytest.raises(ValueError, match="does not exist"):
            analyzer.analyze_project(Path("/nonexistent/path"))

    def test_analyze_project_file_instead_of_directory(self, analyzer, tmp_path):
        """Test analyzing a file instead of directory."""
        file_path = tmp_path / "test.py"
        file_path.write_text("print('hello')")

        with pytest.raises(ValueError, match="not a directory"):
            analyzer.analyze_project(file_path)

    def test_parse_requirements_txt(self, analyzer):
        """Test parsing requirements.txt content."""
        content = """flask==2.0.0
requests>=2.25.0
# This is a comment
numpy==1.21.0
pandas>=1.3.0"""

        deps = analyzer._parse_requirements_txt(content)

        assert "flask" in deps
        assert "requests" in deps
        assert "numpy" in deps
        assert "pandas" in deps
        assert len(deps) == 4

    def test_parse_pyproject_toml(self, analyzer):
        """Test parsing pyproject.toml content."""
        content = """[project]
name = "myapp"
dependencies = [
    "flask>=2.0.0",
    "requests>=2.25.0",
]"""

        deps = analyzer._parse_pyproject_toml(content)

        assert "flask" in deps
        assert "requests" in deps

    def test_parse_go_mod(self, analyzer):
        """Test parsing go.mod content."""
        content = """module myapp
go 1.21
require github.com/gin-gonic/gin v1.9.0
require github.com/stretchr/testify v1.8.0"""

        deps = analyzer._parse_go_mod(content)

        assert "github.com/gin-gonic/gin" in deps
        assert "github.com/stretchr/testify" in deps

    def test_parse_package_json(self, analyzer):
        """Test parsing package.json content."""
        content = '{"name": "myapp", "version": "1.0.0", "main": "index.js", "dependencies": {"express": "^4.18.0"}}'

        data = analyzer._parse_package_json(content)

        assert data["name"] == "myapp"
        assert data["main"] == "index.js"
        assert "express" in data["dependencies"]

    def test_parse_invalid_package_json(self, analyzer):
        """Test parsing invalid package.json content."""
        content = '{"name": "myapp", invalid json'

        data = analyzer._parse_package_json(content)

        assert data is None
