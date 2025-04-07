"""Result retrieval endpoints for the trade war simulation API."""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from tradewar.api.schemas import (EconomicTimeSeriesData, SimulationResult,
                                TradeFlowData)
from tradewar.api.server import get_simulation_manager
from tradewar.economics.models import Country

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{simulation_id}", response_model=SimulationResult)
async def get_simulation_results(
    simulation_id: str,
    from_year: Optional[int] = Query(None, description="Starting year for results"),
    to_year: Optional[int] = Query(None, description="Ending year for results"),
    sim_manager = Depends(get_simulation_manager)
):
    """
    Get comprehensive results for a simulation.
    
    Args:
        simulation_id: ID of the simulation
        from_year: Optional start year for filtering results
        to_year: Optional end year for filtering results
        sim_manager: Simulation manager dependency
        
    Returns:
        Comprehensive simulation results
    """
    # Get the simulation engine
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    try:
        # Get all history states
        history = engine.history
        
        # Filter by year if specified
        if from_year is not None:
            history = [state for state in history if state.year >= from_year]
        if to_year is not None:
            history = [state for state in history if state.year <= to_year]
        
        # Extract country names
        country_names = [country.name for country in engine.countries]
        
        # Create time series data for key metrics
        gdp_series = _create_gdp_time_series(history, country_names)
        inflation_series = _create_inflation_time_series(history, country_names)
        unemployment_series = _create_unemployment_time_series(history, country_names)
        currency_series = _create_currency_time_series(history, country_names)
        
        # Extract trade balances at the end of simulation
        trade_balances = {}
        if history:
            last_state = history[-1]
            for country in last_state.countries:
                # Get the economic indicator for this country
                indicators = last_state.economic_indicators.get(country.name, [])
                if indicators:
                    latest_indicator = indicators[-1]
                    trade_balances[country.name] = latest_indicator.trade_balance
        
        # Create result object
        return SimulationResult(
            simulation_id=simulation_id,
            total_years=engine.max_years,
            current_year=engine.current_year,
            current_quarter=engine.current_quarter,
            countries=country_names,
            trade_balances=trade_balances,
            gdp_series=gdp_series,
            inflation_series=inflation_series,
            unemployment_series=unemployment_series,
            currency_series=currency_series
        )
    
    except Exception as e:
        logger.error(f"Error getting simulation results {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting simulation results: {str(e)}"
        )


@router.get("/{simulation_id}/trade-flows", response_model=List[TradeFlowData])
async def get_trade_flows(
    simulation_id: str,
    year: Optional[int] = Query(None, description="Year to filter by"),
    quarter: Optional[int] = Query(None, description="Quarter to filter by"),
    country: Optional[str] = Query(None, description="Country to filter by"),
    sim_manager = Depends(get_simulation_manager)
):
    """
    Get trade flow data from a simulation.
    
    Args:
        simulation_id: ID of the simulation
        year: Optional year for filtering
        quarter: Optional quarter for filtering
        country: Optional country for filtering
        sim_manager: Simulation manager dependency
        
    Returns:
        List of trade flow data
    """
    # Get the simulation engine
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    try:
        # Get all trade flows
        flows = engine.state.trade_flows
        
        # Apply filters
        if year is not None:
            flows = [flow for flow in flows if flow.year == year]
        if quarter is not None:
            flows = [flow for flow in flows if flow.quarter == quarter]
        if country is not None:
            flows = [
                flow for flow in flows 
                if flow.exporter.name == country or flow.importer.name == country
            ]
        
        # Convert to API schema
        api_flows = []
        for flow in flows:
            api_flow = TradeFlowData(
                exporter=flow.exporter.name,
                importer=flow.importer.name,
                year=flow.year,
                quarter=flow.quarter,
                total_value=flow.total_value,
                sectors={k: v for k, v in flow.sector_values.items()}
            )
            api_flows.append(api_flow)
        
        return api_flows
    
    except Exception as e:
        logger.error(f"Error getting trade flows for {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting trade flows: {str(e)}"
        )


