"""Main entry point for BoatMCP server."""

from typing import Any

from fastmcp import FastMCP

from .tools import register_docker_tools, register_helm_tools, register_minikube_tools

# Initialize FastMCP server
mcp: FastMCP[Any] = FastMCP("boatmcp")

# Register all tools by category
register_docker_tools(mcp)
register_helm_tools(mcp)
register_minikube_tools(mcp)


def main() -> None:
    """Main entry point for the BoatMCP server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
