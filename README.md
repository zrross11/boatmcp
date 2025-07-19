# BoatMCP

MCP server that helps developers ship code from local development to production using natural language interactions with Claude or Cursor.

## What It Does

BoatMCP analyzes your project, generates Dockerfiles, builds containers, and manages Kubernetes deployments through plain English conversations. It eliminates the friction between "it works on my machine" and "it works in production."

**Key Features:**
- Repository analysis and intelligent Dockerfile generation
- Docker image building and container management
- Minikube cluster management and image loading
- Helm chart generation and deployment
- Natural language deployment workflows
- Best practices for security and performance

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager  
- [Claude Desktop](https://claude.ai/download) or [Cursor IDE](https://cursor.sh)

See [Getting Started Guide](docs/getting_started.md) for detailed installation instructions for Docker, minikube, Helm, and other dependencies.

### Installation

```bash
git clone <repository-url>
cd boatmcp
uv venv && source .venv/bin/activate
uv sync
```

### Configuration

BoatMCP uses a `config.yaml` file for configuration. Create one in your project root:

```yaml
# BoatMCP Configuration
server:
  # Enable internal development tools (for testing and development)
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

### Running the Server

```bash
# Run with default config.yaml
uv run boatmcp

# Run with custom config file
uv run boatmcp my-custom-config.yaml
```

### Programmatic Usage

```python
import boatmcp

# Run the MCP server programmatically
boatmcp.run()
```

## MCP Client Setup

### Claude Desktop

Edit your Claude Desktop config at `/Users/<username>/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "boatmcp": {
      "command": "/Users/<username>/.local/bin/uv",
      "args": ["--directory", "/full/path/to/boatmcp", "run", "boatmcp"]
    }
  }
}
```

### Cursor IDE

1. Open Cursor IDE
2. Go to Settings → Features → Enable Model Context Protocol (MCP)
3. Add BoatMCP server configuration:

```json
{
  "mcpServers": {
    "boatmcp": {
      "command": "uv",
      "args": ["--directory", "/full/path/to/boatmcp", "run", "boatmcp"]
    }
  }
}
```

**Important:** Replace `<username>` and `/full/path/to/boatmcp` with your actual paths.

## Usage

Once configured, restart your MCP client and use natural language commands:

- "Analyze my Python project and generate a Dockerfile"
- "Create a minikube cluster for local development"
- "Build a Docker image from my current project"
- "Load my Docker image into the minikube cluster"
- "Generate Helm charts for my application"
- "Help me deploy this Node.js app"

## Available MCP Tools

### Core Workflow
- **`minikube_deployment_workflow`** - Complete project-to-production deployment

### Cluster Management  
- **`manage_minikube_cluster`** - Create, start, stop, and delete minikube clusters

### Internal Tools (Development Mode)
When `internal_tools: true` is set in your config.yaml:
- **`analyze_project`** - Detailed project analysis and recommendations
- **`generate_dockerfile`** - Create optimized Dockerfiles
- **`build_docker_image`** - Build and tag Docker images
- **`load_image_to_minikube`** - Load images into minikube registry
- **`generate_helm_chart`** - Create Kubernetes Helm charts
- **`deploy_helm_chart`** - Deploy applications using Helm

## Configuration Options

The `config.yaml` file supports these settings:

```yaml
server:
  internal_tools: false    # Enable development/debugging tools
  transport: "stdio"       # MCP transport type

tools:
  docker:
    enabled: true          # Enable Docker tools
  kubernetes:
    enabled: true          # Enable Kubernetes tools
    default_minikube_profile: "boatmcp-cluster"
  workflows:
    enabled: true          # Enable workflow orchestration
```

## Development

```bash
# Install development dependencies
uv sync --extra dev --extra test

# Run tests
make test

# Run all checks (lint + typecheck + test)
make check

# Run with internal tools enabled
cp config.test.yaml config.yaml  # Enables internal_tools
uv run boatmcp
```

## Architecture

BoatMCP follows a modular MCP server architecture:

- **Core**: Configuration management and server setup
- **Docker**: Container operations and Dockerfile generation  
- **Kubernetes**: Cluster management and Helm operations
- **Workflows**: High-level deployment orchestration

All operations are exposed as MCP tools and can be invoked through natural language interactions with compatible clients.

## Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and architecture details.

---

*Built with the Model Context Protocol for seamless AI-powered development workflows.*