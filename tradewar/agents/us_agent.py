"""US-specific agent implementation for trade war simulation."""

from typing import Dict, Optional

from tradewar.agents.base_agent import BaseAgent
from tradewar.economics.models import ActionType, Country, EconomicAction, TariffPolicy
from tradewar.llm.client import LLMClient
from tradewar.llm.parser import LLMResponseParser
from tradewar.llm.prompts.us_trump_policy import generate_us_policy_prompt
from tradewar.simulation.state import SimulationState


class USAgent(BaseAgent):
    """
    Agent representing the United States in the trade war simulation.
    
    This agent models US trade policy with a focus on America First policies,
    manufacturing sector protection, and trade deficit reduction.
    """
    
    def __init__(
        self, 
        country: Country, 
        strategy_params: Optional[Dict] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the US agent.
        
        Args:
            country: The US country object
            strategy_params: Parameters to customize US policy strategy
            llm_client: Optional LLM client for policy generation
        """
        strategy_params = strategy_params or {}
        super().__init__(country, strategy_params)
        self.llm_client = llm_client
        self.is_aggressive = strategy_params.get("is_aggressive", True)
        self.focus_sectors = strategy_params.get(
            "focus_sectors", ["technology", "manufacturing", "agriculture"]
        )
        self.response_parser = LLMResponseParser()
        
    def decide_action(self, state: SimulationState) -> EconomicAction:
        """
        Decide the next US economic action based on current simulation state.
        
        Args:
            state: Current simulation state
            
        Returns:
            An economic action representing US trade policy
        """
        # If using LLM for decision making
        if self.llm_client:
            prompt = generate_us_policy_prompt(state, self.country, self.previous_actions)
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
        china_deficit = state.get_trade_balance(self.country, Country(name="China"))

        if china_deficit < -0.05:
            # Increase tariffs on Chinese goods if deficit is large
            return EconomicAction(
                country=self.country,
                action_type=ActionType.TARIFF_INCREASE,
                target_country=Country(name="China"),
                sectors=self.focus_sectors,
                magnitude=0.25,  # 25% tariff
                justification="Addressing trade imbalance and protecting US industries"
            )

        if any(action.country.name == "China" and action.action_type == ActionType.TARIFF_INCREASE for action in state.recent_actions):
            return EconomicAction(
                country=self.country,
                action_type=ActionType.TECH_EXPORT_CONTROL,
                target_country=Country(name="China"),
                sectors=["technology", "semiconductors", "ai"],
                magnitude=0.2,
                justification="Restricting advanced technology exports under strategic competition"
            )
        
        return EconomicAction(
            country=self.country,
            action_type=ActionType.FRIEND_SHORING,
            target_country=Country(name="Indonesia"),
            sectors=["manufacturing", "technology"],
            magnitude=0.1,
            justification="Diversifying supply chains toward trusted partners"
        )
    
    def calculate_tariff_policy(
        self, state: SimulationState, target_country: Country
    ) -> TariffPolicy:
        """
        Calculate US tariff policy toward a target country.
        
        Args:
            state: Current simulation state
            target_country: Country to set tariffs against
            
        Returns:
            US tariff policy specifying rates for different sectors
        """
        base_rate = 0.05  # 5% base tariff
        
        if target_country.name == "China":
            if self.is_aggressive:
                # Higher tariffs on Chinese goods in key sectors
                return TariffPolicy(
                    source_country=self.country,
                    target_country=target_country,
                    sector_rates={
                        "technology": 0.25,
                        "manufacturing": 0.25,
                        "agriculture": 0.10,
                        "raw_materials": 0.05,
                        "services": 0.05,
                    },
                    duration_quarters=4  # 1 year
                )
        
        # Default policy for other countries
        return TariffPolicy(
            source_country=self.country,
            target_country=target_country,
            sector_rates={sector: base_rate for sector in self.focus_sectors},
            duration_quarters=4
        )
    
    def _parse_llm_response(self, llm_response: str, state: SimulationState) -> Optional[EconomicAction]:
        """Parse LLM response into an economic action."""
        return self.response_parser.parse_action_response(llm_response, self.country, state)
