# BoatMCP

MCP server that helps developers ship code from local development to production using natural language interactions with Claude.

## What It Does

BoatMCP analyzes your project, generates Dockerfiles, builds containers, and manages Kubernetes deployments through plain English conversations. It eliminates the friction between "it works on my machine" and "it works in production."

**Key Features:**
- Repository analysis and intelligent Dockerfile generation
- Container building with optimization
- Minikube cluster management
- Natural language deployment workflows
- Best practices for security and performance

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [Claude Desktop](https://claude.ai/download)
- Docker (optional: minikube for Kubernetes)

### Installation

```bash
git clone <repository-url>
cd boatmcp
uv venv && source .venv/bin/activate
uv add fastmcp httpx
uv run boatmcp
```

### Programmatic Usage

```python
import boatmcp

# Run the MCP server
boatmcp.run()
```

**Custom integration example:**
```python
#!/usr/bin/env python3
import sys
import boatmcp

def main():
    try:
        boatmcp.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Package installation:**
```bash
pip install boatmcp
python -c "import boatmcp; boatmcp.run()"
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

## Usage

Once configured, restart Claude Desktop and use natural language commands:

- "Analyze my Python project and generate a Dockerfile"
- "Create a minikube cluster for local development"
- "Build a Docker image from my current project"
- "Help me deploy this Node.js app"

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

## Development

```
boatmcp/
├── src/boatmcp/
│   ├── main.py          # MCP server entry point
│   ├── services/        # Business logic
│   └── schemas/         # Data schemas
├── tests/               # Test suite
└── pyproject.toml       # Project config
```

**Contributing:**
1. Fork the repository
2. Create a feature branch
3. Follow TDD principles
4. Test with `uv run boatmcp`
5. Submit a pull request

---

*Built with the Model Context Protocol for seamless AI-powered development workflows.*