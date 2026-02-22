"""Tests for LLM interactions and response parsing."""

import pytest

from tradewar.economics.models import ActionType, Country
from tradewar.llm.client import LLMClient
from tradewar.llm.parser import LLMResponseParser
from tradewar.llm.prompts.base_prompt import (create_country_context,
                                            create_economic_context,
                                            create_simulation_context)


def test_llm_client_initialization():
    """Test that the LLM client initializes correctly."""
    # Arrange & Act
    client = LLMClient(
        provider="test_provider",
        api_key="test_key",
        model="test_model",
        temperature=0.5,
        max_tokens=100
    )
    
    # Assert
    assert client.provider == "test_provider"
    assert client.api_key == "test_key"
    assert client.model == "test_model"
    assert client.temperature == 0.5
    assert client.max_tokens == 100


def test_parser_extracts_action(mock_state):
    """Test that the parser extracts economic actions correctly."""
    # Arrange
    parser = LLMResponseParser()
    us = next(country for country in mock_state.countries if country.name == "US")
    
    test_response = """
    After analyzing the current economic situation, I recommend:
    
    ACTION: tariff_increase
    TARGET_COUNTRY: China
    SECTORS: technology, manufacturing
    MAGNITUDE: 25
    JUSTIFICATION: This tariff increase is necessary to address the trade deficit with China and protect critical US industries from unfair trade practices.
    EXPECTED_OUTCOMES: Reduced imports from China, protection for domestic industries, some consumer price increases.
    """
    
    # Act
    action = parser.parse_policy_action(test_response, us, mock_state)
    
    # Assert
    assert action is not None
    assert action.action_type == ActionType.TARIFF_INCREASE
    assert action.target_country.name == "China"
    assert "technology" in action.sectors
    assert "manufacturing" in action.sectors
    assert action.magnitude == 0.25  # Converted from 25%


def test_parser_extracts_impact_assessment():
    """Test that the parser extracts impact assessments correctly."""
    # Arrange
    parser = LLMResponseParser()
    
    test_response = """
    Economic Impact Assessment:
    
    GDP: +1.5%
    Inflation: -0.3%
    Unemployment: +0.2%
    Trade: -2.8%
    
    The positive GDP growth is likely due to increased domestic production.
    """
    
    # Act
    impacts = parser.parse_impact_assessment(test_response)
    
    # Assert
    assert impacts["gdp"] == 0.015
    assert impacts["inflation"] == -0.003
    assert impacts["unemployment"] == 0.002
    assert impacts["trade"] == -0.028


def test_parser_extracts_stability_assessment():
    """Test that the parser extracts stability assessments correctly."""
    # Arrange
    parser = LLMResponseParser()
    
    test_response = """
    STABILITY_SCORE: 0.75
    
    REASONING: The economy shows moderate stability with sustainable growth
    and manageable inflation. There are some minor trade tensions but overall
    the situation is well-controlled.
    """
    
    # Act
    score, reasoning = parser.parse_stability_assessment(test_response)
    
    # Assert
    assert score == 0.75
    assert "moderate stability" in reasoning


def test_create_simulation_context(mock_state):
    """Test that simulation context is created correctly."""
    # Act
    context = create_simulation_context(mock_state)
    
    # Assert
    assert isinstance(context, str)
    assert "SIMULATION CONTEXT" in context
    assert "Year:" in context
    assert "Quarter:" in context


def test_create_economic_context(mock_state):
    """Test that economic context is created correctly."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    
    # We need to add at least one economic indicator
    from tradewar.economics.models import EconomicIndicator
    
    indicator = EconomicIndicator(
        country=us,
        year=0,
        quarter=0,
        gdp_growth=0.02,
        inflation=0.025,
        unemployment=0.04,
        trade_balance={"China": -100, "Indonesia": 50},
        consumer_confidence=80,
        business_confidence=75,
        currency_value=1.0
    )
    mock_state.economic_indicators[us.name] = [indicator]
    
    # Act
    context = create_economic_context(mock_state, us)
    
    # Assert
    assert isinstance(context, str)
    assert f"ECONOMIC CONTEXT FOR {us.name}" in context
    assert "GDP:" in context
    assert "Trade balances:" in context


def test_create_country_context():
    """Test that country context is created correctly."""
    # Arrange
    us = Country(name="US", gdp=21.0)
    
    # Act
    context = create_country_context(us)
    
    # Assert
    assert isinstance(context, str)
    assert us.name in context
    assert "largest economy" in context.lower()  # US description should mention this
