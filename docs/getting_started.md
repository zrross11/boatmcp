# Getting Started with BoatMCP

This guide outlines all the tooling dependencies needed to run BoatMCP and test its functionality.

## Core Dependencies

### Python Environment
- **Python 3.11+** - Required for BoatMCP server
- **uv** - Fast Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Container & Kubernetes Tools
- **Docker** - Container runtime
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Ensure Docker daemon is running

- **minikube** - Local Kubernetes cluster
  ```bash
  # macOS
  brew install minikube
  
  # Linux
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  sudo install minikube-linux-amd64 /usr/local/bin/minikube
  
  # Windows
  choco install minikube
  ```

- **kubectl** - Kubernetes CLI (usually installed with minikube)
  ```bash
  # macOS
  brew install kubectl
  
  # Linux
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
  ```

- **Helm** - Kubernetes package manager
  ```bash
  # macOS
  brew install helm
  
  # Linux
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  
  # Windows
  choco install kubernetes-helm
  ```

### MCP Client
- **Claude Desktop** - Primary MCP client for testing
  - [Download Claude Desktop](https://claude.ai/download)
  - Requires Claude subscription for full functionality

## Setup Instructions

### 1. Clone and Setup Project
```bash
git clone <repository-url>
cd boatmcp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add fastmcp httpx
```

### 2. Verify Tool Installation
```bash
# Check Python version
python --version  # Should be 3.11+

# Check uv installation
uv --version

# Check Docker
docker --version
docker ps  # Should connect to daemon

# Check minikube
minikube version

# Check kubectl
kubectl version --client

# Check Helm
helm version
```

### 3. Configure Claude Desktop
Edit the configuration file at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

Add the MCP server configuration:
```json
{
  "mcpServers": {
    "boatmcp": {
      "command": "/Users/<username>/.local/bin/uv",
      "args": [
        "--directory",
        "/full/path/to/your/boatmcp/directory",
        "run",
        "boatmcp"
      ]
    }
  }
}
```

**Important:** Replace `<username>` and `/full/path/to/your/boatmcp/directory` with actual values.

### 4. Test the Setup
```bash
# Start the MCP server
uv run boatmcp

# In another terminal, test minikube
minikube start --driver=docker

# Test basic functionality
minikube status
minikube stop
minikube delete
```

## Optional Tools

### Development Tools
- **git** - Version control
- **VS Code** or your preferred IDE
- **Docker Compose** - Multi-container applications

### Cloud Platforms (for production deployment)
- **AWS CLI** - For EKS deployments
- **Google Cloud SDK** - For GKE deployments
- **Azure CLI** - For AKS deployments

## Next Steps

Once all dependencies are installed and configured:

1. Follow the [Test Prompt Guide](prompt.md) to verify functionality
2. Review the [TODO List](todo.md) for upcoming features
3. Refer to the main [CLAUDE.md](../CLAUDE.md) for development guidelines