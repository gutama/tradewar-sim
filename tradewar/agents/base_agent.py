"""Base agent class defining the interface for all country-specific agents."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING

from tradewar.economics.models import Country, EconomicAction, TariffPolicy

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from tradewar.simulation.state import SimulationState


class BaseAgent(ABC):
    """
    Abstract base class for country agents in the trade war simulation.
    
    Each country agent is responsible for making policy decisions based on the
    current economic state and its own policy objectives.
    """

    def __init__(self, country: Country, strategy_params: Optional[Dict] = None):
        """
        Initialize the agent with a country and optional strategy parameters.
        
        Args:
            country: The country this agent represents
            strategy_params: Optional parameters to customize agent behavior
        """
        self.country = country
        self.strategy_params = strategy_params or {}
        self.previous_actions: List[EconomicAction] = []
    
    @abstractmethod
    def decide_action(self, state: "SimulationState") -> EconomicAction:
        """
        Decide the next economic action based on current simulation state.
        
        Args:
            state: Current simulation state
            
        Returns:
            An economic action to be taken by this country
        """
        pass
    
    @abstractmethod
    def calculate_tariff_policy(
        self, state: "SimulationState", target_country: Country
    ) -> TariffPolicy:
        """
        Calculate tariff policy toward a target country.
        
        Args:
            state: Current simulation state
            target_country: Country to set tariffs against
            
        Returns:
            Tariff policy specifying rates for different sectors
        """
        pass
    
    def update_strategy(self, state: "SimulationState") -> None:
        """
        Update internal strategy based on simulation developments.
        
        Args:
            state: Current simulation state
        """
        pass
    
    def record_action(self, action: EconomicAction) -> None:
        """
        Record an executed action for future reference.
        
        Args:
            action: The economic action that was executed
        """
        self.previous_actions.append(action)
