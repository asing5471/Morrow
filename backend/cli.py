"""Command-line interface for Morrow."""

import argparse

import uvicorn

from backend.config import settings


def start() -> None:
    """Start the Morrow local server."""
    uvicorn.run(
        "backend.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=False,
    )


def main() -> None:
    """Run the Morrow command-line interface."""
    parser = argparse.ArgumentParser(
        prog="morrow",
        description="Private, local-first browser infrastructure.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "start",
        help="Start the local Morrow server.",
    )

    args = parser.parse_args()

    if args.command == "start":
        start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
