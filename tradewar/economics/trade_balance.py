"""Trade balance algorithms for the trade war simulation."""

import logging
import random
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np

from tradewar.economics.models import Country, TradeFlow, TariffPolicy

# Use TYPE_CHECKING for circular imports
if TYPE_CHECKING:
    from tradewar.simulation.state import SimulationState

logger = logging.getLogger(__name__)


def update_trade_balance(
    state: "SimulationState",
    country1: Country,
    country2: Country,
    year: Optional[int] = None,
    quarter: Optional[int] = None
) -> float:
    """
    Update trade balance between two countries based on current policies and state.
    
    Args:
        state: Current simulation state
        country1: First country
        country2: Second country
        year: Optional year override (default: state's current year)
        quarter: Optional quarter override (default: state's current quarter)
        
    Returns:
        Updated trade balance from country1's perspective
    """
    year = year if year is not None else state.year
    quarter = quarter if quarter is not None else state.quarter
    
    # Get active tariff policies between the countries
    c1_to_c2_policies = state.get_active_tariff_policies(country1, country2)
    c2_to_c1_policies = state.get_active_tariff_policies(country2, country1)
    
    # Get previous trade flows (from the last quarter)
    prev_flows = _get_previous_trade_flows(state, country1, country2, year, quarter)
    
    # Calculate new trade flows based on policies and previous flows
    c1_to_c2_flow = _calculate_updated_trade_flow(
        state, country1, country2, c2_to_c1_policies, prev_flows[0], year, quarter
    )
    
    c2_to_c1_flow = _calculate_updated_trade_flow(
        state, country2, country1, c1_to_c2_policies, prev_flows[1], year, quarter
    )
    
    # Add new flows to state
    state.trade_flows.append(c1_to_c2_flow)
    state.trade_flows.append(c2_to_c1_flow)
    
    # Calculate and return balance from country1's perspective
    balance = c1_to_c2_flow.total_value - c2_to_c1_flow.total_value
    return balance


def _get_previous_trade_flows(
    state: "SimulationState",
    country1: Country,
    country2: Country,
    year: int,
    quarter: int
) -> Tuple[TradeFlow, TradeFlow]:
    """
    Get the most recent trade flows between two countries.
    
    Args:
        state: Current simulation state
        country1: First country
        country2: Second country
        year: Current year
        quarter: Current quarter
        
    Returns:
        Tuple of (country1 to country2 flow, country2 to country1 flow)
    """
    # Calculate previous quarter
    prev_year, prev_quarter = (year, quarter - 1) if quarter > 0 else (year - 1, 3)
    if prev_year < 0:
        prev_year, prev_quarter = 0, 0  # First simulation period
    
    # Find most recent flows
    c1_to_c2_flows = [
        flow for flow in state.trade_flows
        if flow.exporter.name == country1.name and 
        flow.importer.name == country2.name and
        (flow.year < year or (flow.year == year and flow.quarter < quarter))
    ]
    
    c2_to_c1_flows = [
        flow for flow in state.trade_flows
        if flow.exporter.name == country2.name and 
        flow.importer.name == country1.name and
        (flow.year < year or (flow.year == year and flow.quarter < quarter))
    ]
    
    # Get most recent flow or create baseline if none exists
    if c1_to_c2_flows:
        c1_to_c2_flow = max(
            c1_to_c2_flows, 
            key=lambda flow: (flow.year, flow.quarter)
        )
    else:
        c1_to_c2_flow = _create_baseline_trade_flow(
            country1, country2, prev_year, prev_quarter
        )
    
    if c2_to_c1_flows:
        c2_to_c1_flow = max(
            c2_to_c1_flows,
            key=lambda flow: (flow.year, flow.quarter)
        )
    else:
        c2_to_c1_flow = _create_baseline_trade_flow(
            country2, country1, prev_year, prev_quarter
        )
    
    return c1_to_c2_flow, c2_to_c1_flow


def _create_baseline_trade_flow(
    exporter: Country,
    importer: Country,
    year: int,
    quarter: int
) -> TradeFlow:
    """
    Create a baseline trade flow when no previous data exists.
    
    Args:
        exporter: Exporting country
        importer: Importing country
        year: Year for the flow
        quarter: Quarter for the flow
        
    Returns:
        A baseline trade flow
    """
    # Use GDP to estimate trade volume
    # Larger economies trade more, but not proportionally to GDP
    trade_scale = (exporter.gdp * importer.gdp) ** 0.4 * 0.001
    
    # Define sector weights based on country characteristics
    sector_weights = _get_country_sector_weights(exporter)
    
    # Calculate volumes by sector using weights
    total_volume = trade_scale * (1.0 + random.uniform(-0.1, 0.1))
    sector_volumes = {}
    sector_values = {}
    
    for sector, weight in sector_weights.items():
        # Add randomness to sector distribution
        adjusted_weight = weight * (1.0 + random.uniform(-0.2, 0.2))
        volume = total_volume * adjusted_weight
        sector_volumes[sector] = volume
        
        # Value is based on volume with some price factor
        price_factor = 1.0 + random.uniform(-0.1, 0.1)
        sector_values[sector] = volume * price_factor
    
    return TradeFlow(
        exporter=exporter,
        importer=importer,
        year=year,
        quarter=quarter,
        sector_volumes=sector_volumes,
        sector_values=sector_values
    )


