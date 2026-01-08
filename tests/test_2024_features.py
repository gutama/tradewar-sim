"""Tests for new 2024-2026 trade war features."""

import pytest
from tradewar.economics.models import (
    ActionType,
    Country,
    EconomicAction,
    EventConfig,
)
from tradewar.simulation.events import EventGenerator
from tradewar.simulation.state import SimulationState


class TestNewActionTypes:
    """Test new action types added for modern trade dynamics."""

    def test_tech_export_control_action_type_exists(self):
        """Test that tech export control action type is available."""
        assert ActionType.TECH_EXPORT_CONTROL == "tech_export_control"

    def test_industrial_subsidy_action_type_exists(self):
        """Test that industrial subsidy action type is available."""
        assert ActionType.INDUSTRIAL_SUBSIDY == "industrial_subsidy"

    def test_supply_chain_diversification_action_type_exists(self):
        """Test that supply chain diversification action type is available."""
        assert ActionType.SUPPLY_CHAIN_DIVERSIFICATION == "supply_chain_diversification"

    def test_green_tech_investment_action_type_exists(self):
        """Test that green tech investment action type is available."""
        assert ActionType.GREEN_TECH_INVESTMENT == "green_tech_investment"

    def test_friend_shoring_action_type_exists(self):
        """Test that friend shoring action type is available."""
        assert ActionType.FRIEND_SHORING == "friend_shoring"

    def test_data_sovereignty_action_type_exists(self):
        """Test that data sovereignty action type is available."""
        assert ActionType.DATA_SOVEREIGNTY == "data_sovereignty"

    def test_create_tech_export_control_action(self):
        """Test creating a tech export control action."""
        us = Country(name="US", gdp=25.0)
        china = Country(name="China", gdp=17.0)

        action = EconomicAction(
            country=us,
            action_type=ActionType.TECH_EXPORT_CONTROL,
            target_country=china,
            sectors=["semiconductors", "ai"],
            magnitude=0.9,
            justification="Restricting advanced chip exports for national security",
        )

        assert action.action_type == ActionType.TECH_EXPORT_CONTROL
        assert action.target_country == china
        assert "semiconductors" in action.sectors
        assert "ai" in action.sectors
        assert action.magnitude == 0.9

    def test_create_green_tech_investment_action(self):
        """Test creating a green tech investment action."""
        china = Country(name="China", gdp=17.0)

        action = EconomicAction(
            country=china,
            action_type=ActionType.GREEN_TECH_INVESTMENT,
            sectors=["batteries", "green_tech", "automotive"],
            magnitude=0.5,
            justification="Massive subsidies for EV manufacturing",
        )

        assert action.action_type == ActionType.GREEN_TECH_INVESTMENT
        assert "batteries" in action.sectors
        assert "green_tech" in action.sectors
        assert action.magnitude == 0.5

    def test_create_supply_chain_diversification_action(self):
        """Test creating a supply chain diversification action."""
        us = Country(name="US", gdp=25.0)
        indonesia = Country(name="Indonesia", gdp=1.1)

        action = EconomicAction(
            country=us,
            action_type=ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
            target_country=indonesia,
            sectors=["electronics", "manufacturing"],
            magnitude=0.3,
            justification="China+1 strategy implementation",
        )

        assert action.action_type == ActionType.SUPPLY_CHAIN_DIVERSIFICATION
        assert action.target_country == indonesia
        assert "electronics" in action.sectors


