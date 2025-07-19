"""Core MCP server setup and configuration."""

from typing import Any

from fastmcp import FastMCP

from ..docker import register_docker_tools
from ..kubernetes import register_kubernetes_tools
from ..workflows import register_workflow_tools


def create_mcp_server() -> FastMCP[Any]:
    """Create and configure the MCP server with all tools registered.

    Returns:
        Configured FastMCP server instance
    """
    # Initialize FastMCP server
    mcp: FastMCP[Any] = FastMCP("boatmcp")

    # Register all domain tools
    register_docker_tools(mcp)
    register_kubernetes_tools(mcp)
    register_workflow_tools(mcp)

    return mcp


def run_server() -> None:
    """Run the MCP server with stdio transport."""
    server = create_mcp_server()
    server.run(transport="stdio")
