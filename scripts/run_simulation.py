#!/usr/bin/env python3
"""Command-line interface for running trade war simulations."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

# Add parent directory to Python path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tradewar.config import Config, config
from tradewar.data.loaders import load_country_data
from tradewar.economics.models import Country
from tradewar.simulation.engine import SimulationEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tradewar-sim")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run a trade war simulation")
    
    parser.add_argument(
        "--years", 
        type=int, 
        default=config.simulation.years,
        help="Number of years to simulate"
    )
    
    parser.add_argument(
        "--steps-per-year",
        type=int,
        default=config.simulation.steps_per_year,
        help="Simulation steps per year"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=config.simulation.random_seed,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=config.simulation.output_dir,
        help="Directory for simulation output"
    )
    
    parser.add_argument(
        "--countries",
        type=str,
        nargs="+",
        default=["US", "China", "Indonesia"],
        help="Countries to include in simulation"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def save_results(results: List[Dict], output_dir: str):
    """Save simulation results to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    # Save full results as CSV
    df.to_csv(os.path.join(output_dir, "simulation_results.csv"), index=False)
    
    # Save summary as JSON
    summary = {
        "total_years": len(df["year"].unique()),
        "countries": df["countries"].iloc[0],
        "final_state": json.loads(df.iloc[-1].to_json()),
    }
    
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Results saved to {output_dir}")


def main():
    """Main entry point for the simulation CLI."""
    args = parse_args()
    
    if args.verbose:
        logging.getLogger("tradewar-sim").setLevel(logging.DEBUG)
    
    logger.info("Starting trade war simulation")
    logger.info(f"Configuration: {args}")
    
    # Load country data
    countries = []
    for country_name in args.countries:
        try:
            country_data = load_country_data(country_name)
            countries.append(Country(**country_data))
            logger.info(f"Loaded data for {country_name}")
        except Exception as e:
            logger.error(f"Error loading data for {country_name}: {str(e)}")
            sys.exit(1)
    
    # Create and run simulation
    try:
        engine = SimulationEngine(countries=countries)
        history = engine.run_full_simulation()
        
        # Process results
        results = []
        for state in history:
            state_dict = {
                "year": state.year,
                "quarter": state.quarter,
                "countries": [country.name for country in state.countries],
            }
            
            # Add country-specific metrics
            for country in state.countries:
                state_dict[f"{country.name}_gdp"] = country.gdp
                state_dict[f"{country.name}_inflation"] = country.inflation_rate
                state_dict[f"{country.name}_unemployment"] = country.unemployment_rate
            
            # Add trade balances
            for country1 in state.countries:
                for country2 in state.countries:
                    if country1.name != country2.name:
                        balance = state.get_trade_balance(country1, country2)
                        state_dict[f"trade_balance_{country1.name}_{country2.name}"] = balance
            
            results.append(state_dict)
        
        # Save results
        save_results(results, args.output_dir)
        
        logger.info("Simulation completed successfully")
    
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
