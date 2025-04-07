"""
Simulation module for trade war dynamics.

This module provides components for running economic simulations of trade wars,
including state management, event generation, and stability analysis.
"""

from tradewar.simulation.engine import SimulationEngine
from tradewar.simulation.events import EventGenerator
from tradewar.simulation.stability import StabilityAnalyzer
from tradewar.simulation.state import SimulationState, TariffImpact

__all__ = [
    "SimulationEngine",
    "SimulationState",
    "TariffImpact",
    "EventGenerator",
    "StabilityAnalyzer",
]
