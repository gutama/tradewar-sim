"""FastAPI implementation for the trade war simulation API."""

import logging
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

class SimulationManager:
    """Simple in-memory manager for simulation engine instances."""

    def __init__(self):
        self.active_simulations: Dict[str, SimulationEngine] = {}

    def register_simulation(self, engine: SimulationEngine) -> str:
        simulation_id = f"sim_{uuid.uuid4().hex[:8]}"
        self.active_simulations[simulation_id] = engine
        return simulation_id

    def get_simulation(self, simulation_id: str) -> Optional[SimulationEngine]:
        return self.active_simulations.get(simulation_id)

    def delete_simulation(self, simulation_id: str) -> bool:
        if simulation_id not in self.active_simulations:
            return False
        del self.active_simulations[simulation_id]
        return True

    def list_simulations(self) -> List[str]:
        return sorted(self.active_simulations.keys())


_simulation_manager = SimulationManager()


def get_simulation_manager() -> SimulationManager:
    """Dependency provider for simulation manager."""
    return _simulation_manager


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Trade War Simulation API",
        "version": "0.1.0",
        "docs_url": "/docs",
    }


@app.get("/api/simulations", response_model=List[str])
async def list_simulations():
    """List active simulation IDs."""
    return _simulation_manager.list_simulations()


from tradewar.api.routes.results import router as results_router
from tradewar.api.routes.simulation import router as simulation_router

app.include_router(simulation_router, prefix="/api")
app.include_router(results_router, prefix="/api")
