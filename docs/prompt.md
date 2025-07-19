# BoatMCP Test Guide

Once you have BoatMCP set up and running, use these prompts in Claude Desktop to test the MCP server functionality.

## Basic Functionality Test

```
I want to test the BoatMCP server. Can you help me:

1. Create a minikube cluster called "test-cluster" with 2 CPUs and 2GB of memory
2. Build a Docker image for the example Go application
3. Load that Docker image into the minikube cluster
4. Delete the test cluster when we're done

Let's go through this step by step.
```

## Complete Deployment Workflow Test

```
I have a project that I want to deploy using BoatMCP. Can you help me:

1. Analyze my project structure and generate an appropriate Dockerfile
2. Build a Docker image from my project  
3. Create a minikube cluster for testing
4. Load the built image into the cluster
5. Generate Helm charts for my application
6. Deploy the application using Helm

Walk me through this entire workflow.
```

## Expected MCP Tools Usage

Claude Desktop should be able to use these BoatMCP tools:

### Minikube Management
- **create_minikube_cluster** - Set up local Kubernetes clusters
- **delete_minikube_cluster** - Clean up test clusters  
- **load_image_into_minikube** - Load Docker images into clusters

### Docker Operations
- **build_docker_image** - Build container images from projects

### Helm Operations  
- **generate_helm_chart** - Create Helm charts from project analysis
- **deploy_helm_chart** - Deploy applications to Kubernetes
- **uninstall_helm_chart** - Remove deployed applications

## Verification Steps

### Test Minikube Cluster Creation
```bash
# Check cluster status
minikube status -p test-cluster

# Verify cluster resources
minikube profile list

# Check if image was loaded
minikube image ls -p test-cluster
```

### Test Docker Image Building
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
If Claude Desktop cannot access BoatMCP tools:

1. **Verify server runs**: `uv run boatmcp`
2. **Check configuration**: Ensure Claude Desktop config points to correct paths
3. **Restart Claude Desktop** after configuration changes
4. **Check logs**: Look for error messages in terminal where MCP server runs

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

Once basic functionality works, try these scenarios:

### Multi-Project Testing
```
I have multiple projects - a Python Flask app and a Node.js React app. Can you help me containerize both and deploy them to the same minikube cluster?
```

### Error Recovery Testing
```
Create a minikube cluster with invalid parameters (like 100 CPUs) and see how BoatMCP handles the error. Then try again with valid parameters.
```

### Full CI/CD Simulation
```
Simulate a complete development workflow: analyze my project, build it, test it locally in minikube, generate production-ready Helm charts, and clean up when done.
```