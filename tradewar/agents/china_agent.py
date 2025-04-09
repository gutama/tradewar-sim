"""China-specific agent implementation for trade war simulation."""

from typing import Dict, Optional

from tradewar.agents.base_agent import BaseAgent
from tradewar.economics.models import Country, EconomicAction, TariffPolicy
from tradewar.llm.client import LLMClient
from tradewar.llm.prompts.china_policy import generate_china_policy_prompt
from tradewar.simulation.state import SimulationState


class ChinaAgent(BaseAgent):
    """
    Agent representing China in the trade war simulation.
    
    Models China's trade policy with focus on export growth, strategic sectors,
    and responsive retaliatory measures.
    """
    
    def __init__(
        self, 
        country: Country, 
        strategy_params: Optional[Dict] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize the China agent.
        
        Args:
            country: The China country object
            strategy_params: Parameters to customize China's policy strategy
            llm_client: Optional LLM client for policy generation
        """
        strategy_params = strategy_params or {}
        super().__init__(country, strategy_params)
        self.llm_client = llm_client
        self.retaliatory_factor = strategy_params.get("retaliatory_factor", 1.0)
        self.strategic_sectors = strategy_params.get(
            "strategic_sectors", ["technology", "manufacturing", "rare_earth_minerals"]
        )
        
    def decide_action(self, state: SimulationState) -> EconomicAction:
        """
        Decide the next Chinese economic action based on current simulation state.
        
        Args:
            state: Current simulation state
            
        Returns:
            An economic action representing China's trade policy
        """
        # Check recent actions from US
        us_actions = [
            action for action in state.recent_actions 
            if action.country.name == "US" and action.target_country and 
            action.target_country.name == "China"
        ]
        
        # If using LLM for decision making
        if self.llm_client:
            prompt = generate_china_policy_prompt(state, self.country, self.previous_actions)
            llm_response = self.llm_client.generate_response(prompt)
            action = self._parse_llm_response(llm_response, state)
            return action
        
        # Default rule-based behavior if no LLM
        if us_actions and us_actions[-1].action_type == "tariff_increase":
            # Retaliate proportionally to US tariff increases
            us_action = us_actions[-1]
            return EconomicAction(
                country=self.country,
                action_type="tariff_increase",
                target_country=Country(name="US"),
                sectors=us_action.sectors,
                magnitude=us_action.magnitude * self.retaliatory_factor,
                justification="Reciprocal measures in response to US tariffs"
            )
        
        # If no recent provocations, focus on strategic sectors
        return EconomicAction(
            country=self.country,
            action_type="investment",
            target_country=None,
            sectors=self.strategic_sectors,
            magnitude=0.1,  # 10% investment increase
            justification="Strategic sector development"
        )
    
    def calculate_tariff_policy(
        self, state: SimulationState, target_country: Country
    ) -> TariffPolicy:
        """
        Calculate China's tariff policy toward a target country.
        
        Args:
            state: Current simulation state
            target_country: Country to set tariffs against
            
        Returns:
            China's tariff policy specifying rates for different sectors
        """
        base_rate = 0.05  # 5% base tariff
        
        if target_country.name == "US":
            # Check if there are active US tariffs against China
            us_policies = state.get_active_tariff_policies(
                Country(name="US"), self.country
            )
            
            if us_policies:
                # Mirror US tariff policies with adjustment based on retaliatory factor
                us_policy = us_policies[0]
                mirrored_rates = {
                    sector: rate * self.retaliatory_factor
                    for sector, rate in us_policy.sector_rates.items()
                }
                
                return TariffPolicy(
                    source_country=self.country,
                    target_country=target_country,
                    sector_rates=mirrored_rates,
                    duration_quarters=us_policy.duration_quarters
                )
        
        # Default policy for other countries
        return TariffPolicy(
            source_country=self.country,
            target_country=target_country,
            sector_rates={sector: base_rate for sector in self.strategic_sectors},
            duration_quarters=4
        )
    
    def _parse_llm_response(self, llm_response: str, state: SimulationState) -> EconomicAction:
        """Parse LLM response into an economic action."""
        # Simplified placeholder implementation
        return EconomicAction(
            country=self.country,
            action_type="tariff_adjustment",
            target_country=Country(name="US"),
            sectors=self.strategic_sectors,
            magnitude=0.15,
            justification="LLM-generated policy decision"
        )
