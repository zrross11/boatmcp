# Claude Desktop Test Prompt

Once you have BoatMCP set up and running, use this prompt in Claude Desktop to test the MCP server functionality:

## Test Prompt

```
I want to test the BoatMCP server. Can you help me create a minikube cluster called "test-cluster" with 2 CPUs and 2GB of memory?

After that, can you show me what clusters are available and then delete the test cluster when we're done?
```

## Dockerfile Generation Test

```
I have a Go web application in the examples/go_web_app directory that I'd like to containerize. Can you help me create a Dockerfile for it?

The application structure is:
- main.go is the entry point
- It's a simple Go web server
- I want to follow Docker best practices for Go applications
- Should be optimized for production deployment

Please create a Dockerfile that builds and runs this Go web application properly.
```

## Expected Behavior

Claude Desktop should be able to:

1. **Create a minikube cluster** using the `create_minikube_cluster` tool
2. **List available clusters** (if that functionality is implemented)
3. **Delete the cluster** using the `delete_minikube_cluster` tool

## Verification Steps

1. Check that minikube cluster is created: `minikube status -p test-cluster`
2. Verify the cluster has the correct resources: `minikube profile list`
3. Confirm the cluster is deleted after the test: `minikube profile list`

## Troubleshooting

If Claude Desktop cannot access the BoatMCP tools:

1. Verify the MCP server is running: `uv run main.py`
2. Check the Claude Desktop configuration in `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Restart Claude Desktop after configuration changes
4. Check for any error messages in the MCP server logs

## Additional Test Scenarios

Once basic functionality is working, try these advanced scenarios:

- **Multi-cluster management**: Create multiple clusters with different profiles
- **Resource allocation**: Test different CPU and memory configurations
- **Error handling**: Try to create a cluster with invalid parameters
- **Deployment workflows**: Test the complete "local development to production" flow
- **Dockerfile generation**: Test creating a Dockerfile for containerizing the application