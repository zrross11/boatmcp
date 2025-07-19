"""Simple Dockerfile generator without analysis dependency."""

from ...schemas.docker import (
    DockerfileGenerationRequest,
    DockerfileGenerationResult,
)


class DockerfileGenerator:
    """Generates simple Dockerfiles."""

    async def generate_dockerfile(self, request: DockerfileGenerationRequest, analysis: None = None) -> DockerfileGenerationResult:
        """Generate a simple Dockerfile."""
        
        # For now, just return a basic Python Flask dockerfile
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
"""
        
        # Write to output path if specified
        output_path = request.output_path or (request.project_path / "Dockerfile")
        
        try:
            with open(output_path, 'w') as f:
                f.write(dockerfile_content)
            
            return DockerfileGenerationResult(
                success=True,
                dockerfile_path=output_path,
                dockerfile_content=dockerfile_content,
                warnings=["Using basic Flask template - full analysis not implemented yet"]
            )
            
        except Exception as e:
            return DockerfileGenerationResult(
                success=False,
                error=f"Failed to write Dockerfile: {str(e)}"
            )