"""Command-line interface for Malvolio."""

import argparse
import sys

from livereload import Server

from .builder import SiteBuilder
from .config import Config


def cmd_build(args: argparse.Namespace) -> None:
    """Build the site once.
    
    Args:
        args: Parsed command-line arguments.
    """
    config = Config()
    builder = SiteBuilder(config)
    
    if args.clean:
        builder.rebuild()
    else:
        builder.build()


def cmd_serve(args: argparse.Namespace) -> None:
    """Start development server with live reload.
    
    Args:
        args: Parsed command-line arguments.
    """
    config = Config()
    builder = SiteBuilder(config)
    
    # Initial build
    builder.build()
    
    # Set up livereload server
    server = Server()
    
    # Watch templates and content directories
    for watch_path in config.watch_paths:
        server.watch(str(watch_path), builder.build)
        print(f"Watching: {watch_path}")
    
    print(f"\nStarting server at http://0.0.0.0:{args.port}")
    print("Press Ctrl+C to stop.\n")
    
    server.serve(root=str(config.public_dir), port=args.port, host="0.0.0.0")


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="malvolio",
        description="A minimal static site generator for personal webpages.",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser(
        "build",
        help="Build the site once",
    )
    build_parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output files before building",
    )
    build_parser.set_defaults(func=cmd_build)
    
    # Serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start development server with live reload",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
    )
    serve_parser.set_defaults(func=cmd_serve)
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
