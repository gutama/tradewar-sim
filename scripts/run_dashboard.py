#!/usr/bin/env python3
# filepath: /home/ginanjar/repositories/tradewar-sim/scripts/run_dashboard.py
"""Command-line script to run the Trade War Simulation Dashboard."""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to Python path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tradewar.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tradewar-dashboard")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the Trade War Simulation Dashboard")
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DASHBOARD_PORT", "8501")),
        help="Port to run the dashboard on"
    )
    
    parser.add_argument(
        "--api-host",
        type=str,
        default=os.getenv("API_HOST", "localhost"),
        help="Host where the API server is running"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=config.api.port,
        help="Port where the API server is running"
    )
    
    return parser.parse_args()


def main():
    """Run the Streamlit dashboard."""
    args = parse_args()
    
    # Set environment variables for the dashboard to connect to the API
    os.environ["API_HOST"] = args.api_host
    os.environ["API_PORT"] = str(args.api_port)
    
    logger.info(f"Starting dashboard on port {args.port}, connecting to API at {args.api_host}:{args.api_port}")
    
    # Run streamlit using subprocess
    dashboard_path = Path(__file__).parent.parent / "tradewar" / "visualization" / "dashboard.py"
    cmd = [
        "streamlit", 
        "run", 
        str(dashboard_path),
        "--server.port", str(args.port),
        "--server.address", "0.0.0.0"
    ]
    
    subprocess.run(cmd)


if __name__ == "__main__":
    main()