# BoatMCP

MCP server that helps developers ship code from local development to production using natural language interactions with Claude.

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
- [Claude Desktop](https://claude.ai/download)

See [Getting Started Guide](docs/getting_started.md) for detailed installation instructions for Docker, minikube, Helm, and other dependencies.

### Installation

```bash
git clone <repository-url>
cd boatmcp
uv venv && source .venv/bin/activate
uv sync
```

### Running the Server

```bash
# Run as MCP server for Claude Desktop
uv run boatmcp
```

### Programmatic Usage

```python
import boatmcp

# Run the MCP server programmatically
boatmcp.run()
```

### Claude Desktop Setup

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

**Important:** Replace `<username>` and `/full/path/to/boatmcp` with your actual paths.

## Usage

Once configured, restart Claude Desktop and use natural language commands:

- "Analyze my Python project and generate a Dockerfile"
- "Create a minikube cluster for local development"
- "Build a Docker image from my current project"
- "Load my Docker image into the minikube cluster"
- "Generate Helm charts for my application"
- "Help me deploy this Node.js app"

## Available MCP Tools

BoatMCP provides the following tools through the Model Context Protocol:

### Docker Tools
- **Build Docker images** - Analyze projects and create optimized Docker images
- **Manage containers** - Start, stop, and inspect Docker containers

### Minikube Tools  
- **Create clusters** - Set up local Kubernetes clusters with custom configurations
- **Delete clusters** - Clean up test clusters with optional data purging
- **Load images** - Load locally built Docker images into minikube clusters

### Helm Tools
- **Generate charts** - Create Helm charts from project analysis
- **Deploy applications** - Deploy Helm charts to Kubernetes clusters
- **Manage releases** - Install, upgrade, and uninstall Helm releases

## Use Cases

- **Rapid Deployment**: Local to containerized application quickly
- **Learning**: Understand deployment concepts through guided interactions
- **Development**: Consistent local Kubernetes environments
- **CI/CD**: Generate deployment artifacts for production pipelines
- **Standardization**: Consistent deployment patterns across projects

## Target Users

- Developers who want to ship code without deep DevOps expertise
- Teams standardizing deployment practices
- Students learning container and Kubernetes technologies
- Anyone preferring natural language over complex deployment commands

## Contributing

We welcome contributions! Here's how to get started:

1. **Clone the repository** (no fork needed for contributions)
2. **Create a feature branch** from main
3. **Follow TDD principles** - write tests first, then implementation
4. **Test your changes** with `uv run pytest`
5. **Verify the MCP server** runs with `uv run src/boatmcp/main.py`
6. **Submit a pull request** to the main repository

**Development Guidelines:**
- Follow the TDD workflow outlined in [CLAUDE.md](CLAUDE.md)
- Ensure all tests pass before submitting PRs
- Use type hints and follow the project's coding standards
- Add documentation for new features

## Documentation

- [Getting Started Guide](docs/getting_started.md) - Complete setup instructions
- [Development Guidelines](CLAUDE.md) - TDD workflow and coding standards
- [Test Prompt](docs/prompt.md) - How to test MCP functionality
- [TODO List](docs/todo.md) - Planned features and improvements

---

*Built with the Model Context Protocol for seamless AI-powered development workflows.*