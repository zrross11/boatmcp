"""BoatMCP - MCP server for shipping code from local to production."""

__version__ = "0.2.0"

from .core import create_mcp_server, run_server
from .main import main as run

__all__ = [
    "create_mcp_server",
    "run_server",
    "run",
]
