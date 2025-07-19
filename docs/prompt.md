# BoatMCP Test Guide

Once you have BoatMCP set up and running, use these prompts in Claude Desktop or Cursor IDE to test the MCP server functionality.

## Configuration Modes

BoatMCP has two configuration modes that affect available tools:

### Production Mode (Default)
```yaml
# config.yaml
server:
  internal_tools: false
```
**Available tools**: Core workflow and cluster management (recommended for daily use)

### Development Mode  
```yaml
# config.yaml
server:
  internal_tools: true
```
**Available tools**: All tools including project analysis and individual Docker/Helm operations (for debugging and learning)

## Basic Functionality Test (All Modes)

```
I want to test the BoatMCP server. Can you help me:

1. Create a minikube cluster called "test-cluster" with 2 CPUs and 2GB of memory
2. Check the cluster status
3. Delete the test cluster when we're done

Let's go through this step by step.
```

## Complete Deployment Workflow Test (All Modes)

The recommended approach using the integrated workflow:

```
I have a project that I want to deploy using BoatMCP. Please use the complete minikube deployment workflow to:

1. Analyze my project and generate an appropriate Dockerfile
2. Build a Docker image from my project  
3. Create/use a minikube cluster for testing
4. Load the built image into the cluster
5. Generate Helm charts for my application
6. Deploy the application using Helm

Use the minikube deployment workflow with these settings:
- Project path: /path/to/my/project
- App name: my-awesome-app
- Port: 8080
```

## One-Stop Deployment Workflow

The fastest way to get from project to production:

```
I want to deploy my application to minikube using the complete deployment workflow. Please take my project from code to running application in minikube.

My project is located at: /path/to/my/project
App name: my-awesome-app
```

### Advanced Workflow Options

For more control over the deployment process:

```
Use the minikube deployment workflow with these settings:
- Project path: /path/to/my/project  
- App name: production-app
- Namespace: production
- Image tag: v1.2.3
- Port: 8080
- Optimize for size: true
- Use multi-stage builds: true
- Custom instructions: ["Add health check endpoint", "Enable SSL"]
```

## Expected MCP Tools Usage

### Available in All Modes

#### Core Workflow
- **minikube_deployment_workflow** - Complete end-to-end deployment from project to running application

#### Cluster Management
- **manage_minikube_cluster** - Create, start, stop, and delete minikube clusters

### Available in Development Mode Only

When `internal_tools: true` in your config.yaml:

#### Docker Operations
- **generate_dockerfile** - Generate and save Dockerfiles for projects
- **build_docker_image** - Build container images from projects
- **analyze_project** - Get detailed project analysis data
- **preview_dockerfile** - Preview generated Dockerfile content without saving

#### Kubernetes Operations
- **generate_helm_chart** - Create Helm charts from project analysis
- **deploy_helm_chart** - Deploy applications to Kubernetes using Helm
- **preview_helm_chart** - Preview generated Helm chart content without saving

#### Image Management
- **load_image_to_minikube** - Load Docker images into minikube clusters

## Development Mode Testing

If you want to test individual tools step-by-step, enable development mode:

### Step-by-Step Workflow Test (Development Mode)

```
I want to test each deployment step individually. Please help me:

1. First, analyze my project structure and show me what technology stack is detected
2. Generate a Dockerfile for my project (but don't build yet)
3. Build a Docker image from the generated Dockerfile
4. Create a minikube cluster for testing
5. Load the built image into the cluster
6. Generate Helm charts for my application
7. Deploy the application using Helm

Walk me through each step so I can understand the process.
```

### Template Inspection and Verification (Development Mode)

```
Before generating any files, inspect what BoatMCP will create:

1. First, analyze the project structure:
   "Analyze my project and show me what type of Dockerfile template will be selected"

2. Preview the Dockerfile that would be generated:
   "Show me a preview of the Dockerfile that would be generated for my Python project with size optimization enabled"

3. Preview the Helm chart content:
   "Show me what Helm chart files will be created and preview their content for my application called 'my-app'"

4. If everything looks good, generate the actual files:
   "Generate and save the Dockerfile, then create the Helm chart"
```

## Verification Steps

### Test Minikube Cluster Creation
```bash
# Check cluster status
minikube status -p test-cluster

# Verify cluster resources
minikube profile list

# Check if image was loaded (if using development mode)
minikube image ls -p test-cluster
```

### Test Docker Image Building (Development Mode)
```bash
# Check if image was created
docker images | grep <your-app-name>

# Verify image can run
docker run --rm <your-app-name>:latest
```

### Test Helm Deployment
```bash
# Check if charts were generated
ls -la helm/

# Verify deployment status
helm list -A

# Check pods are running
kubectl get pods
```

## Troubleshooting

### MCP Server Issues
If your MCP client cannot access BoatMCP tools:

1. **Verify server runs**: `uv run boatmcp`
2. **Check configuration**: Ensure your MCP client config points to correct paths
3. **Restart your MCP client** after configuration changes
4. **Check config.yaml**: Ensure it exists and has valid YAML syntax
5. **Check logs**: Look for error messages in terminal where MCP server runs

### Configuration Issues

**Wrong tools available:**
- Check `internal_tools` setting in `config.yaml`
- Restart BoatMCP after changing configuration
- Verify you're using the correct config file

**Config not loading:**
- Ensure `config.yaml` is in the directory where you run `uv run boatmcp`
- Check file permissions and YAML syntax
- Try specifying config explicitly: `uv run boatmcp config.yaml`

### Tool-Specific Issues

**Minikube problems:**
- Ensure Docker daemon is running
- Check if virtualization is enabled
- Try different driver: `minikube start --driver=virtualbox`

**Docker problems:**
- Verify Docker Desktop is running
- Check if sufficient disk space available
- Ensure project has valid structure for Dockerfile generation

**Helm problems:**  
- Verify kubectl can connect to cluster
- Check if namespace exists
- Ensure Helm is properly installed

## Advanced Test Scenarios

### Multi-Project Testing
```
I have multiple projects - a Python Flask app and a Node.js React app. Can you help me deploy both to the same minikube cluster using the deployment workflow?
```

### Error Recovery Testing
```
Create a minikube cluster with invalid parameters (like 100 CPUs) and see how BoatMCP handles the error. Then try again with valid parameters.
```

### Full CI/CD Simulation
```
Simulate a complete development workflow using the minikube deployment workflow: take my project from code to running application in minikube, verify it's working, then clean up when done.
```

### Configuration Mode Comparison
```
Test the difference between production and development modes:

1. First, run with default config (production mode) and show me what tools are available
2. Then switch to development mode (internal_tools: true) and show the additional tools
3. Use development mode to analyze my project step by step
4. Switch back to production mode and deploy using the workflow tool
```

## MCP Client Compatibility

This guide works with:
- **Claude Desktop** - Standalone AI assistant application
- **Cursor IDE** - AI-powered code editor with built-in MCP support
- Any other MCP-compatible client

The tools and workflows are identical across all MCP clients.