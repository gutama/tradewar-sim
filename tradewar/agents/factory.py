"""Agent factory for creating country-specific agent instances."""

from typing import Dict, Optional, Type

from tradewar.agents.base_agent import BaseAgent
from tradewar.agents.china_agent import ChinaAgent
from tradewar.agents.indonesia_agent import IndonesiaAgent
from tradewar.agents.us_agent import USAgent
from tradewar.config import config
from tradewar.economics.models import Country
from tradewar.llm.client import LLMClient


class AgentFactory:
    """
    Factory class for creating appropriate agent instances for different countries.
    
    This class centralizes agent creation logic and allows for easy configuration
    of different agent types and parameters.
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the agent factory.
        
        Args:
            use_llm: Whether to use LLM for agent decision making
        """
        self.use_llm = use_llm
        self.llm_client = None
        
        if use_llm:
            self.llm_client = LLMClient(
                provider=config.llm.provider,
                api_key=config.llm.api_key,
                model=config.llm.model,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens
            )
        
        # Register country-specific agent classes
        self.agent_classes: Dict[str, Type[BaseAgent]] = {
            "US": USAgent,
            "China": ChinaAgent,
            "Indonesia": IndonesiaAgent,
        }
        
        # Default strategy parameters for each country
        self.default_strategies: Dict[str, Dict] = {
            "US": {
                "is_aggressive": True,
                "focus_sectors": ["technology", "manufacturing", "agriculture"]
            },
            "China": {
                "retaliatory_factor": 1.0,
                "strategic_sectors": ["technology", "manufacturing", "rare_earth_minerals"]
            },
            "Indonesia": {
                "protectionist_tendency": 0.5,
                "priority_sectors": ["agriculture", "manufacturing", "tourism", "natural_resources"]
            }
        }
    
    def create_agent(
        self, country: Country, strategy_params: Optional[Dict] = None
    ) -> BaseAgent:
        """
        Create an appropriate agent for the given country.
        
        Args:
            country: The country to create an agent for
            strategy_params: Optional custom strategy parameters
            
        Returns:
            A country-specific agent instance
            
        Raises:
            ValueError: If no agent class is registered for the country
        """
        agent_class = self.agent_classes.get(country.name)
        
        if not agent_class:
            # Default to a generic agent if no specific one exists
            # This could be expanded with a GenericAgent class
            raise ValueError(f"No agent class registered for country: {country.name}")
        
        # Merge default strategy with provided parameters
        merged_strategy = self.default_strategies.get(country.name, {}).copy()
        if strategy_params:
            merged_strategy.update(strategy_params)
        
        # Create and return the agent instance
        return agent_class(
            country=country,
            strategy_params=merged_strategy,
            llm_client=self.llm_client if self.use_llm else None
        )
