"""Simulation control endpoints for the trade war simulation API."""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from tradewar.api.schemas import CountryData, SimulationConfig, SimulationState
from tradewar.api.server import get_simulation_manager
from tradewar.economics.models import Country
from tradewar.simulation.engine import SimulationEngine
from tradewar.simulation.stability import StabilityAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/start", response_model=str)
async def start_simulation(
    config: SimulationConfig,
    sim_manager = Depends(get_simulation_manager)
):
    """
    Start a new simulation with the provided configuration.
    
    Args:
        config: Configuration for the simulation
        sim_manager: Simulation manager dependency
        
    Returns:
        Simulation ID
    """
    try:
        # Initialize countries from config
        countries = []
        for country_data in config.countries:
            # Convert from API schema to domain model
            country = Country(
                name=country_data.name,
                gdp=country_data.gdp,
                population=country_data.population or 0,
                inflation_rate=country_data.inflation_rate,
                unemployment_rate=country_data.unemployment_rate,
                currency_value=country_data.currency_value,
                sectors=country_data.sectors or {}
            )
            countries.append(country)
        
        # Create a simulation engine with these countries
        engine = SimulationEngine(countries=countries)
        engine.max_years = config.years
        engine.quarters_per_year = config.steps_per_year
        
        # Register in the simulation manager
        simulation_id = sim_manager.register_simulation(engine)
        
        logger.info(f"Started new simulation with ID: {simulation_id}")
        return simulation_id
    
    except Exception as e:
        logger.error(f"Error starting simulation: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error starting simulation: {str(e)}"
        )


@router.post("/{simulation_id}/step", response_model=SimulationState)
async def step_simulation(
    simulation_id: str,
    steps: int = Query(1, ge=1, le=10, description="Number of steps to advance"),
    sim_manager = Depends(get_simulation_manager)
):
    """
    Advance a simulation by one or more steps.
    
    Args:
        simulation_id: ID of the simulation to advance
        steps: Number of steps to advance (default: 1)
        sim_manager: Simulation manager dependency
        
    Returns:
        Updated simulation state
    """
    # Get the simulation engine
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    try:
        # Run the specified number of steps
        for _ in range(steps):
            state = engine.step()
        
        # Convert to API schema
        return _convert_to_api_state(state)
    
    except Exception as e:
        logger.error(f"Error stepping simulation {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error stepping simulation: {str(e)}"
        )


@router.get("/{simulation_id}/state", response_model=SimulationState)
async def get_simulation_state(
    simulation_id: str,
    sim_manager = Depends(get_simulation_manager)
):
    """
    Get the current state of a simulation.
    
    Args:
        simulation_id: ID of the simulation
        sim_manager: Simulation manager dependency
        
    Returns:
        Current simulation state
    """
    # Get the simulation engine
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    try:
        # Get current state
        state = engine.state
        
        # Convert to API schema
        return _convert_to_api_state(state)
    
    except Exception as e:
        logger.error(f"Error getting simulation state {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting simulation state: {str(e)}"
        )


@router.get("/{simulation_id}/status", response_model=Dict)
async def get_simulation_status(
    simulation_id: str,
    sim_manager=Depends(get_simulation_manager)
):
    """Get a lightweight status payload for a simulation."""
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )

    return {
        "simulation_id": simulation_id,
        "year": engine.state.year,
        "quarter": engine.state.quarter,
        "countries": [country.name for country in engine.countries],
        "history_length": len(engine.history),
    }


@router.get("/{simulation_id}/stability", response_model=Dict)
async def analyze_stability(
    simulation_id: str,
    country: Optional[str] = None,
    sim_manager = Depends(get_simulation_manager)
):
    """
    Analyze stability of the economic system or a specific country.
    
    Args:
        simulation_id: ID of the simulation
        country: Optional country name to analyze
        sim_manager: Simulation manager dependency
        
    Returns:
        Stability analysis results
    """
    # Get the simulation engine
    engine = sim_manager.get_simulation(simulation_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    try:
        # Create stability analyzer
        analyzer = StabilityAnalyzer()
        
        # Analyze global or country-specific stability
        if country:
            # Find the country in the simulation
            target_country = next(
                (c for c in engine.state.countries if c.name == country),
                None
            )
            
            if not target_country:
                raise HTTPException(
                    status_code=404,
                    detail=f"Country {country} not found in simulation"
                )
            
            score, factors = analyzer.analyze_country_stability(
                engine.state, target_country
            )
            
            return {
                "country": country,
                "stability_score": score,
                "factors": factors,
                "interpretation": _interpret_stability_score(score)
            }
        else:
            # Global stability analysis
            score, factors = analyzer.analyze_global_stability(engine.state)
            
            return {
                "global_stability_score": score,
                "factors": factors,
                "trend": factors.get("trend", "unknown"),
                "interpretation": _interpret_stability_score(score)
            }
    
    except Exception as e:
        logger.error(f"Error analyzing stability for {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stability: {str(e)}"
        )


def _convert_to_api_state(state) -> SimulationState:
    """Convert domain model state to API schema."""
    # Convert countries
    countries = [
        CountryData(
            name=country.name,
            gdp=country.gdp,
            population=country.population,
            inflation_rate=country.inflation_rate,
            unemployment_rate=country.unemployment_rate,
            currency_value=country.currency_value,
            sectors=country.sectors
        ) for country in state.countries
    ]
    
    # Create API state object
    # This is simplified - would need to convert other properties too
    return SimulationState(
        year=state.year,
        quarter=state.quarter,
        countries=countries,
        # Additional fields would be converted here
    )


def _interpret_stability_score(score: float) -> str:
    """
    Interpret a stability score with a descriptive label.
    
    Args:
        score: Stability score from 0-1
        
    Returns:
        String interpretation
    """
    if score >= 0.8:
        return "Very stable economic conditions"
    elif score >= 0.6:
        return "Stable economic conditions"
    elif score >= 0.4:
        return "Moderately stable economic conditions"
    elif score >= 0.2:
        return "Unstable economic conditions"
    else:
        return "Highly unstable economic conditions with high risk of economic crisis"
