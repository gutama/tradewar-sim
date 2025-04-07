"""Tests for the economic models and calculations."""

import pytest

from tradewar.economics.gdp import calculate_gdp_impact
from tradewar.economics.models import Country, TariffPolicy
from tradewar.economics.tariff import calculate_tariff_impact, calculate_optimal_tariff
from tradewar.economics.trade_balance import update_trade_balance


def test_calculate_tariff_impact(mock_state):
    """Test that tariff impact calculation returns valid results."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")
    
    policy = TariffPolicy(
        source_country=us,
        target_country=china,
        sector_rates={"technology": 0.25, "manufacturing": 0.15},
        duration_quarters=4
    )
    
    # Act
    impact = calculate_tariff_impact(mock_state, policy, us, china)
    
    # Assert
    assert impact.exporter_gdp_impact <= 0  # Exporter (China) should lose
    assert len(impact.trade_volume_change) > 0
    assert len(impact.price_effects) > 0


def test_update_trade_balance(mock_state):
    """Test that trade balance updates correctly."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")
    
    initial_flows_count = len(mock_state.trade_flows)
    
    # Act
    balance = update_trade_balance(mock_state, us, china)
    
    # Assert
    assert isinstance(balance, float)
    assert len(mock_state.trade_flows) > initial_flows_count  # New flows should be added


def test_calculate_gdp_impact(mock_state):
    """Test that GDP impact calculation returns valid results."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    
    # Add some data to the state to make calculation possible
    # This is a simplification - in real usage, the state would have more data
    mock_state.year = 0
    mock_state.quarter = 1
    
    # Act
    growth_rate, factors = calculate_gdp_impact(mock_state, us, 0, 1)
    
    # Assert
    assert isinstance(growth_rate, float)
    assert isinstance(factors, dict)
    assert "baseline" in factors


def test_calculate_optimal_tariff(mock_state):
    """Test that optimal tariff calculation returns valid rates."""
    # Arrange
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")
    
    # Act
    optimal_rates = calculate_optimal_tariff(mock_state, us, china)
    
    # Assert
    assert isinstance(optimal_rates, dict)
    assert len(optimal_rates) > 0
    assert all(0 <= rate <= 1.0 for rate in optimal_rates.values())


def test_country_equality(mock_countries):
    """Test that country equality is based on name."""
    # Arrange
    country1 = Country(name="TestCountry", gdp=1.0)
    country2 = Country(name="TestCountry", gdp=2.0)  # Different GDP
    country3 = Country(name="OtherCountry", gdp=1.0)  # Same GDP, different name
    
    # Assert
    assert country1 == country2  # Same name should be equal
    assert country1 != country3  # Different names should not be equal
    
    # Test in collection
    countries_set = {country1, country3}
    assert len(countries_set) == 2
    
    # Adding country2 (same name as country1) shouldn't increase set size
    countries_set.add(country2)
    assert len(countries_set) == 2
