"""Tests for the agent implementations in the trade war simulation."""

import pytest

from tradewar.agents.base_agent import BaseAgent
from tradewar.agents.china_agent import ChinaAgent
from tradewar.agents.factory import AgentFactory
from tradewar.agents.indonesia_agent import IndonesiaAgent
from tradewar.agents.us_agent import USAgent
from tradewar.economics.models import ActionType, Country, EconomicAction, TariffPolicy
from tradewar.simulation.state import SimulationState


def test_agent_factory_creates_correct_agents(mock_countries):
    """Test that the agent factory creates the correct agent types."""
    # Arrange
    factory = AgentFactory(use_llm=False)
    
    # Act
    us = next(country for country in mock_countries if country.name == "US")
    china = next(country for country in mock_countries if country.name == "China")
    indonesia = next(country for country in mock_countries if country.name == "Indonesia")
    
    us_agent = factory.create_agent(us)
    china_agent = factory.create_agent(china)
    indonesia_agent = factory.create_agent(indonesia)
    
    # Assert
    assert isinstance(us_agent, USAgent)
    assert isinstance(china_agent, ChinaAgent)
    assert isinstance(indonesia_agent, IndonesiaAgent)


def test_us_agent_decides_action(mock_state):
    """Test that the US agent can decide an action."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    agent = USAgent(country=us, strategy_params={"is_aggressive": True})
    
    # Act
    action = agent.decide_action(mock_state)
    
    # Assert
    assert isinstance(action, EconomicAction)
    assert action.country.name == "US"
    assert action.action_type in [
        ActionType.TARIFF_INCREASE,
        ActionType.TECH_EXPORT_CONTROL,
        ActionType.FRIEND_SHORING,
        ActionType.STATUS_QUO,
    ]


def test_china_agent_tariff_policy(mock_state):
    """Test that the China agent calculates correct tariff policies."""
    # Arrange
    china = next(country for country in mock_state.countries if country.name == "China")
    us = next(country for country in mock_state.countries if country.name == "US")
    agent = ChinaAgent(
        country=china, 
        strategy_params={"retaliatory_factor": 1.2}
    )
    
    # Act
    policy = agent.calculate_tariff_policy(mock_state, us)
    
    # Assert
    assert isinstance(policy, TariffPolicy)
    assert policy.source_country.name == "China"
    assert policy.target_country.name == "US"
    assert policy.duration_quarters > 0
    assert len(policy.sector_rates) > 0
    assert all(0 <= rate <= 1.0 for rate in policy.sector_rates.values())


def test_indonesia_agent_decides_action(mock_state):
    """Test that the Indonesia agent can decide an action."""
    # Arrange
    indonesia = next(country for country in mock_state.countries if country.name == "Indonesia")
    agent = IndonesiaAgent(
        country=indonesia, 
        strategy_params={"protectionist_tendency": 0.5}
    )
    
    # Act
    action = agent.decide_action(mock_state)
    
    # Assert
    assert isinstance(action, EconomicAction)
    assert action.country.name == "Indonesia"
    assert action.action_type in [
        ActionType.TARIFF_INCREASE,
        ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
        ActionType.GREEN_TECH_INVESTMENT,
        ActionType.STATUS_QUO,
    ]


def test_agent_records_actions(mock_state):
    """Test that agents record their actions."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    agent = USAgent(country=us)
    
    # Act
    action = agent.decide_action(mock_state)
    agent.record_action(action)
    
    # Assert
    assert len(agent.previous_actions) == 1
    assert agent.previous_actions[0] == action
