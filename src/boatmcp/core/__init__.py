"""Core MCP infrastructure."""

from .config import BoatMCPConfig, load_config
from .server import create_mcp_server, run_server
from .types import JSONDict, ToolResult

__all__ = [
    "BoatMCPConfig",
    "load_config",
    "create_mcp_server",
    "run_server",
    "JSONDict",
    "ToolResult",
]