class TestNewEvents:
    """Test new events added for 2024-2026 era."""

    def test_semiconductor_shortage_event_exists(self):
        """Test that semiconductor shortage event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        semiconductor_events = [
            e for e in events if "Semiconductor" in e.name
        ]
        assert len(semiconductor_events) > 0

        event = semiconductor_events[0]
        assert "semiconductors" in event.affected_sectors

    def test_ai_breakthrough_event_exists(self):
        """Test that AI breakthrough event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        ai_events = [e for e in events if "AI" in e.name]
        assert len(ai_events) > 0

        event = ai_events[0]
        assert "ai" in event.affected_sectors or "technology" in event.affected_sectors

    def test_ev_market_disruption_event_exists(self):
        """Test that EV market disruption event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        ev_events = [e for e in events if "Electric Vehicle" in e.name or "EV" in e.name]
        assert len(ev_events) > 0

    def test_rare_earth_crisis_event_exists(self):
        """Test that rare earth crisis event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        mineral_events = [e for e in events if "Rare Earth" in e.name or "Minerals" in e.name]
        assert len(mineral_events) > 0

    def test_cyber_attack_event_exists(self):
        """Test that cyber attack event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        cyber_events = [e for e in events if "Cyber" in e.name]
        assert len(cyber_events) > 0

    def test_green_tech_subsidy_event_exists(self):
        """Test that green tech subsidy event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        green_events = [
            e for e in events if "Green Technology" in e.name or "Green Tech" in e.name
        ]
        assert len(green_events) > 0

    def test_nearshoring_event_exists(self):
        """Test that nearshoring event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        nearshoring_events = [e for e in events if "Nearshoring" in e.name]
        assert len(nearshoring_events) > 0

    def test_regional_trade_agreement_event_exists(self):
        """Test that regional trade agreement event is created."""
        generator = EventGenerator(seed=42)
        events = generator.predefined_events

        trade_agreement_events = [
            e for e in events if "Regional Trade Agreement" in e.name
        ]
        assert len(trade_agreement_events) > 0


class TestModernSectors:
    """Test handling of modern sectors in actions and events."""

    def test_semiconductor_sector_in_action(self):
        """Test that semiconductor sector can be used in actions."""
        china = Country(name="China", gdp=17.0)

        action = EconomicAction(
            country=china,
            action_type=ActionType.INDUSTRIAL_SUBSIDY,
            sectors=["semiconductors"],
            magnitude=0.6,
            justification="Subsidizing domestic chip production",
        )

        assert "semiconductors" in action.sectors

    def test_green_tech_sector_in_action(self):
        """Test that green tech sector can be used in actions."""
        us = Country(name="US", gdp=25.0)

        action = EconomicAction(
            country=us,
            action_type=ActionType.GREEN_TECH_INVESTMENT,
            sectors=["green_tech", "batteries"],
            magnitude=0.4,
            justification="IRA subsidies for clean energy",
        )

        assert "green_tech" in action.sectors
        assert "batteries" in action.sectors

    def test_rare_earths_sector_in_action(self):
        """Test that rare earths sector can be used in actions."""
        china = Country(name="China", gdp=17.0)
        us = Country(name="US", gdp=25.0)

        action = EconomicAction(
            country=china,
            action_type=ActionType.TECH_EXPORT_CONTROL,
            target_country=us,
            sectors=["rare_earths"],
            magnitude=0.7,
            justification="Restricting rare earth exports as retaliation",
        )

        assert "rare_earths" in action.sectors


class TestEventGeneration:
    """Test that new events can be generated during simulation."""

    def test_events_can_be_generated(self):
        """Test that event generator can produce new events."""
        generator = EventGenerator(seed=123)
        
        countries = [
            Country(name="US", gdp=25.0),
            Country(name="China", gdp=17.0),
            Country(name="Indonesia", gdp=1.1),
        ]
        state = SimulationState(countries=countries)

        # Generate events for multiple quarters to test randomness
        all_events = []
        for year in range(1, 6):
            for quarter in range(1, 5):
                events = generator.generate_events(state, year, quarter)
                all_events.extend(events)

        # Should have generated at least some events
        assert len(all_events) > 0

    def test_modern_events_have_correct_sectors(self):
        """Test that modern events reference appropriate sectors."""
        generator = EventGenerator(seed=42)
        
        modern_sector_events = [
            e for e in generator.predefined_events
            if any(
                sector in e.affected_sectors
                for sector in ["semiconductors", "ai", "green_tech", "batteries", "rare_earths"]
            )
        ]

        # Should have several events with modern sectors
        assert len(modern_sector_events) >= 5


class TestSimulationStateWithNewActions:
    """Test that simulation state handles new action types correctly."""

    def test_state_can_store_new_action_types(self):
        """Test that simulation state can store new action types."""
        countries = [
            Country(name="US", gdp=25.0),
            Country(name="China", gdp=17.0),
        ]
        state = SimulationState(countries=countries)

        action = EconomicAction(
            country=countries[0],
            action_type=ActionType.TECH_EXPORT_CONTROL,
            target_country=countries[1],
            sectors=["semiconductors"],
            magnitude=0.8,
            justification="Export controls on advanced chips",
        )

        state.add_action(action)

        assert len(state.recent_actions) == 1
        assert state.recent_actions[0].action_type == ActionType.TECH_EXPORT_CONTROL

    def test_state_can_store_multiple_new_action_types(self):
        """Test that state can store various new action types."""
        countries = [
            Country(name="US", gdp=25.0),
            Country(name="China", gdp=17.0),
            Country(name="Indonesia", gdp=1.1),
        ]
        state = SimulationState(countries=countries)

        actions = [
            EconomicAction(
                country=countries[0],
                action_type=ActionType.TECH_EXPORT_CONTROL,
                target_country=countries[1],
                sectors=["semiconductors"],
                magnitude=0.8,
                justification="Export controls",
            ),
            EconomicAction(
                country=countries[1],
                action_type=ActionType.GREEN_TECH_INVESTMENT,
                sectors=["batteries", "green_tech"],
                magnitude=0.5,
                justification="EV subsidies",
            ),
            EconomicAction(
                country=countries[2],
                action_type=ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
                sectors=["electronics"],
                magnitude=0.3,
                justification="Attracting manufacturing",
            ),
        ]

        for action in actions:
            state.add_action(action)

        assert len(state.recent_actions) == 3
        assert ActionType.TECH_EXPORT_CONTROL in [a.action_type for a in state.recent_actions]
        assert ActionType.GREEN_TECH_INVESTMENT in [a.action_type for a in state.recent_actions]
        assert ActionType.SUPPLY_CHAIN_DIVERSIFICATION in [a.action_type for a in state.recent_actions]
