"""Simulation orchestration engine for trade war scenarios."""

import logging
from typing import Dict, List, Optional

from tradewar.agents.base_agent import BaseAgent
from tradewar.agents.factory import AgentFactory
from tradewar.config import config
from tradewar.economics.models import Country, EconomicAction
from tradewar.economics.tariff import calculate_tariff_impact
from tradewar.economics.trade_balance import update_trade_balance
from tradewar.simulation.events import EventGenerator
from tradewar.simulation.state import SimulationState

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Core engine for running trade war simulations.
    
    This class orchestrates the simulation by managing agents, processing their
    actions, updating the economic state, and handling external events.
    """
    
    def __init__(self, countries: List[Country], initial_state: Optional[SimulationState] = None):
        """
        Initialize the simulation engine.
        
        Args:
            countries: List of countries participating in the simulation
            initial_state: Optional initial state, otherwise created from scratch
        """
        self.countries = countries
        self.state = initial_state or SimulationState(countries=countries)
        self.agents: Dict[str, BaseAgent] = {}
        self.event_generator = EventGenerator(config.simulation.random_seed)
        self.current_year = 0
        self.current_quarter = 0
        self.max_years = config.simulation.years
        self.quarters_per_year = config.simulation.steps_per_year
        self.history: List[SimulationState] = []
        
        # Initialize agents for each country
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """Create agent instances for each country in the simulation."""
        agent_factory = AgentFactory()
        
        for country in self.countries:
            self.agents[country.name] = agent_factory.create_agent(country)
            logger.info(f"Initialized agent for {country.name}")
    
    def run_full_simulation(self) -> List[SimulationState]:
        """
        Run the full simulation for the configured time period.
        
        Returns:
            List of simulation states, one per time step
        """
        logger.info(f"Starting simulation for {self.max_years} years")
        
        for year in range(self.max_years):
            self.current_year = year
            
            for quarter in range(self.quarters_per_year):
                self.current_quarter = quarter
                self.step()
                self.history.append(self.state.clone())
        
        logger.info("Simulation completed")
        return self.history
    
    def step(self) -> SimulationState:
        """
        Execute a single simulation time step.
        
        Returns:
            Updated simulation state after the step
        """
        logger.info(f"Running simulation step: Year {self.current_year}, Quarter {self.current_quarter}")
        
        # 1. Generate external events
        events = self.event_generator.generate_events(
            self.state, self.current_year, self.current_quarter
        )
        self.state.add_events(events)
        
        # 2. Collect actions from agents
        actions: List[EconomicAction] = []
        for country_name, agent in self.agents.items():
            action = agent.decide_action(self.state)
            actions.append(action)
            logger.info(f"{country_name} decided: {action.action_type} - {action.justification}")
        
        # 3. Apply actions to update the economic state
        self._apply_actions(actions)
        
        # 4. Update global economic indicators
        self._update_economic_indicators()
        
        # 5. Update agent strategies based on new state
        for agent in self.agents.values():
            agent.update_strategy(self.state)
        
        return self.state
    
    def _apply_actions(self, actions: List[EconomicAction]) -> None:
        """
        Apply economic actions to the simulation state.
        
        Args:
            actions: List of actions from all agents
        """
        for action in actions:
            self.state.add_action(action)
            
            # Handle different action types
            if action.action_type == "tariff_increase" or action.action_type == "tariff_adjustment":
                if action.target_country:
                    # Calculate and apply tariff policy
                    policy = self.agents[action.country.name].calculate_tariff_policy(
                        self.state, action.target_country
                    )
                    self.state.add_tariff_policy(policy)
                    
                    # Calculate economic impact
                    tariff_impact = calculate_tariff_impact(
                        self.state, policy, action.country, action.target_country
                    )
                    self.state.apply_tariff_impact(tariff_impact)
            
            # Add logic for other action types here
    
    def _update_economic_indicators(self) -> None:
        """Update all economic indicators based on recent actions and events."""
        # Update trade balances
        for country in self.countries:
            for partner in self.countries:
                if country != partner:
                    update_trade_balance(self.state, country, partner)
        
        # Other economic updates would go here
        # - GDP impact
        # - Employment effects
        # - Currency value changes
        # - etc.
        
        # Finalize the state update
        self.state.finalize_update(self.current_year, self.current_quarter)
