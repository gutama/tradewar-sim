#!/usr/bin/env python3
# filepath: /home/ginanjar/repositories/tradewar-sim/scripts/run_api.py
"""Command-line script to run the Trade War Simulation API server."""

import argparse
import logging
import sys
from pathlib import Path

import uvicorn

# Add parent directory to Python path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tradewar.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tradewar-api")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the Trade War Simulation API server")
    
    parser.add_argument(
        "--host",
        type=str,
        default=config.api.host,
        help="Host to bind the server to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=config.api.port,
        help="Port to bind the server to"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reloading on code changes (development mode)"
    )
    
    return parser.parse_args()


def main():
    """Run the API server."""
    args = parse_args()
    
    logger.info(f"Starting API server at {args.host}:{args.port}")
    
    uvicorn.run(
        "tradewar.api.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()