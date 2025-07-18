"""Helm chart deployment service."""

import subprocess

from boatmcp.schemas.helm import HelmDeploymentRequest, HelmDeploymentResult


class HelmDeployer:
    """Service for deploying Helm charts to Kubernetes."""

    async def deploy_helm_chart(
        self,
        request: HelmDeploymentRequest
    ) -> HelmDeploymentResult:
        """Deploy a Helm chart to the specified namespace."""
        try:
            # Validate chart path exists
            if not request.chart_path.exists():
                return HelmDeploymentResult(
                    success=False,
                    error="Chart path does not exist"
                )

            # Build helm install command
            cmd = [
                "helm", "install",
                request.release_name,
                str(request.chart_path),
                "--namespace", request.namespace,
                "--create-namespace"
            ]

            # Add values overrides if provided
            if request.values_overrides:
                for key, value in request.values_overrides.items():
                    cmd.extend(["--set", f"{key}={value}"])

            # Add wait flag if specified
            if request.wait:
                cmd.append("--wait")
                cmd.extend(["--timeout", f"{request.timeout}s"])

            # Execute helm install command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=request.timeout + 30  # Add buffer for command execution
            )

            if result.returncode == 0:
                return HelmDeploymentResult(
                    success=True,
                    release_name=request.release_name,
                    namespace=request.namespace
                )
            else:
                return HelmDeploymentResult(
                    success=False,
                    error=result.stderr or "Deployment failed"
                )

        except subprocess.TimeoutExpired:
            return HelmDeploymentResult(
                success=False,
                error=f"Deployment timeout after {request.timeout} seconds"
            )
        except Exception as e:
            return HelmDeploymentResult(
                success=False,
                error=str(e)
            )

    async def uninstall_helm_chart(
        self,
        release_name: str,
        namespace: str = "default"
    ) -> HelmDeploymentResult:
        """Uninstall a Helm chart release."""
        try:
            cmd = [
                "helm", "uninstall",
                release_name,
                "--namespace", namespace
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                return HelmDeploymentResult(
                    success=True,
                    release_name=release_name,
                    namespace=namespace
                )
            else:
                return HelmDeploymentResult(
                    success=False,
                    error=result.stderr or "Uninstall failed"
                )

        except subprocess.TimeoutExpired:
            return HelmDeploymentResult(
                success=False,
                error="Uninstall timeout after 120 seconds"
            )
        except Exception as e:
            return HelmDeploymentResult(
                success=False,
                error=str(e)
            )
