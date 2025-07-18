"""Dockerfile generation based on project analysis."""

from pathlib import Path
from typing import Dict, List, Optional
from ...schemas.repository import ProjectAnalysis
from ...schemas.docker import DockerfileTemplate, DockerfileInstruction, DockerfileGenerationRequest, DockerfileGenerationResult


class DockerfileGenerator:
    """Generates Dockerfiles based on project analysis."""
    
    # Base image mappings
    BASE_IMAGES = {
        "python": {
            "default": "python:3.11-slim",
            "alpine": "python:3.11-alpine",
            "full": "python:3.11"
        },
        "go": {
            "default": "golang:1.21-alpine",
            "alpine": "golang:1.21-alpine",
            "full": "golang:1.21"
        },
        "node": {
            "default": "node:18-alpine",
            "alpine": "node:18-alpine",
            "full": "node:18"
        },
        "java": {
            "default": "openjdk:17-jdk-slim",
            "alpine": "openjdk:17-jdk-alpine",
            "full": "openjdk:17-jdk"
        },
        "rust": {
            "default": "rust:1.70-slim",
            "alpine": "rust:1.70-alpine",
            "full": "rust:1.70"
        }
    }
    
    def __init__(self):
        self.template_generators = {
            "python": self._generate_python_dockerfile,
            "go": self._generate_go_dockerfile,
            "node": self._generate_node_dockerfile,
            "java": self._generate_java_dockerfile,
            "rust": self._generate_rust_dockerfile,
            "unknown": self._generate_generic_dockerfile
        }
    
    async def generate_dockerfile(self, request: DockerfileGenerationRequest, analysis: ProjectAnalysis) -> DockerfileGenerationResult:
        """Generate a Dockerfile based on project analysis."""
        try:
            # Get appropriate template generator
            generator = self.template_generators.get(analysis.project_type, self._generate_generic_dockerfile)
            
            # Generate template
            template = generator(analysis, request)
            
            # Convert template to Dockerfile content
            dockerfile_content = self._template_to_dockerfile(template)
            
            # Add custom instructions if provided
            if request.custom_instructions:
                dockerfile_content += "\n# Custom instructions\n"
                for instruction in request.custom_instructions:
                    dockerfile_content += f"{instruction}\n"
            
            # Determine output path - always default to the scanned directory
            if request.output_path:
                output_path = request.output_path
            else:
                # Always place Dockerfile in the scanned directory, not elsewhere
                output_path = analysis.root_path / "Dockerfile"
            
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
    
    def _generate_python_dockerfile(self, analysis: ProjectAnalysis, request: DockerfileGenerationRequest) -> DockerfileTemplate:
        """Generate Dockerfile template for Python projects."""
        base_image = self.BASE_IMAGES["python"]["alpine" if request.optimize_for_size else "default"]
        
        instructions = [
            DockerfileInstruction("FROM", base_image),
            DockerfileInstruction("WORKDIR", "/app"),
        ]
        
        # Add system dependencies for common Python packages
        if any(dep in analysis.dependencies for dep in ["pillow", "psycopg2", "lxml", "numpy", "scipy"]):
            instructions.append(DockerfileInstruction(
                "RUN", 
                "apk add --no-cache gcc musl-dev libffi-dev openssl-dev postgresql-dev",
                "System dependencies for common Python packages"
            ))
        
        # Copy requirements first for better caching
        if any(f.path.name in ["requirements.txt", "pyproject.toml"] for f in analysis.config_files):
            instructions.extend([
                DockerfileInstruction("COPY", "requirements.txt* pyproject.toml* ./"),
                DockerfileInstruction("RUN", "pip install --no-cache-dir -r requirements.txt || pip install .", "Install dependencies")
            ])
        
        # Copy source code
        instructions.extend([
            DockerfileInstruction("COPY", ". ."),
            DockerfileInstruction("EXPOSE", "8000")
        ])
        
        # Set default command
        if analysis.entry_points:
            entry_point = analysis.entry_points[0]
            if analysis.framework == "flask":
                instructions.append(DockerfileInstruction("CMD", f'["python", "{entry_point}"]'))
            elif analysis.framework == "django":
                instructions.append(DockerfileInstruction("CMD", '["python", "manage.py", "runserver", "0.0.0.0:8000"]'))
            elif analysis.framework == "fastapi":
                instructions.append(DockerfileInstruction("CMD", f'["uvicorn", "{entry_point}:app", "--host", "0.0.0.0", "--port", "8000"]'))
            else:
                instructions.append(DockerfileInstruction("CMD", f'["python", "{entry_point}"]'))
        else:
            instructions.append(DockerfileInstruction("CMD", '["python", "-m", "http.server", "8000"]'))
        
        return DockerfileTemplate(
            base_image=base_image,
            instructions=instructions,
            metadata={"language": "python", "framework": analysis.framework}
        )
    
    def _generate_go_dockerfile(self, analysis: ProjectAnalysis, request: DockerfileGenerationRequest) -> DockerfileTemplate:
        """Generate Dockerfile template for Go projects."""
        if request.multi_stage:
            # Multi-stage build
            instructions = [
                DockerfileInstruction("FROM", "golang:1.21-alpine AS builder"),
                DockerfileInstruction("WORKDIR", "/app"),
                DockerfileInstruction("COPY", "go.mod go.sum ./"),
                DockerfileInstruction("RUN", "go mod download"),
                DockerfileInstruction("COPY", ". ."),
                DockerfileInstruction("RUN", "CGO_ENABLED=0 GOOS=linux go build -o main ."),
                DockerfileInstruction("FROM", "alpine:latest"),
                DockerfileInstruction("RUN", "apk --no-cache add ca-certificates"),
                DockerfileInstruction("WORKDIR", "/root/"),
                DockerfileInstruction("COPY", "--from=builder /app/main ."),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["./main"]')
            ]
            base_image = "golang:1.21-alpine"
        else:
            # Single stage build
            base_image = self.BASE_IMAGES["go"]["default"]
            instructions = [
                DockerfileInstruction("FROM", base_image),
                DockerfileInstruction("WORKDIR", "/app"),
                DockerfileInstruction("COPY", "go.mod go.sum ./"),
                DockerfileInstruction("RUN", "go mod download"),
                DockerfileInstruction("COPY", ". ."),
                DockerfileInstruction("RUN", "go build -o main ."),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["./main"]')
            ]
        
        return DockerfileTemplate(
            base_image=base_image,
            instructions=instructions,
            metadata={"language": "go", "framework": analysis.framework}
        )
    
    def _generate_node_dockerfile(self, analysis: ProjectAnalysis, request: DockerfileGenerationRequest) -> DockerfileTemplate:
        """Generate Dockerfile template for Node.js projects."""
        base_image = self.BASE_IMAGES["node"]["alpine" if request.optimize_for_size else "default"]
        
        instructions = [
            DockerfileInstruction("FROM", base_image),
            DockerfileInstruction("WORKDIR", "/app"),
            DockerfileInstruction("COPY", "package*.json ./"),
        ]
        
        # Use appropriate package manager
        if analysis.package_manager == "yarn":
            instructions.extend([
                DockerfileInstruction("COPY", "yarn.lock ./"),
                DockerfileInstruction("RUN", "yarn install --frozen-lockfile")
            ])
        elif analysis.package_manager == "pnpm":
            instructions.extend([
                DockerfileInstruction("COPY", "pnpm-lock.yaml ./"),
                DockerfileInstruction("RUN", "npm install -g pnpm && pnpm install --frozen-lockfile")
            ])
        else:
            instructions.append(DockerfileInstruction("RUN", "npm ci"))
        
        instructions.extend([
            DockerfileInstruction("COPY", ". ."),
            DockerfileInstruction("EXPOSE", "3000")
        ])
        
        # Set command based on framework
        if analysis.framework == "react":
            instructions.extend([
                DockerfileInstruction("RUN", "npm run build"),
                DockerfileInstruction("CMD", '["npm", "start"]')
            ])
        else:
            instructions.append(DockerfileInstruction("CMD", '["npm", "start"]'))
        
        return DockerfileTemplate(
            base_image=base_image,
            instructions=instructions,
            metadata={"language": "javascript", "framework": analysis.framework}
        )
    
    def _generate_java_dockerfile(self, analysis: ProjectAnalysis, request: DockerfileGenerationRequest) -> DockerfileTemplate:
        """Generate Dockerfile template for Java projects."""
        base_image = self.BASE_IMAGES["java"]["default"]
        
        instructions = [
            DockerfileInstruction("FROM", base_image),
            DockerfileInstruction("WORKDIR", "/app"),
            DockerfileInstruction("COPY", ". ."),
        ]
        
        # Add build commands based on build tool
        if any(f.path.name == "pom.xml" for f in analysis.config_files):
            instructions.extend([
                DockerfileInstruction("RUN", "./mvnw clean package"),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["java", "-jar", "target/*.jar"]')
            ])
        elif any(f.path.name == "build.gradle" for f in analysis.config_files):
            instructions.extend([
                DockerfileInstruction("RUN", "./gradlew build"),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["java", "-jar", "build/libs/*.jar"]')
            ])
        else:
            instructions.extend([
                DockerfileInstruction("RUN", "javac *.java"),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["java", "Main"]')
            ])
        
        return DockerfileTemplate(
            base_image=base_image,
            instructions=instructions,
            metadata={"language": "java"}
        )
    
    def _generate_rust_dockerfile(self, analysis: ProjectAnalysis, request: DockerfileGenerationRequest) -> DockerfileTemplate:
        """Generate Dockerfile template for Rust projects."""
        if request.multi_stage:
            # Multi-stage build
            instructions = [
                DockerfileInstruction("FROM", "rust:1.70 as builder"),
                DockerfileInstruction("WORKDIR", "/app"),
                DockerfileInstruction("COPY", "Cargo.toml Cargo.lock ./"),
                DockerfileInstruction("RUN", "cargo build --release"),
                DockerfileInstruction("COPY", "src ./src"),
                DockerfileInstruction("RUN", "cargo build --release"),
                DockerfileInstruction("FROM", "debian:bookworm-slim"),
                DockerfileInstruction("COPY", "--from=builder /app/target/release/main /usr/local/bin/main"),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["main"]')
            ]
            base_image = "rust:1.70"
        else:
            base_image = self.BASE_IMAGES["rust"]["default"]
            instructions = [
                DockerfileInstruction("FROM", base_image),
                DockerfileInstruction("WORKDIR", "/app"),
                DockerfileInstruction("COPY", ". ."),
                DockerfileInstruction("RUN", "cargo build --release"),
                DockerfileInstruction("EXPOSE", "8080"),
                DockerfileInstruction("CMD", '["./target/release/main"]')
            ]
        
        return DockerfileTemplate(
            base_image=base_image,
            instructions=instructions,
            metadata={"language": "rust"}
        )
    
    def _generate_generic_dockerfile(self, analysis: ProjectAnalysis, request: DockerfileGenerationRequest) -> DockerfileTemplate:
        """Generate generic Dockerfile template."""
        base_image = "ubuntu:22.04"
        
        instructions = [
            DockerfileInstruction("FROM", base_image),
            DockerfileInstruction("WORKDIR", "/app"),
            DockerfileInstruction("COPY", ". ."),
            DockerfileInstruction("EXPOSE", "8080"),
            DockerfileInstruction("CMD", '["echo", "Please configure the command for your application"]')
        ]
        
        return DockerfileTemplate(
            base_image=base_image,
            instructions=instructions,
            metadata={"language": "unknown"}
        )
    
    def _template_to_dockerfile(self, template: DockerfileTemplate) -> str:
        """Convert template to Dockerfile content."""
        lines = []
        
        for instruction in template.instructions:
            line = f"{instruction.instruction} {instruction.arguments}"
            if instruction.comment:
                line += f"  # {instruction.comment}"
            lines.append(line)
        
        return "\n".join(lines)