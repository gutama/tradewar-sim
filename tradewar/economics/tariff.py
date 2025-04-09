"""Tariff impact calculations for the trade war simulation."""

import logging
from typing import Dict, Optional, TYPE_CHECKING

import numpy as np

from tradewar.economics.models import Country, TariffPolicy

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from tradewar.simulation.state import SimulationState, TariffImpact

logger = logging.getLogger(__name__)


def calculate_tariff_impact(
    state: "SimulationState",
    policy: TariffPolicy, 
    imposing_country: Country,
    targeted_country: Country,
    elasticity_multiplier: float = 1.0
) -> "TariffImpact":
    """
    Calculate the economic impact of a tariff policy.
    
    Args:
        state: Current simulation state
        policy: The tariff policy to analyze
        imposing_country: Country imposing the tariffs
        targeted_country: Country targeted by the tariffs
        elasticity_multiplier: Factor to adjust price elasticity
        
    Returns:
        Object containing calculated impacts on both economies
    """
    # Import here to avoid circular import
    from tradewar.simulation.state import TariffImpact
    
    logger.info(
        f"Calculating impact of {imposing_country.name}'s tariffs on {targeted_country.name}"
    )
    
    # Get previous trade flows between the countries
    trade_flows = [
        flow for flow in state.trade_flows
        if flow.exporter.name == targeted_country.name and 
        flow.importer.name == imposing_country.name
    ]
    
    # If no previous trade data, use estimates
    if not trade_flows:
        logger.warning(f"No trade flow data for {targeted_country.name} to {imposing_country.name}")
        # Create estimated trade flow data based on GDP sizes
        estimated_trade_volume = (
            targeted_country.gdp * imposing_country.gdp
        ) ** 0.5 * 0.001  # Arbitrary scaling factor
        
        trade_volume_change = {}
        price_effects = {}
        
        for sector, rate in policy.sector_rates.items():
            # Assume equal distribution across sectors if no data
            base_volume = estimated_trade_volume / len(policy.sector_rates)
            # Higher tariffs lead to greater volume reduction
            trade_volume_change[sector] = -base_volume * rate * 2.0
            # Price effects are proportional to tariff rates
            price_effects[sector] = rate * 0.7  # Partial pass-through to prices
    else:
        # Use most recent trade flow
        latest_flow = max(trade_flows, key=lambda flow: (flow.year, flow.quarter))
        
        trade_volume_change = {}
        price_effects = {}
        
        # Calculate impacts by sector
        for sector, rate in policy.sector_rates.items():
            # Get sector volume from trade flow, or estimate if missing
            sector_volume = latest_flow.sector_volumes.get(
                sector, latest_flow.total_value / len(policy.sector_rates)
            )
            
            # Calculate price elasticity (simplified model)
            # In reality, this would depend on sector, substitutability, etc.
            price_elasticity = -2.0 * elasticity_multiplier  # Default elasticity
            
            # Higher tariffs lead to higher prices and lower demand
            price_increase = rate * 0.7  # Assuming 70% pass-through to prices
            price_effects[sector] = price_increase
            
            # Volume change based on price elasticity
            volume_change = sector_volume * price_elasticity * price_increase
            trade_volume_change[sector] = volume_change
    
    # Calculate GDP impacts
    # Exporter (targeted country) loses exports
    total_export_loss = sum(trade_volume_change.values())
    exporter_gdp_impact = total_export_loss * 0.8  # Not 1:1 due to substitution effects
    
    # Importer (imposing country) faces deadweight loss but gains tariff revenue
    tariff_revenue = sum(
        -vol * policy.sector_rates[sector]
        for sector, vol in trade_volume_change.items()
    )
    consumer_surplus_loss = tariff_revenue * 0.3  # Simplified consumer welfare loss
    importer_gdp_impact = tariff_revenue - consumer_surplus_loss
    
    return TariffImpact(
        policy=policy,
        exporter_gdp_impact=exporter_gdp_impact,
        importer_gdp_impact=importer_gdp_impact,
        trade_volume_change=trade_volume_change,
        price_effects=price_effects
    )


def calculate_optimal_tariff(
    state: "SimulationState",
    imposing_country: Country,
    targeted_country: Country,
    objective: str = "welfare"
) -> Dict[str, float]:
    """
    Calculate the optimal tariff rates for different sectors.
    
    Args:
        state: Current simulation state
        imposing_country: Country imposing the tariffs
        targeted_country: Country targeted by the tariffs
        objective: Optimization objective (welfare, revenue, politics)
        
    Returns:
        Dictionary of optimal tariff rates by sector
    """
    # Get trade elasticities from historical data or use defaults
    trade_elasticities = _estimate_trade_elasticities(
        state, imposing_country, targeted_country
    )
    
    optimal_rates = {}
    
    # Simple optimal tariff formula (based on welfare maximization)
    # t* = 1/e where e is the export supply elasticity
    for sector, elasticity in trade_elasticities.items():
        if objective == "welfare":
            # Classic optimal tariff
            optimal_rates[sector] = min(1.0 / abs(elasticity), 0.5)  # Cap at 50%
        
        elif objective == "revenue":
            # Revenue maximizing tariff
            optimal_rates[sector] = min(1.0 / (1.0 + abs(elasticity)), 0.7)  # Cap at 70%
        
        elif objective == "politics":
            # Political economy considerations (protect sensitive sectors)
            sensitivity = _get_sector_political_sensitivity(imposing_country, sector)
            optimal_rates[sector] = min(
                (1.0 / abs(elasticity)) * (1.0 + sensitivity), 0.8
            )  # Cap at 80%
    
    return optimal_rates


def _estimate_trade_elasticities(
    state: "SimulationState", 
    country1: Country, 
    country2: Country
) -> Dict[str, float]:
    """
    Estimate trade elasticities between two countries from historical data.
    
    Args:
        state: Current simulation state
        country1: First country
        country2: Second country
        
    Returns:
        Dictionary of elasticity estimates by sector
    """
    # This would normally analyze historical price and volume changes
    # For simplicity, return default values by sector
    return {
        "agriculture": -1.5,
        "manufacturing": -2.0,
        "technology": -2.5,
        "raw_materials": -1.0,
        "services": -3.0,
        "healthcare": -2.2,
        "education": -2.5,
        "tourism": -3.5,
        "natural_resources": -0.8,
        "rare_earth_minerals": -0.5,
    }


def _get_sector_political_sensitivity(country: Country, sector: str) -> float:
    """
    Get the political sensitivity of a sector for a country.
    
    Args:
        country: The country
        sector: The economic sector
        
    Returns:
        Political sensitivity score (0-1)
    """
    # This would be based on employment, voter preferences, etc.
    # For simplicity, use hardcoded values
    us_sensitivities = {
        "manufacturing": 0.8,
        "agriculture": 0.7,
        "technology": 0.5,
    }
    
    china_sensitivities = {
        "technology": 0.9,
        "manufacturing": 0.7,
        "rare_earth_minerals": 0.6,
    }
    
    indonesia_sensitivities = {
        "agriculture": 0.9,
        "natural_resources": 0.8,
        "manufacturing": 0.7,
        "tourism": 0.6,
    }
    
    sensitivities = {
        "US": us_sensitivities,
        "China": china_sensitivities,
        "Indonesia": indonesia_sensitivities,
    }
    
    country_sectors = sensitivities.get(country.name, {})
    return country_sectors.get(sector, 0.3)  # Default 0.3 for unlisted sectors
