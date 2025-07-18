# BoatMCP

BoatMCP is an MCP (Model Context Protocol) server designed to help developers ship code from local development to production using natural language interactions with an LLM client.

## 🚀 Mission Statement

BoatMCP's mission is to eliminate the friction between "it works on my machine" and "it works in production" by providing intelligent tooling that guides developers through deployment workflows using plain English conversations with Claude or other MCP-compatible LLMs.

## 🛠 Features

- **Repository Analysis**: Intelligent scanning of project structure, dependencies, and configuration
- **Dockerfile Generation**: Automated creation of optimized Dockerfiles based on project analysis
- **Container Building**: Docker image building with intelligent defaults and optimization
- **Kubernetes Integration**: Minikube cluster management for local development
- **Natural Language Interface**: Describe deployment goals in plain English
- **Best Practices**: Incorporates security, performance, and deployment best practices

## 🛠 How It Works

BoatMCP acts as an MCP server that integrates with Claude Desktop and other MCP-compatible clients. When you describe your deployment needs in natural language, BoatMCP:

1. **Analyzes** your project structure and dependencies
2. **Generates** appropriate infrastructure code (Dockerfiles, configs)
3. **Builds** container images with optimized settings
4. **Provisions** local development environments (minikube)
5. **Guides** you through deployment workflows step-by-step

## 💡 Use Cases

- **Rapid Deployment**: Go from local code to containerized application quickly
- **Learning Tool**: Understand deployment concepts through guided interactions
- **Development Environments**: Spin up consistent local Kubernetes environments
- **CI/CD Preparation**: Generate deployment artifacts for production pipelines
- **Standardization**: Ensure consistent deployment patterns across projects

## 🎯 Target Users

- **Developers** who want to ship code without deep DevOps expertise
- **Teams** looking to standardize deployment practices
- **Students** learning container and Kubernetes technologies
- **Anyone** who prefers natural language over complex deployment commands

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (project uses 3.12+ as recommended)
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Claude Desktop](https://claude.ai/download)** - Required for MCP client interaction
- **Docker** - For container building functionality
- **minikube** - For Kubernetes cluster management (optional)

### Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd boatmcp
   ```

2. **Set up Python environment with uv:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv add fastmcp httpx
   ```

4. **Test the server:**
   ```bash
   uv run main.py
   ```

### Claude Desktop Configuration

To use BoatMCP with Claude Desktop, you need to configure the MCP server in your Claude Desktop settings.

**Update your Claude Desktop config file:**

**Location:** `/Users/<username>/Library/Application Support/Claude/claude_desktop_config.json`

**Contents:**
```json
{
  "mcpServers": {
    "boatmcp": {
      "command": "/Users/<username>/.local/bin/uv",
      "args": [
        "--directory",
        "/full/path/to/your/boatmcp/directory",
        "run",
        "main.py"
      ]
    }
  }
}
```

**Important:** Replace `<username>` and `/path/to/your/boatmcp/directory` with actual values.

### Usage

Once configured, restart Claude Desktop and you'll have access to BoatMCP's deployment tools through natural language commands in your Claude conversations.

**Example commands:**
- "Analyze my Python project and generate a Dockerfile"
- "Create a minikube cluster for local development"
- "Build a Docker image from my current project"
- "Help me deploy this Node.js app to production"

## 🔧 Integration

As an MCP server, BoatMCP can be integrated with:
- **Claude Desktop** for interactive deployment workflows
- **IDEs and editors** with MCP support
- **CI/CD pipelines** for automated deployment preparation
- **Custom applications** via the MCP protocol
- **Command-line tools** and scripts

## 🛠 Development

The project structure:
```
boatmcp/
├── main.py              # MCP server entrypoint
├── src/
│   └── boatmcp/         # Main application package
│       ├── main.py      # Core MCP server logic
│       ├── services/    # Business logic services
│       │   ├── repository.py   # Repository analysis
│       │   └── docker.py      # Dockerfile generation
│       └── schemas/     # Data schemas
│           ├── repository.py   # Repository schemas
│           └── docker.py      # Docker schemas
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── uv.lock             # Dependency lock file
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following TDD principles
4. Test with `uv run main.py`
5. Submit a pull request

### Development Guidelines

- Follow Test-Driven Development (TDD)
- All code must have type hints
- Use pytest for testing
- Follow the existing code structure and patterns

---

*Built with the Model Context Protocol for seamless integration with AI-powered development workflows.*