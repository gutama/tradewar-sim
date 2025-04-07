"""GDP impact calculations for the trade war simulation."""

import logging
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from tradewar.economics.models import Country, EconomicAction, EventConfig, TariffPolicy
from tradewar.simulation.state import SimulationState

logger = logging.getLogger(__name__)


def calculate_gdp_impact(
    state: SimulationState, 
    country: Country,
    year: int,
    quarter: int
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate GDP impact for a country based on trade war dynamics.
    
    Args:
        state: Current simulation state
        country: The country to calculate for
        year: Current year
        quarter: Current quarter
        
    Returns:
        Tuple of (overall GDP growth rate, factors contributing to growth)
    """
    # Baseline growth rate - country-specific
    baseline_growth = _get_baseline_quarterly_growth(country)
    
    # Calculate impacts from different factors
    tariff_impact = _calculate_tariff_gdp_impact(state, country)
    trade_impact = _calculate_trade_gdp_impact(state, country)
    investment_impact = _calculate_investment_gdp_impact(state, country)
    event_impact = _calculate_event_gdp_impact(state, country)
    global_impact = _calculate_global_economy_impact(state)
    
    # Sum up all impacts
    growth_rate = baseline_growth + tariff_impact + trade_impact + \
                  investment_impact + event_impact + global_impact
    
    # Add small random noise
    growth_rate += random.uniform(-0.0025, 0.0025)
    
    # Bound growth rate to realistic range
    growth_rate = max(-0.08, min(0.10, growth_rate))
    
    # Record contribution factors
    contribution_factors = {
        "baseline": baseline_growth,
        "tariffs": tariff_impact,
        "trade": trade_impact,
        "investment": investment_impact,
        "events": event_impact,
        "global": global_impact
    }
    
    logger.debug(f"GDP growth for {country.name}: {growth_rate:.2%}, factors: {contribution_factors}")
    
    return growth_rate, contribution_factors


def _get_baseline_quarterly_growth(country: Country) -> float:
    """
    Get the baseline quarterly GDP growth rate for a country.
    
    Args:
        country: The country
        
    Returns:
        Baseline quarterly growth rate
    """
    # Country-specific baseline annual growth rates
    annual_rates = {
        "US": 0.020,        # 2.0%
        "China": 0.050,     # 5.0%
        "Indonesia": 0.042  # 4.2%
    }
    
    # Convert annual rate to quarterly
    annual_rate = annual_rates.get(country.name, 0.025)  # Default 2.5% if country not found
    quarterly_rate = (1 + annual_rate) ** 0.25 - 1
    
    return quarterly_rate


def _calculate_tariff_gdp_impact(state: SimulationState, country: Country) -> float:
    """
    Calculate GDP impact from tariffs imposed on and by this country.
    
    Args:
        state: Current simulation state
        country: The country
        
    Returns:
        GDP growth impact from tariff policies
    """
    # Tariffs imposed BY this country on others
    outgoing_tariff_impact = 0.0
    
    # Collect all active tariff policies imposed by this country
    outgoing_policies = [
        policy for policy in state.active_tariff_policies
        if policy.source_country.name == country.name
    ]
    
    # Tariffs increase government revenue but reduce consumer welfare
    # Net effect is usually slightly negative or neutral for imposing country
    for policy in outgoing_policies:
        # Calculate weighted average tariff rate
        avg_rate = sum(policy.sector_rates.values()) / len(policy.sector_rates)
        # Small negative effect on GDP growth
        outgoing_tariff_impact -= avg_rate * 0.05
    
    # Tariffs imposed ON this country by others
    incoming_tariff_impact = 0.0
    
    # Collect all active tariff policies targeting this country
    incoming_policies = [
        policy for policy in state.active_tariff_policies
        if policy.target_country.name == country.name
    ]
    
    # Tariffs reduce exports, which negatively affects GDP
    for policy in incoming_policies:
        # Calculate weighted average tariff rate
        avg_rate = sum(policy.sector_rates.values()) / len(policy.sector_rates)
        # Larger negative effect on GDP growth (exports directly contribute to GDP)
        incoming_tariff_impact -= avg_rate * 0.15
    
    return outgoing_tariff_impact + incoming_tariff_impact


def _calculate_trade_gdp_impact(state: SimulationState, country: Country) -> float:
    """
    Calculate GDP impact from changes in trade flows.
    
    Args:
        state: Current simulation state
        country: The country
        
    Returns:
        GDP growth impact from trade patterns
    """
    # Get trade flows involving this country
    country_trade_flows = [
        flow for flow in state.trade_flows
        if flow.exporter.name == country.name or flow.importer.name == country.name
    ]
    
    # Not enough data to calculate changes
    if len(country_trade_flows) < 2:
        return 0.0
    
    # Calculate trade as % of GDP (simplified)
    exports = sum(
        flow.total_value for flow in state.trade_flows
        if flow.exporter.name == country.name
    )
    
    # Changes in exports directly affect GDP
    # For simplicity, assume exports are 20-50% of GDP depending on country
    export_to_gdp_ratio = 0.3  # Default 30%
    
    if country.name == "US":
        export_to_gdp_ratio = 0.1  # US: exports ~10% of GDP
    elif country.name == "China":
        export_to_gdp_ratio = 0.2  # China: exports ~20% of GDP
    elif country.name == "Indonesia":
        export_to_gdp_ratio = 0.25  # Indonesia: exports ~25% of GDP
    
    # Calculate export growth
    latest_flows = [
        flow for flow in state.trade_flows 
        if flow.exporter.name == country.name and
        flow.year == state.year and flow.quarter == state.quarter
    ]
    
    prev_flows = [
        flow for flow in state.trade_flows 
        if flow.exporter.name == country.name and
        (flow.year < state.year or 
         (flow.year == state.year and flow.quarter < state.quarter))
    ]
    
    # Not enough data to calculate growth
    if not latest_flows or not prev_flows:
        return 0.0
    
    latest_export = sum(flow.total_value for flow in latest_flows)
    prev_export = sum(flow.total_value for flow in prev_flows)
    
    # Avoid division by zero
    if prev_export == 0:
        return 0.0
    
    export_growth = (latest_export - prev_export) / prev_export
    
    # GDP impact is export growth * export-to-GDP ratio
    return export_growth * export_to_gdp_ratio


def _calculate_investment_gdp_impact(state: SimulationState, country: Country) -> float:
    """
    Calculate GDP impact from investment policy actions.
    
    Args:
        state: Current simulation state
        country: The country
        
    Returns:
        GDP growth impact from investment policies
    """
    # Look for investment actions in the recent period
    investment_actions = [
        action for action in state.recent_actions
        if action.country.name == country.name and action.action_type == "investment"
    ]
    
    impact = 0.0
    
    for action in investment_actions:
        # Investment has a multiplier effect on GDP
        # Magnitude is the percentage of GDP being invested
        impact += action.magnitude * 1.5  # Multiplier of 1.5
    
    return impact


def _calculate_event_gdp_impact(state: SimulationState, country: Country) -> float:
    """
    Calculate GDP impact from external events.
    
    Args:
        state: Current simulation state
        country: The country
        
    Returns:
        GDP growth impact from external events
    """
    impact = 0.0
    
    for event in state.active_events:
        # Check if this country is affected by the event
        if country.name in event.affected_countries:
            # Direct impact from event configuration
            impact += event.gdp_impact.get(country.name, 0.0)
    
    return impact


def _calculate_global_economy_impact(state: SimulationState) -> float:
    """
    Calculate GDP impact from global economic conditions.
    
    Args:
        state: Current simulation state
        
    Returns:
        GDP growth impact from global economy
    """
    # Simplified global economic cycle model
    # In a real model, this would consider many more factors
    year = state.year
    quarter = state.quarter
    
    # Model a long-term economic cycle with period of ~20 quarters (5 years)
    cycle_position = (year * 4 + quarter) % 20
    
    # Simple sinusoidal model for economic cycle
    cycle_impact = 0.005 * np.sin(2 * np.pi * cycle_position / 20)
    
    return cycle_impact
