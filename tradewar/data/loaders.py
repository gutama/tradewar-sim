"""Data loading utilities for the trade war simulation."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Base paths
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_DIR = os.path.join(MODULE_DIR, "baseline")


def load_country_data(country_name: str) -> Dict:
    """
    Load economic baseline data for a country.
    
    Args:
        country_name: Name of the country to load data for
        
    Returns:
        Dictionary with country economic data
        
    Raises:
        FileNotFoundError: If the country data file doesn't exist
        ValueError: If the data is invalid
    """
    file_path = os.path.join(BASELINE_DIR, f"{country_name.lower()}_economy.json")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        logger.info(f"Loaded data for {country_name} from {file_path}")
        
        # Validate required fields
        required_fields = ["name", "gdp", "population"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in {file_path}")
        
        # Set defaults for optional fields
        data.setdefault("inflation_rate", 0.02)
        data.setdefault("unemployment_rate", 0.05)
        data.setdefault("interest_rate", 0.02)
        data.setdefault("currency_value", 1.0)
        data.setdefault("sectors", {})
        
        return data
    
    except FileNotFoundError:
        logger.warning(f"Country data file not found: {file_path}")
        
        # Generate fake data for countries without data files
        # This is useful for testing and development
        logger.info(f"Generating synthetic data for {country_name}")
        return _generate_synthetic_country_data(country_name)
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
        raise ValueError(f"Invalid JSON in country data file: {file_path}")


def load_historical_trade_data(
    country1: str, country2: str, start_year: Optional[int] = None
) -> pd.DataFrame:
    """
    Load historical trade data between two countries.
    
    Args:
        country1: First country name
        country2: Second country name
        start_year: Optional start year to filter data
        
    Returns:
        DataFrame with historical trade data
    """
    # Create filename - try both country order possibilities
    filename1 = f"{country1.lower()}_{country2.lower()}_trade.csv"
    filename2 = f"{country2.lower()}_{country1.lower()}_trade.csv"
    
    file_path1 = os.path.join(MODULE_DIR, "historical", filename1)
    file_path2 = os.path.join(MODULE_DIR, "historical", filename2)
    
    # Try to load the file
    if os.path.exists(file_path1):
        file_path = file_path1
    elif os.path.exists(file_path2):
        file_path = file_path2
    else:
        logger.warning(f"No historical trade data found for {country1}-{country2}")
        # Return empty DataFrame with expected structure
        return pd.DataFrame(columns=["year", "quarter", "exporter", "importer", "value", "sector"])
    
    try:
        df = pd.read_csv(file_path)
        
        # Filter by year if requested
        if start_year is not None:
            df = df[df["year"] >= start_year]
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading trade data from {file_path}: {str(e)}")
        return pd.DataFrame(columns=["year", "quarter", "exporter", "importer", "value", "sector"])


def save_simulation_result(result: Dict, output_dir: str, simulation_id: str) -> None:
    """
    Save a simulation result to disk.
    
    Args:
        result: Dictionary with simulation results
        output_dir: Directory to save results in
        simulation_id: Unique identifier for this simulation run
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as JSON
    output_path = os.path.join(output_dir, f"simulation_{simulation_id}.json")
    
    try:
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Saved simulation result to {output_path}")
    
    except Exception as e:
        logger.error(f"Error saving simulation result to {output_path}: {str(e)}")


def _generate_synthetic_country_data(country_name: str) -> Dict:
    """Generate synthetic data for testing when real data is unavailable."""
    # Scale GDP and population based on country
    gdp_scale = {
        "US": 28.8,
        "China": 17.8,
        "Indonesia": 1.42,
    }.get(country_name, 1.0)
    
    pop_scale = {
        "US": 330,
        "China": 1400,
        "Indonesia": 270,
    }.get(country_name, 100)
    
    # Create sector profile based on country
    if country_name == "US":
        sectors = {
            "technology": 0.25,
            "services": 0.40,
            "manufacturing": 0.15,
            "agriculture": 0.02,
            "healthcare": 0.10,
            "natural_resources": 0.05,
            "education": 0.03,
        }
    elif country_name == "China":
        sectors = {
            "manufacturing": 0.35,
            "technology": 0.15,
            "services": 0.25,
            "agriculture": 0.08,
            "natural_resources": 0.10,
            "rare_earth_minerals": 0.05,
            "education": 0.02,
        }
    elif country_name == "Indonesia":
        sectors = {
            "agriculture": 0.15,
            "natural_resources": 0.25,
            "manufacturing": 0.20,
            "services": 0.30,
            "tourism": 0.08,
            "technology": 0.02,
        }
    else:
        # Generic sector profile
        sectors = {
            "services": 0.35,
            "manufacturing": 0.25,
            "agriculture": 0.10,
            "natural_resources": 0.10,
            "technology": 0.10,
            "education": 0.05,
            "healthcare": 0.05,
        }
    
    # Build synthetic data
    return {
        "name": country_name,
        "gdp": gdp_scale,
        "population": pop_scale * 1000000,  # Convert to millions
        "inflation_rate": 0.02 + np.random.rand() * 0.02,  # 2-4%
        "unemployment_rate": 0.03 + np.random.rand() * 0.04,  # 3-7%
        "interest_rate": 0.01 + np.random.rand() * 0.03,  # 1-4%
        "currency_value": 1.0,
        "sectors": sectors
    }
