"""Simplified minikube management utilities."""

import subprocess
from typing import Any


async def create_minikube_cluster(
    profile: str = "boatmcp-cluster",
    cpus: int = 2,
    memory: str = "2048mb",
    disk_size: str = "20gb",
    driver: str = "docker",
) -> str:
    """
    Create a new minikube cluster.

    Args:
        profile: Name of the minikube profile/cluster
        cpus: Number of CPUs to allocate
        memory: Amount of memory to allocate
        disk_size: Disk size for the cluster
        driver: Minikube driver to use

    Returns:
        Status message with cluster creation results
    """
    try:
        cmd = [
            "minikube",
            "start",
            "--profile",
            profile,
            "--cpus",
            str(cpus),
            "--memory",
            memory,
            "--disk-size",
            disk_size,
            "--driver",
            driver,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            output = []
            output.append(f"✅ Minikube cluster '{profile}' created successfully!")
            output.append(f"🖥️  Profile: {profile}")
            output.append(f"⚙️  CPUs: {cpus}")
            output.append(f"💾 Memory: {memory}")
            output.append(f"💿 Disk Size: {disk_size}")
            output.append(f"🚗 Driver: {driver}")
            return "\n".join(output)
        else:
            return f"❌ Failed to create minikube cluster '{profile}': {result.stderr}"

    except subprocess.TimeoutExpired:
        return f"❌ Timeout creating minikube cluster '{profile}' (exceeded 10 minutes)"
    except Exception as e:
        return f"❌ Error creating minikube cluster '{profile}': {str(e)}"


async def delete_minikube_cluster(profile: str, purge: bool = False) -> str:
    """
    Delete a minikube cluster.

    Args:
        profile: Name of the minikube profile/cluster to delete
        purge: Whether to purge all cached images and configs

    Returns:
        Status message with deletion results
    """
    try:
        cmd = ["minikube", "delete", "--profile", profile]
        if purge:
            cmd.append("--purge")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            status = "purged" if purge else "deleted"
            return f"✅ Minikube cluster '{profile}' {status} successfully!"
        else:
            return f"❌ Failed to delete minikube cluster '{profile}': {result.stderr}"

    except subprocess.TimeoutExpired:
        return f"❌ Timeout deleting minikube cluster '{profile}' (exceeded 2 minutes)"
    except Exception as e:
        return f"❌ Error deleting minikube cluster '{profile}': {str(e)}"


async def load_image_into_minikube(
    image_name: str, profile: str = "boatmcp-cluster"
) -> str:
    """
    Load a locally built Docker image into a minikube cluster.

    Args:
        image_name: Name and tag of the Docker image to load
        profile: Name of the minikube profile/cluster

    Returns:
        Status message with image loading results
    """
    try:
        cmd = ["minikube", "image", "load", image_name, "--profile", profile]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            output = []
            output.append(
                f"✅ Image '{image_name}' loaded into minikube cluster '{profile}' successfully!"
            )
            output.append(f"🐳 Image: {image_name}")
            output.append(f"🖥️  Cluster: {profile}")
            return "\n".join(output)
        else:
            return f"❌ Failed to load image '{image_name}' into cluster '{profile}': {result.stderr}"

    except subprocess.TimeoutExpired:
        return f"❌ Timeout loading image '{image_name}' (exceeded 5 minutes)"
    except Exception as e:
        return f"❌ Error loading image '{image_name}': {str(e)}"


async def get_minikube_status(profile: str = "boatmcp-cluster") -> dict[str, Any]:
    """
    Get the status of a minikube cluster.

    Args:
        profile: Name of the minikube profile/cluster

    Returns:
        Dict with cluster status information
    """
    try:
        cmd = ["minikube", "status", "--profile", profile, "--format", "json"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            import json

            status_data = json.loads(result.stdout)
            return {"success": True, "status": status_data, "profile": profile}
        else:
            return {
                "success": False,
                "error": result.stderr or "Failed to get cluster status",
                "profile": profile,
            }

    except Exception as e:
        return {"success": False, "error": str(e), "profile": profile}
