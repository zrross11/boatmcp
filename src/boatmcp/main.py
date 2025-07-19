"""Main entry point for BoatMCP server."""

import sys
from pathlib import Path

from .core import load_config, run_server


def main() -> None:
    """Main entry point for the BoatMCP server."""
    # Check for custom config path from command line
    config_path = None
    if len(sys.argv) > 1 and sys.argv[1].endswith('.yaml'):
        config_path = Path(sys.argv[1])

    # Load configuration from config.yaml (or fallback to environment variables)
    config = load_config(config_path)

    # Start the server with the loaded configuration
    run_server(config)


if __name__ == "__main__":
    main()
