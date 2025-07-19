"""Core MCP server setup and configuration."""

from typing import Any

from fastmcp import FastMCP

from ..docker import register_docker_tools
from ..kubernetes import register_kubernetes_tools
from ..workflows import register_workflow_tools
from .config import BoatMCPConfig


def create_mcp_server(config: BoatMCPConfig) -> FastMCP[Any]:
    """Create and configure the MCP server with all tools registered.

    Args:
        config: BoatMCP configuration instance

    Returns:
        Configured FastMCP server instance
    """
    # Initialize FastMCP server
    mcp: FastMCP[Any] = FastMCP("boatmcp")

    # Register domain tools based on configuration
    if config.docker_enabled:
        register_docker_tools(mcp, config)
    if config.kubernetes_enabled:
        register_kubernetes_tools(mcp, config)
    if config.workflows_enabled:
        register_workflow_tools(mcp, config)

    return mcp


def run_server(config: BoatMCPConfig) -> None:
    """Run the MCP server with stdio transport.

    Args:
        config: BoatMCP configuration instance
    """
    server = create_mcp_server(config)
    # Force stdio transport for now (config.transport is for future extensibility)
    server.run(transport="stdio")
