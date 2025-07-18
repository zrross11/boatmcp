"""Legacy entry point - redirects to new structure."""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from boatmcp.main import mcp

if __name__ == "__main__":
    mcp.run(transport='stdio')