"""Tests for the economic models and calculations."""

from datetime import datetime, timedelta

import pytest

from tradewar.economics.gdp import calculate_gdp_impact
from tradewar.economics.models import Country, EventConfig, TariffPolicy, TradeFlow
from tradewar.economics.tariff import calculate_tariff_impact, calculate_optimal_tariff
from tradewar.economics.trade_balance import update_trade_balance
from tradewar.simulation.engine import SimulationEngine


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


def test_trade_diversion_shifts_us_imports_toward_indonesia(mock_state):
    """Higher US tariffs on China should divert some import volume toward Indonesia."""
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")
    indonesia = next(country for country in mock_state.countries if country.name == "Indonesia")

    # Build deterministic baseline flows
    mock_state.trade_flows = []
    mock_state.year = 0
    mock_state.quarter = 1

    mock_state.trade_flows.append(
        TradeFlow(
            exporter=indonesia,
            importer=us,
            year=0,
            quarter=0,
            sector_volumes={"manufacturing": 100.0},
            sector_values={"manufacturing": 100.0},
        )
    )
    mock_state.trade_flows.append(
        TradeFlow(
            exporter=us,
            importer=indonesia,
            year=0,
            quarter=0,
            sector_volumes={"manufacturing": 30.0},
            sector_values={"manufacturing": 30.0},
        )
    )
    mock_state.trade_flows.append(
        TradeFlow(
            exporter=china,
            importer=us,
            year=0,
            quarter=0,
            sector_volumes={"manufacturing": 300.0},
            sector_values={"manufacturing": 300.0},
        )
    )

    # US applies a higher tariff to China than Indonesia in manufacturing
    mock_state.active_tariff_policies = [
        TariffPolicy(
            source_country=us,
            target_country=china,
            sector_rates={"manufacturing": 0.35},
            duration_quarters=4,
        ),
        TariffPolicy(
            source_country=us,
            target_country=indonesia,
            sector_rates={"manufacturing": 0.05},
            duration_quarters=4,
        ),
    ]

    update_trade_balance(mock_state, indonesia, us, year=0, quarter=1)

    latest_idn_to_us = max(
        (
            flow for flow in mock_state.trade_flows
            if flow.exporter.name == "Indonesia"
            and flow.importer.name == "US"
            and flow.year == 0
            and flow.quarter == 1
        ),
        key=lambda flow: (flow.year, flow.quarter),
    )

    assert latest_idn_to_us.sector_volumes["manufacturing"] > 100.0


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


def test_remove_expired_policies_and_events(mock_state):
    """Expired policies/events should be removed on finalize."""
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")

    old_policy = TariffPolicy(
        source_country=us,
        target_country=china,
        sector_rates={"technology": 0.2},
        duration_quarters=1,
        start_date=datetime.now() - timedelta(days=365),
    )
    old_event = EventConfig(
        name="Temporary Shock",
        probability=0.0,
        affected_countries={"US"},
        affected_sectors={"technology"},
        gdp_impact={"US": -0.01},
        duration_quarters=1,
        description="Short-lived shock",
    )

    mock_state.add_tariff_policy(old_policy)
    mock_state.add_events([old_event])
    mock_state.policy_start_steps[id(old_policy)] = 0
    mock_state.event_start_steps[id(old_event)] = 0

    mock_state.finalize_update(year=1, quarter=2)

    assert old_policy not in mock_state.active_tariff_policies
    assert old_event not in mock_state.active_events


def test_dynamic_indicators_move_with_shock(mock_state):
    """Inflation/confidence should move away from static defaults under tariff stress."""
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")

    shock_policy = TariffPolicy(
        source_country=china,
        target_country=us,
        sector_rates={"technology": 0.4, "manufacturing": 0.3},
        duration_quarters=4,
    )
    mock_state.add_tariff_policy(shock_policy)

    us.gdp *= 0.985
    mock_state.gdp_snapshots["US"].append((0, us.gdp / 0.985))
    mock_state.finalize_update(year=0, quarter=1)

    latest = mock_state.economic_indicators["US"][-1]
    assert latest.inflation != 0.025
    assert latest.consumer_confidence != 100.0


def test_zero_gdp_country_gdp_impact_no_crash(mock_state):
    """GDP impact calculation should handle zero GDP countries safely."""
    zero_country = Country(name="ZeroLand", gdp=0.0)
    mock_state.countries.append(zero_country)
    mock_state.economic_indicators[zero_country.name] = []

    growth_rate, factors = calculate_gdp_impact(mock_state, zero_country, 0, 0)

    assert isinstance(growth_rate, float)
    assert "baseline" in factors


def test_simulation_engine_rejects_empty_country_list():
    """SimulationEngine should fail fast with no countries."""
    with pytest.raises(ValueError):
        SimulationEngine(countries=[])


def test_negative_tariff_rates_are_handled(mock_state):
    """Tariff decrease (negative rates) should not produce invalid volume impacts."""
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")

    policy = TariffPolicy(
        source_country=us,
        target_country=china,
        sector_rates={"technology": -0.1, "manufacturing": -0.05},
        duration_quarters=2,
    )

    impact = calculate_tariff_impact(mock_state, policy, us, china)

    assert all(value >= 0 for value in impact.trade_volume_change.values())


def test_missing_sector_in_policy_is_skipped_gracefully(mock_state):
    """Trade updates should not fail when tariff policy includes sectors absent from flow."""
    us = next(country for country in mock_state.countries if country.name == "US")
    china = next(country for country in mock_state.countries if country.name == "China")

    mock_state.active_tariff_policies.append(
        TariffPolicy(
            source_country=us,
            target_country=china,
            sector_rates={"nonexistent_sector": 0.3},
            duration_quarters=2,
        )
    )

    before = len(mock_state.trade_flows)
    balance = update_trade_balance(mock_state, us, china, year=0, quarter=1)

    assert isinstance(balance, float)
    assert len(mock_state.trade_flows) > before
