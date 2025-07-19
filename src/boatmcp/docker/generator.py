"""Simplified Dockerfile generator with project type detection."""

from pathlib import Path
from typing import Any

from .schemas import DockerfileGenerationRequest, DockerfileGenerationResult


class DockerfileGenerator:
    """Generates Dockerfiles based on project type detection."""

    def __init__(self) -> None:
        """Initialize the generator."""
        pass

    async def generate_dockerfile(
        self,
        request: DockerfileGenerationRequest,
        analysis: Any = None
    ) -> DockerfileGenerationResult:
        """Generate a Dockerfile based on project analysis.

        Args:
            request: The generation request containing project path and options
            analysis: Unused parameter kept for compatibility

        Returns:
            Result containing the generated Dockerfile content
        """
        try:
            # Detect project type
            project_type = self._detect_project_type(request.project_path)

            # Generate Dockerfile content based on project type
            dockerfile_content = self._generate_dockerfile_content(project_type, request)

            # Add custom instructions if provided
            if request.custom_instructions:
                dockerfile_content += "\n# Custom instructions\n"
                for instruction in request.custom_instructions:
                    dockerfile_content += f"{instruction}\n"

            # Determine output path
            output_path = request.output_path or (request.project_path / "Dockerfile")

            # Write Dockerfile
            output_path.write_text(dockerfile_content)

            return DockerfileGenerationResult(
                success=True,
                dockerfile_path=output_path,
                dockerfile_content=dockerfile_content
            )

        except Exception as e:
            return DockerfileGenerationResult(
                success=False,
                error=f"Error generating Dockerfile: {str(e)}"
            )

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect project type based on files present.

        Args:
            project_path: Path to the project directory

        Returns:
            Detected project type (python, node, go, java, rust, generic)
        """
        # Check for Python
        if (project_path / "requirements.txt").exists():
            return "python"
        if (project_path / "pyproject.toml").exists():
            return "python"
        if (project_path / "setup.py").exists():
            return "python"
        if (project_path / "Pipfile").exists():
            return "python"

        # Check for Node.js
        if (project_path / "package.json").exists():
            return "node"

        # Check for Go
        if (project_path / "go.mod").exists():
            return "go"
        if (project_path / "go.sum").exists():
            return "go"

        # Check for Java
        if (project_path / "pom.xml").exists():
            return "java"
        if (project_path / "build.gradle").exists():
            return "java"
        if (project_path / "build.gradle.kts").exists():
            return "java"

        # Check for Rust
        if (project_path / "Cargo.toml").exists():
            return "rust"

        # Default to generic
        return "generic"

    def _generate_dockerfile_content(self, project_type: str, request: DockerfileGenerationRequest) -> str:
        """Generate Dockerfile content for the detected project type.

        Args:
            project_type: The detected project type
            request: The generation request

        Returns:
            Generated Dockerfile content as string
        """
        if project_type == "python":
            return self._generate_python_dockerfile(request)
        elif project_type == "node":
            return self._generate_node_dockerfile(request)
        elif project_type == "go":
            return self._generate_go_dockerfile(request)
        elif project_type == "java":
            return self._generate_java_dockerfile(request)
        elif project_type == "rust":
            return self._generate_rust_dockerfile(request)
        else:
            return self._generate_generic_dockerfile(request)

    def _generate_python_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Generate Python Dockerfile."""
        base_image = "python:3.11-alpine" if request.optimize_for_size else "python:3.11-slim"

        dockerfile = f"""FROM {base_image}

WORKDIR /app

# Install system dependencies for common Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev postgresql-dev

# Copy requirements first for better caching
COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir -r requirements.txt || pip install .

# Copy source code
COPY . .

EXPOSE 8000

# Default command
CMD ["python", "-m", "http.server", "8000"]"""

        return dockerfile

    def _generate_node_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Generate Node.js Dockerfile."""
        base_image = "node:18-alpine" if request.optimize_for_size else "node:18-slim"

        dockerfile = f"""FROM {base_image}

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

EXPOSE 3000

# Default command
CMD ["npm", "start"]"""

        return dockerfile

    def _generate_go_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Generate Go Dockerfile."""
        if request.multi_stage:
            dockerfile = """FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates
WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]"""
        else:
            dockerfile = """FROM golang:1.21-alpine

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build and run
RUN go build -o main .

EXPOSE 8080

CMD ["./main"]"""

        return dockerfile

    def _generate_java_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Generate Java Dockerfile."""
        dockerfile = """FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy source code
COPY . .

# Build with Maven (default)
RUN ./mvnw clean package

EXPOSE 8080

CMD ["java", "-jar", "target/*.jar"]"""

        return dockerfile

    def _generate_rust_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Generate Rust Dockerfile."""
        if request.multi_stage:
            dockerfile = """FROM rust:1.70-slim AS builder

WORKDIR /app

# Copy Cargo files
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY . .

# Build the application
RUN cargo build --release

# Final stage
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /app/target/release/* ./

EXPOSE 8080

CMD ["./main"]"""
        else:
            dockerfile = """FROM rust:1.70-slim

WORKDIR /app

# Copy Cargo files
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY . .

# Build the application
RUN cargo build --release

EXPOSE 8080

CMD ["./target/release/main"]"""

        return dockerfile

    def _generate_generic_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Generate generic Dockerfile."""
        dockerfile = """FROM ubuntu:22.04

WORKDIR /app

# Install basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

EXPOSE 8080

CMD ["echo", "Please configure the command for your application"]"""

        return dockerfile
