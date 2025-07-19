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
Choose one of these MCP-compatible clients:

- **Claude Desktop** - Standalone AI assistant
  - [Download Claude Desktop](https://claude.ai/download)
  - Requires Claude subscription for full functionality

- **Cursor IDE** - AI-powered code editor with built-in MCP support
  - [Download Cursor IDE](https://cursor.sh)
  - Integrates seamlessly with your development workflow

## Setup Instructions

### 1. Clone and Setup Project
```bash
git clone <repository-url>
cd boatmcp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### 2. Create Configuration File
Create a `config.yaml` file in the project root:

```yaml
# BoatMCP Configuration
server:
  # Set to true for development/testing to access internal tools
  internal_tools: false
  transport: "stdio"

tools:
  docker:
    enabled: true
  kubernetes:
    enabled: true
    default_minikube_profile: "boatmcp-cluster"
  workflows:
    enabled: true
```

**Configuration Options:**
- `internal_tools: false` - Production mode (recommended for daily use)
- `internal_tools: true` - Development mode (exposes additional debugging tools)

### 3. Verify Tool Installation
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

### 4. Configure MCP Client

#### Option A: Claude Desktop
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

#### Option B: Cursor IDE
1. Open Cursor IDE
2. Go to **Settings** → **Features** → **Enable Model Context Protocol (MCP)**
3. Configure BoatMCP server in the MCP settings:

```json
{
  "mcpServers": {
    "boatmcp": {
      "command": "uv",
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

### 5. Test the Setup
```bash
# Test BoatMCP server starts correctly
uv run boatmcp

# In another terminal, test minikube
minikube start --driver=docker

# Test basic functionality
minikube status
minikube stop
minikube delete
```

## Configuration Modes

### Production Mode (Default)
```yaml
server:
  internal_tools: false
```
- **Use for**: Daily development work
- **Available tools**: Core workflow and cluster management
- **Benefits**: Clean interface, essential tools only

### Development Mode
```yaml
server:
  internal_tools: true
```
- **Use for**: Debugging, learning, advanced workflows
- **Available tools**: All tools including project analysis, individual Docker/Helm operations
- **Benefits**: Fine-grained control, step-by-step debugging

You can switch modes by editing `config.yaml` or using a custom config file:
```bash
# Use development config
uv run boatmcp config.dev.yaml

# Use production config (default)
uv run boatmcp
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

1. **Test Basic Functionality**: Follow the [Test Prompt Guide](prompt.md) to verify everything works
2. **Start Development**: Review the [Development Guidelines](../CLAUDE.md) for coding standards
3. **Deploy Your First App**: Use BoatMCP to deploy the included example applications

## Troubleshooting

### Common Issues

**MCP Server Not Starting:**
- Ensure `config.yaml` exists and has valid YAML syntax
- Check that all dependencies are installed: `uv sync`
- Verify Python version is 3.11+

**Docker Issues:**
- Make sure Docker Desktop is running
- Test with: `docker run hello-world`

**Minikube Issues:**
- Check virtualization is enabled on your system
- Try different driver: `minikube start --driver=virtualbox`

**Configuration Not Loading:**
- Ensure `config.yaml` is in the directory where you run `uv run boatmcp`
- Check file permissions and syntax
- Use `uv run boatmcp --help` to see available options

Need help? Check the project issues or create a new one with your setup details.