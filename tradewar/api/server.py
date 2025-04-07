"""FastAPI implementation for the trade war simulation API."""

import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from tradewar.api.schemas import (CountryData, SimulationConfig,
                                 SimulationResult, SimulationState)
from tradewar.config import config
from tradewar.simulation.engine import SimulationEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Trade War Simulation API",
    description="API for running and analyzing trade war simulations",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for simulation instances
active_simulations: Dict[str, SimulationEngine] = {}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Trade War Simulation API",
        "version": "0.1.0",
        "docs_url": "/docs",
    }


@app.post("/api/simulation/start", response_model=str)
async def start_simulation(sim_config: SimulationConfig):
    """Start a new simulation with the provided configuration."""
    try:
        # Create a new simulation ID
        simulation_id = f"sim_{len(active_simulations) + 1}"
        
        # Initialize countries from config
        countries = [
            country.dict() for country in sim_config.countries
        ]
        
        # Create simulation engine
        engine = SimulationEngine(countries)
        active_simulations[simulation_id] = engine
        
        logger.info(f"Started new simulation with ID: {simulation_id}")
        
        return simulation_id
    
    except Exception as e:
        logger.error(f"Error starting simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting simulation: {str(e)}")


@app.post("/api/simulation/{simulation_id}/step", response_model=SimulationState)
async def step_simulation(simulation_id: str):
    """Advance the simulation by one time step."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    try:
        engine = active_simulations[simulation_id]
        state = engine.step()
        
        # Convert to API schema
        api_state = SimulationState(
            year=state.year,
            quarter=state.quarter,
            countries=[
                CountryData(
                    name=country.name,
                    gdp=country.gdp,
                    inflation_rate=country.inflation_rate,
                    unemployment_rate=country.unemployment_rate,
                    currency_value=country.currency_value,
                ) for country in state.countries
            ],
            # Include other state data as needed
        )
        
        return api_state
    
    except Exception as e:
        logger.error(f"Error stepping simulation {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error stepping simulation: {str(e)}"
        )


@app.get("/api/simulation/{simulation_id}/state", response_model=SimulationState)
async def get_simulation_state(simulation_id: str):
    """Get the current state of a simulation."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    try:
        engine = active_simulations[simulation_id]
        state = engine.state
        
        # Convert to API schema (similar to step_simulation)
        api_state = SimulationState(
            year=state.year,
            quarter=state.quarter,
            countries=[
                CountryData(
                    name=country.name,
                    gdp=country.gdp,
                    inflation_rate=country.inflation_rate,
                    unemployment_rate=country.unemployment_rate,
                    currency_value=country.currency_value,
                ) for country in state.countries
            ],
            # Include other state data as needed
        )
        
        return api_state
    
    except Exception as e:
        logger.error(f"Error getting simulation state {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting simulation state: {str(e)}"
        )


@app.get("/api/results/{simulation_id}", response_model=SimulationResult)
async def get_simulation_results(
    simulation_id: str,
    from_year: Optional[int] = Query(None, description="Starting year for results"),
    to_year: Optional[int] = Query(None, description="Ending year for results"),
):
    """Get results for a completed simulation."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    try:
        engine = active_simulations[simulation_id]
        history = engine.history
        
        # Filter by year if specified
        if from_year is not None:
            history = [state for state in history if state.year >= from_year]
        if to_year is not None:
            history = [state for state in history if state.year <= to_year]
        
        # Convert to API result schema
        result = SimulationResult(
            simulation_id=simulation_id,
            total_years=engine.max_years,
            current_year=engine.current_year,
            current_quarter=engine.current_quarter,
            countries=[country.name for country in engine.countries],
            # Include result data
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting simulation results {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting simulation results: {str(e)}"
        )


@app.delete("/api/simulation/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete a simulation and free resources."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    try:
        del active_simulations[simulation_id]
        return {"success": True, "message": f"Simulation {simulation_id} deleted"}
    
    except Exception as e:
        logger.error(f"Error deleting simulation {simulation_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting simulation: {str(e)}"
        )