def _calculate_updated_trade_flow(
    state: "SimulationState",
    exporter: Country,
    importer: Country,
    tariff_policies: List[TariffPolicy],
    previous_flow: TradeFlow,
    year: int,
    quarter: int
) -> TradeFlow:
    """
    Calculate an updated trade flow based on policies and previous flow.
    
    Args:
        state: Current simulation state
        exporter: Exporting country
        importer: Importing country
        tariff_policies: Active tariff policies affecting this flow
        previous_flow: Previous trade flow to base calculations on
        year: Current year
        quarter: Current quarter
        
    Returns:
        Updated trade flow
    """
    # Start with previous flow volumes and values
    new_sector_volumes = previous_flow.sector_volumes.copy()
    new_sector_values = previous_flow.sector_values.copy()
    
    # Apply tariff effects
    for policy in tariff_policies:
        for sector, rate in policy.sector_rates.items():
            if sector in new_sector_volumes:
                # Calculate price elasticity effect
                elasticity = _get_sector_price_elasticity(sector)
                
                # Volume reduction due to tariff (price effect)
                volume_change = new_sector_volumes[sector] * elasticity * rate
                new_sector_volumes[sector] += volume_change
                
                # Ensure volume doesn't go negative
                new_sector_volumes[sector] = max(0, new_sector_volumes[sector])
                
                # Value includes both volume change and price effect
                # Some of the tariff is absorbed by the exporter
                exporter_price_absorption = rate * 0.3
                new_price = (1 + rate - exporter_price_absorption)
                new_sector_values[sector] = new_sector_volumes[sector] * new_price
    
    # Apply base growth rate
    growth_rate = _calculate_base_growth_rate(exporter, importer, state)
    
    for sector in new_sector_volumes:
        new_sector_volumes[sector] *= (1 + growth_rate)
        new_sector_values[sector] *= (1 + growth_rate)
    
    return TradeFlow(
        exporter=exporter,
        importer=importer,
        year=year,
        quarter=quarter,
        sector_volumes=new_sector_volumes,
        sector_values=new_sector_values
    )


def _get_country_sector_weights(country: Country) -> Dict[str, float]:
    """
    Get the export sector weights for a country.
    
    Args:
        country: The country
        
    Returns:
        Dictionary of sector weights (summing to 1.0)
    """
    # These would ideally be data-driven from country profiles
    if country.name == "US":
        return {
            "technology": 0.25,
            "services": 0.20,
            "manufacturing": 0.15,
            "agriculture": 0.10,
            "healthcare": 0.10,
            "education": 0.05,
            "raw_materials": 0.05,
            "natural_resources": 0.05,
            "tourism": 0.05,
        }
    elif country.name == "China":
        return {
            "manufacturing": 0.35,
            "technology": 0.20,
            "raw_materials": 0.10,
            "rare_earth_minerals": 0.05,
            "agriculture": 0.08,
            "services": 0.07,
            "healthcare": 0.05,
            "natural_resources": 0.05,
            "tourism": 0.05,
        }
    elif country.name == "Indonesia":
        return {
            "natural_resources": 0.25,
            "agriculture": 0.20,
            "manufacturing": 0.20,
            "tourism": 0.15,
            "raw_materials": 0.10,
            "services": 0.05,
            "technology": 0.05,
        }
    else:
        # Generic distribution for other countries
        return {
            "manufacturing": 0.25,
            "services": 0.20,
            "agriculture": 0.15,
            "natural_resources": 0.15,
            "technology": 0.10,
            "tourism": 0.10,
            "healthcare": 0.05,
        }


def _get_sector_price_elasticity(sector: str) -> float:
    """
    Get the price elasticity of demand for a sector.
    
    Args:
        sector: The economic sector
        
    Returns:
        Price elasticity (negative value)
    """
    # Default elasticities by sector
    elasticities = {
        "agriculture": -0.8,
        "manufacturing": -1.5,
        "technology": -2.0,
        "raw_materials": -0.6,
        "services": -1.8,
        "healthcare": -1.2,
        "education": -1.0,
        "tourism": -2.5,
        "natural_resources": -0.7,
        "rare_earth_minerals": -0.5,
    }
    
    return elasticities.get(sector, -1.2)  # Default elasticity if sector not listed


def _calculate_base_growth_rate(
    exporter: Country, 
    importer: Country, 
    state: "SimulationState"
) -> float:
    """
    Calculate the base growth rate for trade between two countries.
    
    Args:
        exporter: Exporting country
        importer: Importing country
        state: Current simulation state
        
    Returns:
        Base quarterly growth rate for trade
    """
    # Growth depends on both economies' performance
    # Get the most recent economic indicators
    exporter_indicators = state.economic_indicators.get(exporter.name, [])
    importer_indicators = state.economic_indicators.get(importer.name, [])
    
    exporter_growth = 0.01  # Default 1% quarterly growth
    importer_growth = 0.01  # Default 1% quarterly growth
    
    if exporter_indicators:
        exporter_growth = exporter_indicators[-1].gdp_growth / 4  # Convert annual to quarterly
    
    if importer_indicators:
        importer_growth = importer_indicators[-1].gdp_growth / 4  # Convert annual to quarterly
    
    # Growth is a weighted average of exporter's production capacity and importer's demand
    # Plus a small random component
    base_growth = (0.6 * exporter_growth + 0.4 * importer_growth) + random.uniform(-0.005, 0.005)
    
    return max(-0.05, min(0.07, base_growth))  # Bound between -5% and 7% quarterly
