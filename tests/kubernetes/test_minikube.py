"""Tests for Minikube cluster management functionality."""

from unittest.mock import patch

import pytest

from boatmcp.kubernetes import MinikubeManager


class TestMinikubeManager:
    @pytest.fixture
    def minikube_manager(self) -> MinikubeManager:
        return MinikubeManager()

    @pytest.mark.asyncio
    async def test_load_image_into_cluster_success(self, minikube_manager: MinikubeManager) -> None:
        """Test successful image loading into minikube cluster."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Image loaded successfully"
            mock_run.return_value.stderr = ""

            result = await minikube_manager.load_image_into_cluster(
                image_name="my-app:latest",
                profile="test-cluster"
            )

            assert "✅ Image 'my-app:latest' loaded successfully into cluster 'test-cluster'!" in result
            assert "📁 Profile: test-cluster" in result
            assert "🐳 Image: my-app:latest" in result

    @pytest.mark.asyncio
    async def test_load_image_into_cluster_failure(self, minikube_manager: MinikubeManager) -> None:
        """Test error handling when image loading fails."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Error: image not found"

            result = await minikube_manager.load_image_into_cluster(
                image_name="nonexistent:latest",
                profile="test-cluster"
            )

            assert "❌ Failed to load image 'nonexistent:latest' into cluster 'test-cluster'" in result
            assert "Error: image not found" in result

    @pytest.mark.asyncio
    async def test_load_image_into_cluster_timeout(self, minikube_manager: MinikubeManager) -> None:
        """Test timeout handling for image loading."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("subprocess.TimeoutExpired")

            result = await minikube_manager.load_image_into_cluster(
                image_name="my-app:latest",
                profile="test-cluster"
            )

            assert "❌ Error loading image 'my-app:latest' into cluster 'test-cluster'" in result
            assert "subprocess.TimeoutExpired" in result

    @pytest.mark.asyncio
    async def test_load_image_into_cluster_uses_default_profile(self, minikube_manager: MinikubeManager) -> None:
        """Test that default profile is used when not specified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Image loaded successfully"
            mock_run.return_value.stderr = ""

            result = await minikube_manager.load_image_into_cluster(
                image_name="my-app:latest"
            )

            # Check that the default profile was used
            call_args = mock_run.call_args[0][0]
            assert "--profile" in call_args
            assert "boatmcp-cluster" in call_args
            assert "✅ Image 'my-app:latest' loaded successfully into cluster 'boatmcp-cluster'!" in result

    @pytest.mark.asyncio
    async def test_load_image_into_cluster_command_structure(self, minikube_manager: MinikubeManager) -> None:
        """Test that the correct minikube command is constructed."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Image loaded successfully"
            mock_run.return_value.stderr = ""

            await minikube_manager.load_image_into_cluster(
                image_name="my-app:v1.0.0",
                profile="my-cluster"
            )

            # Verify the command structure
            call_args = mock_run.call_args[0][0]
            expected_cmd = ["minikube", "image", "load", "my-app:v1.0.0", "--profile", "my-cluster"]
            assert call_args == expected_cmd
