"""Main entry point for BoatMCP server."""

from .core import run_server


def main() -> None:
    """Main entry point for the BoatMCP server."""
    run_server()


if __name__ == "__main__":
    main()
