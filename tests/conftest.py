"""Pytest fixtures for trade war simulation tests."""

import logging
import os
import random
from typing import Dict, List

import pytest

from tradewar.agents.factory import AgentFactory
from tradewar.economics.models import Country, EconomicAction, TariffPolicy, TradeFlow
from tradewar.llm.client import LLMClient
from tradewar.simulation.engine import SimulationEngine
from tradewar.simulation.state import SimulationState


@pytest.fixture
def mock_countries() -> List[Country]:
    """Create a list of mock countries for testing."""
    countries = [
        Country(
            name="US",
            gdp=28.8,
            population=330_000_000,
            inflation_rate=0.02,
            unemployment_rate=0.04,
            currency_value=1.0,
            sectors={
                "technology": 0.25,
                "services": 0.40,
                "manufacturing": 0.15,
                "agriculture": 0.02,
            }
        ),
        Country(
            name="China",
            gdp=17.8,
            population=1_400_000_000, 
            inflation_rate=0.025,
            unemployment_rate=0.05,
            currency_value=1.0,
            sectors={
                "manufacturing": 0.35,
                "technology": 0.15,
                "services": 0.25,
                "agriculture": 0.08,
            }
        ),
        Country(
            name="Indonesia",
            gdp=1.42,
            population=270_000_000,
            inflation_rate=0.03,
            unemployment_rate=0.06,
            currency_value=1.0,
            sectors={
                "agriculture": 0.15,
                "natural_resources": 0.25,
                "manufacturing": 0.20,
                "services": 0.30,
            }
        )
    ]
    return countries


@pytest.fixture
def mock_state(mock_countries: List[Country]) -> SimulationState:
    """Create a mock simulation state."""
    random.seed(42)
    state = SimulationState(countries=mock_countries)
    
    # Add some initial trade flows
    for exporter in mock_countries:
        for importer in mock_countries:
            if exporter != importer:
                # Create basic trade flow
                sectors = list(exporter.sectors.keys())[:3]  # Use first 3 sectors
                sector_volumes = {sector: random.uniform(0.1, 1.0) for sector in sectors}
                sector_values = {sector: vol * 1.1 for sector, vol in sector_volumes.items()}
                
                flow = TradeFlow(
                    exporter=exporter,
                    importer=importer,
                    year=0,
                    quarter=0,
                    sector_volumes=sector_volumes,
                    sector_values=sector_values
                )
                
                state.trade_flows.append(flow)
    
    # Add an initial tariff policy
    us = next(country for country in mock_countries if country.name == "US")
    china = next(country for country in mock_countries if country.name == "China")
    
    tariff_policy = TariffPolicy(
        source_country=us,
        target_country=china,
        sector_rates={"technology": 0.25, "manufacturing": 0.15},
        duration_quarters=4
    )
    state.active_tariff_policies.append(tariff_policy)
    
    # Initialize economic indicators for each country
    for country in mock_countries:
        state.economic_indicators[country.name] = []
    
    return state


@pytest.fixture
def mock_engine(mock_countries: List[Country]) -> SimulationEngine:
    """Create a mock simulation engine."""
    return SimulationEngine(countries=mock_countries)


@pytest.fixture
def mock_agent_factory() -> AgentFactory:
    """Create a mock agent factory that doesn't use real LLMs."""
    factory = AgentFactory(use_llm=False)
    return factory


@pytest.fixture
def disable_api_calls(monkeypatch):
    """
    Disable real API calls in tests by patching LLM client.
    
    This prevents accidental API usage during testing.
    """
    def mock_generate(*args, **kwargs):
        return "Mock LLM response for testing purposes."
    
    monkeypatch.setattr(LLMClient, "generate_response", mock_generate)
    return None


@pytest.fixture(autouse=True)
def suppress_logging():
    """Suppress verbose logging during tests."""
    logging.basicConfig(level=logging.ERROR)
