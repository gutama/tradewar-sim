"""Indonesia-specific agent implementation for trade war simulation."""

from typing import Dict, List, Optional

from tradewar.agents.base_agent import BaseAgent
from tradewar.economics.models import ActionType, Country, EconomicAction, TariffPolicy
from tradewar.llm.client import LLMClient
from tradewar.llm.parser import LLMResponseParser
from tradewar.llm.prompts.indonesia_policy import generate_indonesia_policy_prompt
from tradewar.simulation.state import SimulationState


class IndonesiaAgent(BaseAgent):
    """
    Agent representing Indonesia in the trade war simulation.
    
    Models Indonesia's trade policy with focus on economic development,
    balancing relations with major powers, and protecting domestic industries.
    """
    
    def __init__(
        self, 
        country: Country, 
        strategy_params: Optional[Dict] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the Indonesia agent.
        
        Args:
            country: The Indonesia country object
            strategy_params: Parameters to customize Indonesia's policy strategy
            llm_client: Optional LLM client for policy generation
        """
        strategy_params = strategy_params or {}
        super().__init__(country, strategy_params)
        self.llm_client = llm_client
        self.protectionist_tendency = strategy_params.get("protectionist_tendency", 0.5)
        self.priority_sectors = strategy_params.get(
            "priority_sectors", ["agriculture", "manufacturing", "tourism", "natural_resources"]
        )
        self.response_parser = LLMResponseParser()
        
    def decide_action(self, state: SimulationState) -> EconomicAction:
        """
        Decide the next Indonesian economic action based on current simulation state.
        
        Args:
            state: Current simulation state
            
        Returns:
            An economic action representing Indonesia's trade policy
        """
        # Check what US and China are doing
        us_actions = [
            action for action in state.recent_actions 
            if action.country.name == "US" and action.target_country
        ]
        china_actions = [
            action for action in state.recent_actions 
            if action.country.name == "China" and action.target_country
        ]
        
        # If using LLM for decision making
        if self.llm_client:
            prompt = generate_indonesia_policy_prompt(state, self.country, self.previous_actions)
            llm_response = self.llm_client.generate_response(prompt)
            if llm_response.startswith("ERROR:"):
                return self._decide_without_llm(state)
            action = self._parse_llm_response(llm_response, state)
            if action is None:
                return self._decide_without_llm(state)
            return action

        return self._decide_without_llm(state)

    def _decide_without_llm(self, state: SimulationState) -> EconomicAction:
        """Rule-based fallback behavior when LLM is unavailable."""
        # Check what US and China are doing
        us_actions = [
            action for action in state.recent_actions
            if action.country.name == "US" and action.target_country
        ]
        china_actions = [
            action for action in state.recent_actions
            if action.country.name == "China" and action.target_country
        ]

        # Observe US-China trade tensions and try to benefit
        if us_actions and china_actions:
            if us_actions[-1].target_country.name == "China" and china_actions[-1].target_country.name == "US":
                # US and China are in conflict - opportunity for Indonesia
                return EconomicAction(
                    country=self.country,
                    action_type=ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
                    target_country=Country(name="US"),
                    sectors=self.priority_sectors[:2],  # Focus on top priority sectors
                    magnitude=0.15,  # 15% investment increase
                    justification="Leveraging US-China trade tensions to boost domestic industries"
                )
        
        # Protect domestic industries with moderate tariffs if economy is struggling
        indicators = state.economic_indicators.get(self.country.name, [])
        if indicators and indicators[-1].gdp_growth < 0.015:  # Growth below 1.5%
            return EconomicAction(
                country=self.country,
                action_type=ActionType.TARIFF_INCREASE,
                target_country=None,  # Apply to all trading partners
                sectors=self.priority_sectors,
                magnitude=0.1 * self.protectionist_tendency,  # 5-10% tariffs depending on tendency
                justification="Protecting domestic industries during economic slowdown"
            )
        
        # Default: Focus on economic development through investment
        return EconomicAction(
            country=self.country,
            action_type=ActionType.GREEN_TECH_INVESTMENT,
            target_country=None,
            sectors=self.priority_sectors,
            magnitude=0.08,  # 8% investment increase
            justification="Continuing focus on economic development and domestic growth"
        )
    
    def calculate_tariff_policy(
        self, state: SimulationState, target_country: Country
    ) -> TariffPolicy:
        """
        Calculate Indonesia's tariff policy toward a target country.
        
        Args:
            state: Current simulation state
            target_country: Country to set tariffs against
            
        Returns:
            Indonesia's tariff policy specifying rates for different sectors
        """
        base_rate = 0.07  # 7% base tariff rate
        sector_rates = {}
        
        # Apply differentiated tariffs based on sectors
        for sector in self.priority_sectors:
            # Higher tariffs on priority sectors for protection
            sector_rates[sector] = base_rate * (1 + self.protectionist_tendency)
        
        # Lower tariffs on other sectors
        for sector in ["technology", "healthcare", "education"]:
            sector_rates[sector] = base_rate * 0.6
        
        # Special case for China and US
        if target_country.name in ["China", "US"]:
            # Check if they have tariffs against Indonesia
            their_policies = state.get_active_tariff_policies(
                target_country, self.country
            )
            
            if their_policies:
                # Slightly increase tariffs in response, but avoid escalation
                for sector, rate in sector_rates.items():
                    sector_rates[sector] = min(rate * 1.25, 0.2)  # Cap at 20%
        
        return TariffPolicy(
            source_country=self.country,
            target_country=target_country,
            sector_rates=sector_rates,
            duration_quarters=4  # 1 year
        )
    
    def _parse_llm_response(self, llm_response: str, state: SimulationState) -> Optional[EconomicAction]:
        """Parse LLM response into an economic action."""
        return self.response_parser.parse_action_response(llm_response, self.country, state)
