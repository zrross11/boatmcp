# nlpi
Natural-Language-Processed Infrastructure

**nlpi** is a Model Context Protocol (FastMCP) server that enables developers and DevOps engineers to create, manage, and deploy infrastructure as code using natural language. By leveraging advanced language models, nlpi transforms human-readable infrastructure requirements into production-ready Infrastructure as Code (IaC) templates.

## 🚀 Features

- **Natural Language to IaC**: Convert plain English descriptions into Terraform, CloudFormation, or other IaC formats
- **Multi-Cloud Support**: Generate infrastructure code for AWS, Azure, Google Cloud, and other providers
- **Interactive Refinement**: Iteratively improve and modify infrastructure definitions through conversation
- **Best Practices Integration**: Automatically incorporates security, scalability, and cost optimization best practices
- **Template Management**: Save, version, and reuse infrastructure patterns
- **Validation & Testing**: Built-in validation for generated infrastructure code

## 🛠 How It Works

nlpi acts as an FastMCP server that can be integrated with various AI clients and development environments. When you describe your infrastructure needs in natural language, nlpi:

1. **Parses** your requirements using advanced NLP techniques
2. **Translates** them into appropriate IaC syntax and structure
3. **Validates** the generated code for syntax and best practices
4. **Provides** explanations and suggestions for improvements
5. **Enables** iterative refinement through follow-up conversations

## 💡 Use Cases

- **Rapid Prototyping**: Quickly spin up development environments
- **Learning Tool**: Help newcomers understand infrastructure concepts
- **Documentation**: Generate IaC from existing infrastructure descriptions
- **Migration**: Convert legacy setups to modern IaC practices
- **Standardization**: Ensure consistent infrastructure patterns across teams

## 🎯 Target Users

- **DevOps Engineers** looking to accelerate infrastructure provisioning
- **Developers** who need infrastructure but aren't IaC experts
- **Platform Teams** building self-service infrastructure capabilities
- **Students and Learners** exploring cloud infrastructure concepts

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** 
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Claude Desktop](https://claude.ai/download)** - Required for local development and testing

### Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd nlpi
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

To use nlpi with Claude Desktop, you need to configure the FastMCP server in your Claude Desktop settings.

**Update your Claude Desktop config file:**

**Location:** `/Users/<username>/Library/Application Support/Claude/claude_desktop_config.json`

**Contents:**
```json
{
  "mcpServers": {
    "infrastructure-tools": {
      "command": "/Users/<username>/.local/bin/uv",
      "args": [
        "--directory",
        "/full/path/to/your/nlpi/directory",
        "run",
        "main.py"
      ]
    }
  }
}
```

**Important:** Replace `<username>` and `/path/to/your/nlpi/directory` with real values.

### Usage

Once configured, restart Claude Desktop and you'll have access to nlpi's infrastructure management tools through natural language commands in your Claude conversations.

**Example commands:**
- Create a minikube cluster with custom specifications
- Delete specific clusters by name
- Manage Kubernetes environments through simple requests

## 🔧 Integration

As an FastMCP server, nlpi can be integrated with:
- IDEs and code editors with FastMCP support
- CI/CD pipelines for automated infrastructure generation
- Custom applications via the FastMCP protocol
- Command-line tools and scripts

## 🛠 Development

The project structure:
```
nlpi/
├── main.py              # FastMCP server entrypoint
├── app/                 # Application modules
│   └── minikube/        # Minikube management functionality
├── pyproject.toml       # Project configuration
└── uv.lock             # Dependency lock file
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `uv run main.py`
5. Submit a pull request

---

*Built with the Model Context Protocol for seamless integration with AI-powered development workflows.*
