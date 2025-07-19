"""Simplified Helm chart generation utilities."""

import subprocess
from pathlib import Path
from typing import Any


def generate_helm_chart(
    project_path: Path,
    chart_name: str,
    app_version: str = "1.0.0",
    chart_version: str = "0.1.0",
    image_name: str | None = None,
    image_tag: str = "latest",
    port: int = 80,
    namespace: str = "default",
) -> dict[str, Any]:
    """
    Generate a Helm chart for a project.

    Args:
        project_path: Path to the project root directory
        chart_name: Name for the Helm chart
        app_version: Version of the application
        chart_version: Version of the Helm chart
        image_name: Name of the Docker image (defaults to chart_name)
        image_tag: Tag for the Docker image
        port: Port the application runs on
        namespace: Kubernetes namespace

    Returns:
        Dict with success status, chart_path, and any warnings/errors
    """
    try:
        if image_name is None:
            image_name = chart_name

        # Create helm directory structure
        helm_dir = project_path / "helm"
        chart_dir = helm_dir / chart_name
        templates_dir = chart_dir / "templates"

        # Create directories
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Template parameters
        template_params = {
            "chart_name": chart_name,
            "app_version": app_version,
            "chart_version": chart_version,
            "image_name": image_name,
            "image_tag": image_tag,
            "port": port,
            "namespace": namespace,
        }

        # Generate all chart files
        _create_chart_file(chart_dir, "Chart.yaml", template_params)
        _create_chart_file(chart_dir, "values.yaml", template_params)
        _create_chart_file(templates_dir, "deployment.yaml", template_params)
        _create_chart_file(templates_dir, "service.yaml", template_params)
        _create_chart_file(templates_dir, "_helpers.tpl", template_params)

        return {"success": True, "chart_path": chart_dir, "warnings": []}

    except Exception as e:
        return {"success": False, "chart_path": None, "error": str(e)}


def deploy_helm_chart(
    chart_path: Path,
    release_name: str,
    namespace: str = "default",
    values_overrides: dict[str, Any] | None = None,
    wait: bool = True,
    timeout: int = 300,
) -> dict[str, Any]:
    """
    Deploy a Helm chart to Kubernetes.

    Args:
        chart_path: Path to the Helm chart directory
        release_name: Name for the Helm release
        namespace: Kubernetes namespace to deploy to
        values_overrides: Optional values to override
        wait: Whether to wait for the deployment to complete
        timeout: Timeout in seconds for the deployment

    Returns:
        Dict with success status, release info, and any warnings/errors
    """
    try:
        # Build helm command
        cmd = [
            "helm",
            "install",
            release_name,
            str(chart_path),
            "--namespace",
            namespace,
            "--create-namespace",
        ]

        # Add value overrides
        if values_overrides:
            for key, value in values_overrides.items():
                cmd.extend(["--set", f"{key}={value}"])

        # Add wait and timeout if specified
        if wait:
            cmd.extend(["--wait", "--timeout", f"{timeout}s"])

        # Execute helm command
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 30
        )

        if result.returncode == 0:
            return {
                "success": True,
                "release_name": release_name,
                "namespace": namespace,
                "warnings": [],
            }
        else:
            return {
                "success": False,
                "release_name": release_name,
                "namespace": namespace,
                "error": result.stderr or "Deployment failed",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "release_name": release_name,
            "namespace": namespace,
            "error": f"Deployment timed out after {timeout} seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "release_name": release_name,
            "namespace": namespace,
            "error": str(e),
        }


def uninstall_helm_chart(
    release_name: str, namespace: str = "default"
) -> dict[str, Any]:
    """
    Uninstall a Helm chart release.

    Args:
        release_name: Name of the Helm release to uninstall
        namespace: Kubernetes namespace the release is in

    Returns:
        Dict with success status and any warnings/errors
    """
    try:
        cmd = ["helm", "uninstall", release_name, "--namespace", namespace]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return {
                "success": True,
                "release_name": release_name,
                "namespace": namespace,
                "warnings": [],
            }
        else:
            return {
                "success": False,
                "release_name": release_name,
                "namespace": namespace,
                "error": result.stderr or "Uninstall failed",
            }

    except Exception as e:
        return {
            "success": False,
            "release_name": release_name,
            "namespace": namespace,
            "error": str(e),
        }


def _create_chart_file(directory: Path, filename: str, params: dict[str, Any]) -> None:
    """Create a chart file from template."""
    # Get template file path
    template_dir = Path(__file__).parent.parent / "templates" / "helm"
    template_file = template_dir / f"{filename}.template"

    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Read template content
    template_content = template_file.read_text()

    # Replace template parameters
    content = template_content.format(**params)

    # Write to destination
    output_file = directory / filename
    output_file.write_text(content)