@router.get("/{simulation_id}/actions", response_model=Dict)
async def get_policy_actions(
    simulation_id: str,
    from_year: Optional[int] = Query(None, description="Starting year for actions"),
    to_year: Optional[int] = Query(None, description="Ending year for actions"),
    country: Optional[str] = Query(None, description="Country to filter by"),
    action_type: Optional[str] = Query(None, description="Action type to filter by"),
    sim_manager = Depends(get_simulation_manager)
):
    """
    Get policy actions from a simulation.
    
    Args:
        simulation_id: ID of the simulation
        from_year: Optional start year for filtering
        to_year: Optional end year for filtering
        country: Optional country for filtering
        action_type: Optional action type for filtering
        sim_manager: Simulation manager dependency
        
    Returns:
        Dictionary with policy action data
    """
    # Get the simulation engine
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    try:
        # Get all actions
        actions = engine.state.all_actions
        
        # Apply filters
        if from_year is not None:
            actions = [action for action in actions if action.year >= from_year]
        if to_year is not None:
            actions = [action for action in actions if action.year <= to_year]
        if country is not None:
            actions = [action for action in actions if action.country.name == country]
        if action_type is not None:
            actions = [action for action in actions if action.action_type == action_type]
        
        # Convert to API format
        api_actions = []
        for action in actions:
            api_action = {
                "country": action.country.name,
                "action_type": action.action_type,
                "target_country": action.target_country.name if action.target_country else None,
                "sectors": action.sectors,
                "magnitude": action.magnitude,
                "justification": action.justification,
                "year": action.year,
                "quarter": action.quarter
            }
            api_actions.append(api_action)
        
        # Group by country for easier analysis
        by_country = {}
        for action in api_actions:
            country = action["country"]
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(action)
        
        return {
            "actions": api_actions,
            "by_country": by_country,
            "total_count": len(api_actions)
        }
    
    except Exception as e:
        logger.error(f"Error getting policy actions for {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting policy actions: {str(e)}"
        )


def _create_gdp_time_series(history, country_names) -> List[EconomicTimeSeriesData]:
    """Create GDP time series for each country."""
    series_list = []
    
    for country_name in country_names:
        times = []
        values = []
        
        for state in history:
            # Find the country in this state
            country = next((c for c in state.countries if c.name == country_name), None)
            if country:
                time_label = f"Y{state.year+1}Q{state.quarter+1}"
                times.append(time_label)
                values.append(country.gdp)
        
        if times and values:
            series = EconomicTimeSeriesData(
                country=country_name,
                metric="gdp",
                times=times,
                values=values
            )
            series_list.append(series)
    
    return series_list


def _create_inflation_time_series(history, country_names) -> List[EconomicTimeSeriesData]:
    """Create inflation time series for each country."""
    series_list = []
    
    for country_name in country_names:
        times = []
        values = []
        
        for state in history:
            indicators = state.economic_indicators.get(country_name, [])
            if indicators:
                time_label = f"Y{state.year+1}Q{state.quarter+1}"
                times.append(time_label)
                values.append(indicators[-1].inflation)
        
        if times and values:
            series = EconomicTimeSeriesData(
                country=country_name,
                metric="inflation",
                times=times,
                values=values
            )
            series_list.append(series)
    
    return series_list


def _create_unemployment_time_series(history, country_names) -> List[EconomicTimeSeriesData]:
    """Create unemployment time series for each country."""
    series_list = []
    
    for country_name in country_names:
        times = []
        values = []
        
        for state in history:
            indicators = state.economic_indicators.get(country_name, [])
            if indicators:
                time_label = f"Y{state.year+1}Q{state.quarter+1}"
                times.append(time_label)
                values.append(indicators[-1].unemployment)
        
        if times and values:
            series = EconomicTimeSeriesData(
                country=country_name,
                metric="unemployment",
                times=times,
                values=values
            )
            series_list.append(series)
    
    return series_list


def _create_currency_time_series(history, country_names) -> List[EconomicTimeSeriesData]:
    """Create currency value time series for each country."""
    series_list = []
    
    for country_name in country_names:
        times = []
        values = []
        
        for state in history:
            indicators = state.economic_indicators.get(country_name, [])
            if indicators:
                time_label = f"Y{state.year+1}Q{state.quarter+1}"
                times.append(time_label)
                values.append(indicators[-1].currency_value)
        
        if times and values:
            series = EconomicTimeSeriesData(
                country=country_name,
                metric="currency_value",
                times=times,
                values=values
            )
            series_list.append(series)
    
    return series_list
