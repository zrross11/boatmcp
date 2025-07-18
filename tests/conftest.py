"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def python_project_dir(temp_project_dir):
    """Create a sample Python project for testing."""
    project_dir = temp_project_dir / "python_project"
    project_dir.mkdir()
    
    # Create app.py
    (project_dir / "app.py").write_text("""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
""")
    
    # Create requirements.txt
    (project_dir / "requirements.txt").write_text("flask==2.3.2\n")
    
    return project_dir


@pytest.fixture
def go_project_dir(temp_project_dir):
    """Create a sample Go project for testing."""
    project_dir = temp_project_dir / "go_project"
    project_dir.mkdir()
    
    # Create main.go
    (project_dir / "main.go").write_text("""
package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, World!")
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)
}
""")
    
    # Create go.mod
    (project_dir / "go.mod").write_text("""
module testproject

go 1.21
""")
    
    return project_dir