"""Minikube-related MCP tools."""

import subprocess
from typing import Any

from fastmcp import FastMCP


def register_minikube_tools(mcp: FastMCP[Any]) -> None:
    """Register all Minikube-related MCP tools."""
    
    @mcp.tool()
    async def create_minikube_cluster(
        profile: str = "boatmcp-cluster",
        cpus: int = 2,
        memory: str = "2048mb",
        disk_size: str = "20gb",
        driver: str = "docker"
    ) -> str:
        """
        Create a new minikube cluster for local Kubernetes development.

        Args:
            profile: Name of the minikube profile/cluster
            cpus: Number of CPUs to allocate
            memory: Amount of memory to allocate
            disk_size: Disk size for the cluster
            driver: Minikube driver to use (docker, virtualbox, etc.)

        Returns:
            Status message with cluster creation results
        """
        try:
            cmd = [
                "minikube", "start",
                "--profile", profile,
                "--cpus", str(cpus),
                "--memory", memory,
                "--disk-size", disk_size,
                "--driver", driver
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Switch to the created cluster profile
                profile_cmd = ["minikube", "profile", profile]
                profile_result = subprocess.run(profile_cmd, capture_output=True, text=True, timeout=30)
                
                output = []
                output.append(f"✅ Minikube cluster '{profile}' created successfully!")
                output.append(f"🖥️  Driver: {driver}")
                output.append(f"💻 CPUs: {cpus}")
                output.append(f"💾 Memory: {memory}")
                output.append(f"💿 Disk: {disk_size}")
                
                if profile_result.returncode == 0:
                    output.append(f"🔄 Switched to profile '{profile}' as active cluster")
                else:
                    output.append(f"⚠️  Warning: Failed to switch to profile '{profile}': {profile_result.stderr}")
                
                output.append("\n📋 Cluster details:")
                output.append(result.stdout)
                return "\n".join(output)
            else:
                return f"❌ Failed to create minikube cluster '{profile}': {result.stderr}"

        except subprocess.TimeoutExpired:
            return f"❌ Timeout creating minikube cluster '{profile}' (exceeded 5 minutes)"
        except Exception as e:
            return f"❌ Error creating minikube cluster '{profile}': {str(e)}"

    @mcp.tool()
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
                output = []
                output.append(f"✅ Minikube cluster '{profile}' deleted successfully!")
                if purge:
                    output.append("🗑️  Cached images and configs purged")
                output.append("\n📋 Deletion details:")
                output.append(result.stdout)
                return "\n".join(output)
            else:
                return f"❌ Failed to delete minikube cluster '{profile}': {result.stderr}"

        except subprocess.TimeoutExpired:
            return f"❌ Timeout deleting minikube cluster '{profile}' (exceeded 2 minutes)"
        except Exception as e:
            return f"❌ Error deleting minikube cluster '{profile}': {str(e)}"