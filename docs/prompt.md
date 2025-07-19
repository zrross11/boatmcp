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

## One-Stop Deployment Workflow (NEW!)

The fastest way to get from project to production is using the new **minikube_deployment_workflow** tool:

```
I want to deploy my application to minikube using the fastest possible workflow. Please use the one-stop deployment workflow to take my project from code to running application in minikube.

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

Claude Desktop should be able to use these BoatMCP tools:

### Minikube Management
- **create_minikube_cluster** - Set up local Kubernetes clusters
- **delete_minikube_cluster** - Clean up test clusters  
- **load_image_into_minikube** - Load Docker images into clusters

### Docker Operations
- **build_docker_image** - Build container images from projects
- **generate_dockerfile** - Generate and save Dockerfiles for projects
- **analyze_project_for_dockerfile** - Get project analysis data for Dockerfile generation
- **get_dockerfile_template_info** - Inspect Dockerfile template selection and parameters
- **preview_dockerfile** - Preview generated Dockerfile content without saving
- **get_dockerfile_templates** - View available Dockerfile templates and generation logic

### Helm Operations  
- **create_helm_chart** - Create Helm charts from project analysis
- **install_helm_chart** - Deploy applications to Kubernetes
- **remove_helm_chart** - Remove deployed applications
- **get_helm_template_info** - Inspect Helm chart template parameters and structure
- **preview_helm_chart** - Preview generated Helm chart content without saving
- **get_helm_templates** - View available Helm templates and raw template sources

### Workflow Orchestration (NEW!)
- **minikube_deployment_workflow** - Complete end-to-end deployment from project to running application
- **get_workflow_progress** - Monitor progress of the deployment workflow

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

### Workflow Testing
```
Test the new one-stop deployment workflow with a Python Flask application. Monitor the progress as it goes through each step: Dockerfile generation, image building, minikube loading, Helm chart creation, and deployment.
```

### Workflow Error Handling
```
Test what happens when the workflow encounters errors at different stages. For example, try deploying a project without a requirements.txt file, or with invalid Dockerfile configurations.
```

### Template Inspection and Verification (NEW!)
```
Before generating any files, inspect what BoatMCP will create:

1. First, analyze the project structure:
   "Analyze my project and show me what type of Dockerfile template will be selected"

2. Preview the Dockerfile that would be generated:
   "Show me a preview of the Dockerfile that would be generated for my Python project with size optimization enabled"

3. Inspect the Helm chart templates:
   "Show me what Helm chart files will be created and preview their content for my application called 'my-app'"

4. View the raw template sources:
   "Show me the actual template files used for Dockerfile generation so I can understand how they work"
```

### Template Verification Workflow
```
Use the inspection tools to verify templates before generation:

1. "Get template info for my Dockerfile with these settings: port 8080, optimize for size, multi-stage build"
2. "Preview the Dockerfile with those settings" 
3. "If it looks good, generate and save the Dockerfile"
4. "Get Helm template info for chart name 'my-app'"
5. "Preview the Helm chart content"
6. "If correct, create the Helm chart"
```