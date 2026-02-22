"""Simulation orchestration engine for trade war scenarios."""

import logging
import random
from typing import Dict, List, Optional, TYPE_CHECKING

# Import non-circular imports first
from tradewar.config import config
from tradewar.economics.gdp import calculate_gdp_impact
from tradewar.economics.models import ActionType, Country, EconomicAction, TradeFlow
from tradewar.economics.tariff import calculate_tariff_impact
from tradewar.economics.trade_balance import update_trade_balance
from tradewar.simulation.events import EventGenerator
from tradewar.simulation.state import SimulationState

# Use TYPE_CHECKING for circular imports
if TYPE_CHECKING:
    from tradewar.agents.base_agent import BaseAgent
    from tradewar.agents.factory import AgentFactory

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Core engine for running trade war simulations.
    
    This class orchestrates the simulation by managing agents, processing their
    actions, updating the economic state, and handling external events.
    """
    
    def __init__(self, countries: List[Country], start_year: int = 2023):
        """
        Initialize the simulation engine.
        
        Args:
            countries: List of countries to include in simulation
            start_year: Year to start the simulation
        """
        if not countries:
            raise ValueError("Simulation requires at least one country")

        random.seed(config.simulation.random_seed)
        self.countries = countries
        self.current_year = start_year
        self.current_quarter = 0
        self.quarters_per_year = 4
        self.max_years = 5
        self.state = SimulationState(
            countries=countries,
            year=start_year,
            quarter=self.current_quarter
        )
        
        # Initialize some basic trade flows between countries
        self._initialize_trade_flows()
        
        self.agents: Dict[str, "BaseAgent"] = {}
        self.event_generator = EventGenerator(config.simulation.random_seed)
        self.history: List[SimulationState] = []
        
        # Initialize agents for each country
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """Create agent instances for each country in the simulation."""
        # Import here to avoid circular import
        from tradewar.agents.factory import AgentFactory
        
        agent_factory = AgentFactory()
        
        for country in self.countries:
            self.agents[country.name] = agent_factory.create_agent(country)
            logger.info(f"Initialized agent for {country.name}")
    
    def _initialize_trade_flows(self):
        """Initialize some basic trade flows between countries to avoid no-data warnings."""
        if len(self.countries) < 2:
            return
            
        # Get current year and quarter
        year = self.current_year
        quarter = self.current_quarter
        
        # Create pairwise flows between countries
        for i, country1 in enumerate(self.countries):
            for j, country2 in enumerate(self.countries):
                if i != j:  # Skip self-trade
                    # Create simple sector mappings
                    sectors = ["technology", "manufacturing", "agriculture", "services"]
                    
                    # Create basic volumes and values
                    sector_volumes = {}
                    sector_values = {}
                    
                    for sector in sectors:
                        # Basic trade volume based on GDP
                        base_volume = (country1.gdp * country2.gdp) ** 0.4 * 0.001
                        sector_volumes[sector] = base_volume * 0.25  # Split evenly across sectors
                        sector_values[sector] = sector_volumes[sector] * 1.1  # Simple price factor
                    
                    # Create flow from country1 to country2
                    flow = TradeFlow(
                        exporter=country1,
                        importer=country2,
                        year=year,
                        quarter=quarter,
                        sector_volumes=sector_volumes,
                        sector_values=sector_values
                    )
                    
                    # Add to state
                    self.state.trade_flows.append(flow)
    
    def run_full_simulation(self) -> List[SimulationState]:
        """
        Run the full simulation for the configured time period.
        
        Returns:
            List of simulation states, one per time step
        """
        logger.info(f"Starting simulation for {self.max_years} years")
        
        start_year = self.state.year

        for year_offset in range(self.max_years):
            year = start_year + year_offset
            self.current_year = year
            
            for quarter in range(self.quarters_per_year):
                self.current_quarter = quarter
                self.step(year=year, quarter=quarter)
                self.history.append(self.state.clone())
        
        logger.info("Simulation completed")
        return self.history
    
    def step(self, year: Optional[int] = None, quarter: Optional[int] = None) -> SimulationState:
        """Advance the simulation by one quarter."""
        if year is None or quarter is None:
            next_year = self.current_year
            next_quarter = self.current_quarter + 1
            if next_quarter >= self.quarters_per_year:
                next_year += 1
                next_quarter = 0
            self.current_year = next_year
            self.current_quarter = next_quarter
        else:
            self.current_year = year
            self.current_quarter = quarter

        self.state.year = self.current_year
        self.state.quarter = self.current_quarter
        
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
            agent.record_action(action)
            actions.append(action)
            logger.info(f"{country_name} decided: {action.action_type} - {action.justification}")
        
        # 3. Apply actions to update the economic state
        self._apply_actions(actions)
        
        # 4. Apply economic impacts of actions
        self._apply_economic_impacts(actions)
        
        # 5. Update global economic indicators
        self._update_economic_indicators()
        
        # 6. Update agent strategies based on new state
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
            if action.action_type in {
                ActionType.TARIFF_INCREASE,
                ActionType.TARIFF_ADJUSTMENT,
                ActionType.TARIFF_DECREASE,
            }:
                if action.target_country:
                    # Calculate and apply tariff policy
                    policy = self.agents[action.country.name].calculate_tariff_policy(
                        self.state, action.target_country
                    )
                    if action.action_type == ActionType.TARIFF_DECREASE:
                        policy.sector_rates = {
                            sector: max(0.0, rate - abs(action.magnitude))
                            for sector, rate in policy.sector_rates.items()
                        }
                    self.state.add_tariff_policy(policy)
                    
                    # Calculate economic impact
                    tariff_impact = calculate_tariff_impact(
                        self.state, policy, action.country, action.target_country
                    )
                    self.state.apply_tariff_impact(tariff_impact)

            if action.action_type in {
                ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
                ActionType.FRIEND_SHORING,
            } and action.target_country:
                redirect_bonus = min(0.2, max(0.0, action.magnitude))
                for flow in self.state.trade_flows:
                    if flow.exporter.name == action.target_country.name:
                        for sector in action.sectors:
                            if sector in flow.sector_volumes:
                                flow.sector_volumes[sector] *= (1 + redirect_bonus)
                                flow.sector_values[sector] *= (1 + redirect_bonus)

            if action.action_type == ActionType.DATA_SOVEREIGNTY:
                for flow in self.state.trade_flows:
                    if flow.exporter.name == action.country.name or flow.importer.name == action.country.name:
                        if "digital_services" in flow.sector_volumes:
                            penalty = min(0.5, max(0.0, action.magnitude))
                            flow.sector_volumes["digital_services"] *= (1 - penalty)
                            flow.sector_values["digital_services"] *= (1 - penalty)

            if action.action_type == ActionType.IMPORT_QUOTA:
                quota_factor = max(0.0, 1 - min(0.9, max(0.0, action.magnitude)))
                for flow in self.state.trade_flows:
                    affected_importer = flow.importer.name == action.country.name
                    affected_exporter = (
                        action.target_country is None or
                        flow.exporter.name == action.target_country.name
                    )
                    if affected_importer and affected_exporter:
                        target_sectors = action.sectors or list(flow.sector_volumes.keys())
                        for sector in target_sectors:
                            if sector in flow.sector_volumes:
                                flow.sector_volumes[sector] *= quota_factor
                                flow.sector_values[sector] *= quota_factor
            
            # Add logic for other action types here
    
    def _apply_economic_impacts(self, actions: List[EconomicAction]) -> None:
        """Apply economic impacts of actions to countries."""
        # Action-specific immediate impacts
        for action in actions:
            # Find the source country
            source = next((c for c in self.countries if c.name == action.country.name), None)
            if not source:
                continue

            if action.action_type == ActionType.CURRENCY_DEVALUATION:
                source.currency_value *= max(0.6, 1 - action.magnitude * 0.2)

            if action.action_type == ActionType.INDUSTRIAL_SUBSIDY:
                source.gdp *= (1 + min(0.02, action.magnitude * 0.02))

            if action.action_type == ActionType.GREEN_TECH_INVESTMENT:
                source.gdp *= (1 + min(0.02, action.magnitude * 0.03))

            if action.action_type == ActionType.TECH_EXPORT_CONTROL and action.target_country:
                target = next((c for c in self.countries if c.name == action.target_country.name), None)
                if target:
                    target.gdp *= (1 - min(0.02, action.magnitude * 0.02))

            if action.action_type == ActionType.EXPORT_SUBSIDY:
                source.gdp *= (1 + min(0.01, action.magnitude * 0.015))

        # Apply GDP growth model to all countries
        for country in self.countries:
            growth_rate, _ = calculate_gdp_impact(
                state=self.state,
                country=country,
                year=self.current_year,
                quarter=self.current_quarter,
            )
            country.gdp *= (1 + growth_rate)
    
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
