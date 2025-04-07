"""Tests for the simulation engine and related components."""

import pytest

from tradewar.agents.factory import AgentFactory
from tradewar.economics.models import Country, TradeFlow
from tradewar.simulation.engine import SimulationEngine
from tradewar.simulation.events import EventGenerator
from tradewar.simulation.stability import StabilityAnalyzer
from tradewar.simulation.state import SimulationState


def test_simulation_engine_initialization(mock_countries):
    """Test that the simulation engine initializes correctly."""
    # Act
    engine = SimulationEngine(countries=mock_countries)
    
    # Assert
    assert len(engine.countries) == len(mock_countries)
    assert len(engine.agents) == len(mock_countries)
    assert engine.current_year == 0
    assert engine.current_quarter == 0


def test_simulation_step_advances_time(mock_engine):
    """Test that stepping the simulation advances time correctly."""
    # Arrange
    initial_year = mock_engine.current_year
    initial_quarter = mock_engine.current_quarter
    
    # Act
    mock_engine.step()
    
    # Assert - Time should advance by one quarter
    if initial_quarter == 3:  # Quarter 0-3, so 3 is last quarter of year
        assert mock_engine.current_year == initial_year + 1
        assert mock_engine.current_quarter == 0
    else:
        assert mock_engine.current_year == initial_year
        assert mock_engine.current_quarter == initial_quarter + 1


def test_simulation_generates_trade_flows(mock_engine):
    """Test that simulation generates trade flows."""
    # Arrange
    initial_flows_count = len(mock_engine.state.trade_flows)
    
    # Act
    mock_engine.step()
    
    # Assert
    assert len(mock_engine.state.trade_flows) > initial_flows_count


def test_stability_analyzer(mock_state):
    """Test that the stability analyzer produces valid scores."""
    # Arrange
    analyzer = StabilityAnalyzer()
    
    # Act
    global_score, global_factors = analyzer.analyze_global_stability(mock_state)
    
    # Find a country for individual stability analysis
    us = next(country for country in mock_state.countries if country.name == "US")
    country_score, country_factors = analyzer.analyze_country_stability(mock_state, us)
    
    # Assert
    assert 0 <= global_score <= 1
    assert isinstance(global_factors, dict)
    assert 0 <= country_score <= 1
    assert isinstance(country_factors, dict)


def test_event_generator(mock_state):
    """Test that the event generator produces events."""
    # Arrange
    generator = EventGenerator(seed=42)
    
    # Act
    # Generate events for multiple time periods to increase chance of getting some
    events1 = generator.generate_events(mock_state, 0, 0)
    events2 = generator.generate_events(mock_state, 1, 0)
    events3 = generator.generate_events(mock_state, 2, 0)
    
    # Assert
    # At least one of the time periods should have generated events
    assert events1 or events2 or events3
    
    # If we got events, check they have required attributes
    if events1:
        event = events1[0]
        assert hasattr(event, 'name')
        assert hasattr(event, 'affected_countries')
        assert hasattr(event, 'gdp_impact')


def test_simulation_state_clone(mock_state):
    """Test that simulation state can be cloned correctly."""
    # Act
    clone = mock_state.clone()
    
    # Assert
    assert isinstance(clone, SimulationState)
    assert len(clone.countries) == len(mock_state.countries)
    assert len(clone.trade_flows) == len(mock_state.trade_flows)
    assert clone is not mock_state  # Different objects


def test_full_simulation_run(mock_countries):
    """Test running a full simulation."""
    # Arrange
    engine = SimulationEngine(countries=mock_countries)
    max_years = 2
    quarters_per_year = 4
    engine.max_years = max_years
    engine.quarters_per_year = quarters_per_year
    
    # Act
    history = engine.run_full_simulation()
    
    # Assert
    assert len(history) == max_years * quarters_per_year
    
    # Check that GDP changes over time
    initial_gdp = {country.name: country.gdp for country in mock_countries}
    final_gdp = {country.name: country.gdp for country in engine.countries}
    
    # At least one country's GDP should have changed
    assert any(abs(final_gdp[name] - initial_gdp[name]) > 0.001 for name in initial_gdp)
