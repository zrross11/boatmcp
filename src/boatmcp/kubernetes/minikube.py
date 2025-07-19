"""Minikube cluster management functionality."""

import subprocess


class MinikubeManager:
    """Service for managing Minikube clusters."""

    async def create_cluster(
        self,
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

    async def delete_cluster(self, profile: str, purge: bool = False) -> str:
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

    async def load_image_into_cluster(
        self,
        image_name: str,
        profile: str = "boatmcp-cluster"
    ) -> str:
        """
        Load a locally built Docker image into a minikube cluster.

        Args:
            image_name: Name and tag of the Docker image to load (e.g., "my-app:latest")
            profile: Name of the minikube profile/cluster to load the image into

        Returns:
            Status message with image loading results
        """
        try:
            cmd = ["minikube", "image", "load", image_name, "--profile", profile]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                output = []
                output.append(f"✅ Image '{image_name}' loaded successfully into cluster '{profile}'!")
                output.append(f"📁 Profile: {profile}")
                output.append(f"🐳 Image: {image_name}")
                output.append("\n📋 Load details:")
                output.append(result.stdout)
                return "\n".join(output)
            else:
                return f"❌ Failed to load image '{image_name}' into cluster '{profile}': {result.stderr}"

        except subprocess.TimeoutExpired:
            return f"❌ Timeout loading image '{image_name}' into cluster '{profile}' (exceeded 3 minutes)"
        except Exception as e:
            return f"❌ Error loading image '{image_name}' into cluster '{profile}': {str(e)}"
