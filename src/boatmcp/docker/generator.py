"""Dockerfile generation utilities."""

import re
import subprocess
from pathlib import Path

from ..core.analysis import ProjectAnalysis


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

    if project_type == "python":
        return _generate_python_dockerfile(
            analysis, port, optimize_for_size, multi_stage
        )
    elif project_type == "node.js":
        return _generate_nodejs_dockerfile(
            analysis, port, optimize_for_size, multi_stage
        )
    elif project_type == "go":
        return _generate_go_dockerfile(analysis, port, optimize_for_size, multi_stage)
    elif project_type == "rust":
        return _generate_rust_dockerfile(analysis, port, optimize_for_size, multi_stage)
    elif project_type == "java":
        return _generate_java_dockerfile(analysis, port, optimize_for_size, multi_stage)
    else:
        return _generate_generic_dockerfile(analysis, port)


def _generate_python_dockerfile(
    analysis: ProjectAnalysis, port: int, optimize_for_size: bool, multi_stage: bool
) -> str:
    """Generate Python Dockerfile."""
    base_image = "python:3.11-slim" if optimize_for_size else "python:3.11"

    # Detect main application file
    main_file = "app.py"
    if "main.py" in analysis.project_files:
        main_file = "main.py"
    elif "server.py" in analysis.project_files:
        main_file = "server.py"

    content = f"""FROM {base_image}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["python", "{main_file}"]
"""
    return content


def _generate_nodejs_dockerfile(
    analysis: ProjectAnalysis, port: int, optimize_for_size: bool, multi_stage: bool
) -> str:
    """Generate Node.js Dockerfile."""
    base_image = "node:18-alpine" if optimize_for_size else "node:18"

    # Detect main application file
    main_file = "index.js"
    if "server.js" in analysis.project_files:
        main_file = "server.js"
    elif "app.js" in analysis.project_files:
        main_file = "app.js"

    content = f"""FROM {base_image}

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE {port}

CMD ["node", "{main_file}"]
"""
    return content


def _generate_go_dockerfile(
    analysis: ProjectAnalysis, port: int, optimize_for_size: bool, multi_stage: bool
) -> str:
    """Generate Go Dockerfile."""
    # Detect user's Go version
    go_version = _detect_go_version()

    if multi_stage:
        builder_image = f"golang:{go_version}-alpine"
        content = f"""FROM {builder_image} AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/main .

EXPOSE {port}

CMD ["./main"]
"""
    else:
        base_image = (
            f"golang:{go_version}-alpine"
            if optimize_for_size
            else f"golang:{go_version}"
        )
        content = f"""FROM {base_image}

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o main .

EXPOSE {port}

CMD ["./main"]
"""
    return content


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


def _generate_rust_dockerfile(
    analysis: ProjectAnalysis, port: int, optimize_for_size: bool, multi_stage: bool
) -> str:
    """Generate Rust Dockerfile."""
    if multi_stage:
        content = f"""FROM rust:1.70 AS builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN cargo fetch

COPY . .
RUN cargo build --release

FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY --from=builder /app/target/release/* ./

EXPOSE {port}

CMD ["./main"]
"""
    else:
        base_image = "rust:1.70-slim" if optimize_for_size else "rust:1.70"
        content = f"""FROM {base_image}

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
RUN cargo fetch

COPY . .
RUN cargo build --release

EXPOSE {port}

CMD ["./target/release/main"]
"""
    return content


def _generate_java_dockerfile(
    analysis: ProjectAnalysis, port: int, optimize_for_size: bool, multi_stage: bool
) -> str:
    """Generate Java Dockerfile."""
    base_image = "openjdk:11-jre-slim" if optimize_for_size else "openjdk:11"

    if analysis.dependency_files.get("pom.xml"):
        # Maven project
        if multi_stage:
            content = f"""FROM maven:3.8-openjdk-11 AS builder

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline

COPY . .
RUN mvn package -DskipTests

FROM {base_image}
WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar

EXPOSE {port}

CMD ["java", "-jar", "app.jar"]
"""
        else:
            content = f"""FROM maven:3.8-openjdk-11

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY . .
RUN mvn package -DskipTests

EXPOSE {port}

CMD ["java", "-jar", "target/*.jar"]
"""
    else:
        # Gradle project
        content = f"""FROM {base_image}

WORKDIR /app

COPY . .
RUN ./gradlew build

EXPOSE {port}

CMD ["java", "-jar", "build/libs/*.jar"]
"""

    return content


def _generate_generic_dockerfile(analysis: ProjectAnalysis, port: int) -> str:
    """Generate generic Dockerfile."""
    content = f"""FROM alpine:latest

WORKDIR /app

COPY . .

EXPOSE {port}

CMD ["./app"]
"""
    return content


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
