"""Economic state tracking and updates for the trade war simulation."""

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from tradewar.economics.models import (Country, EconomicAction, EconomicIndicator,
                                      EventConfig, TariffPolicy, TradeFlow)


@dataclass
class TariffImpact:
    """Represents the calculated impact of a tariff policy."""
    
    policy: TariffPolicy
    exporter_gdp_impact: float
    importer_gdp_impact: float
    trade_volume_change: Dict[str, float]
    price_effects: Dict[str, float]


@dataclass
class SimulationState:
    """
    Represents the complete economic state of the simulation.
    
    This class tracks all economic variables, policies, and historical data
    throughout the simulation.
    """
    
    countries: List[Country]
    year: int = 0
    quarter: int = 0
    trade_flows: List[TradeFlow] = field(default_factory=list)
    economic_indicators: Dict[str, List[EconomicIndicator]] = field(default_factory=dict)
    active_tariff_policies: List[TariffPolicy] = field(default_factory=list)
    recent_actions: List[EconomicAction] = field(default_factory=list)
    all_actions: List[EconomicAction] = field(default_factory=list)
    active_events: List[EventConfig] = field(default_factory=list)
    policy_start_steps: Dict[int, int] = field(default_factory=dict)
    event_start_steps: Dict[int, int] = field(default_factory=dict)
    gdp_snapshots: Dict[str, List[Tuple[int, float]]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize dictionaries for each country."""
        for country in self.countries:
            if country.name not in self.economic_indicators:
                self.economic_indicators[country.name] = []
            if country.name not in self.gdp_snapshots:
                self.gdp_snapshots[country.name] = []
    
    def add_action(self, action: EconomicAction) -> None:
        """
        Add an economic action to the state.
        
        Args:
            action: The economic action to add
        """
        self.recent_actions.append(action)
        self.all_actions.append(action)
        
        # Keep recent actions to a reasonable size
        if len(self.recent_actions) > 10:
            self.recent_actions = self.recent_actions[-10:]
    
    def add_tariff_policy(self, policy: TariffPolicy) -> None:
        """
        Add a new tariff policy to the state.
        
        Args:
            policy: The tariff policy to add
        """
        self.active_tariff_policies.append(policy)
        self.policy_start_steps[id(policy)] = self.year * 4 + self.quarter
    
    def add_events(self, events: List[EventConfig]) -> None:
        """
        Add external events to the simulation.
        
        Args:
            events: List of events to add
        """
        for event in events:
            self.active_events.append(event)
            self.event_start_steps[id(event)] = self.year * 4 + self.quarter
    
    def apply_tariff_impact(self, impact: TariffImpact) -> None:
        """
        Apply the calculated impact of a tariff policy.
        
        Args:
            impact: The tariff impact to apply
        """
        exporter = impact.policy.target_country
        importer = impact.policy.source_country
        
        # Update country GDPs
        for country in self.countries:
            if country.name == exporter.name:
                country.gdp += impact.exporter_gdp_impact
            elif country.name == importer.name:
                country.gdp += impact.importer_gdp_impact
        
        # Update trade flows would happen here
    
    def get_trade_balance(self, country1: Country, country2: Country) -> float:
        """
        Calculate the trade balance between two countries.
        
        Args:
            country1: First country
            country2: Second country
            
        Returns:
            Trade balance from country1's perspective (+ is surplus, - is deficit)
        """
        exports = sum(
            flow.total_value for flow in self.trade_flows
            if flow.exporter.name == country1.name and flow.importer.name == country2.name
        )
        
        imports = sum(
            flow.total_value for flow in self.trade_flows
            if flow.exporter.name == country2.name and flow.importer.name == country1.name
        )
        
        return exports - imports
    
    def get_active_tariff_policies(
        self, source_country: Country, target_country: Country
    ) -> List[TariffPolicy]:
        """
        Get active tariff policies between two countries.
        
        Args:
            source_country: Country imposing the tariffs
            target_country: Country targeted by the tariffs
            
        Returns:
            List of active tariff policies
        """
        return [
            policy for policy in self.active_tariff_policies
            if policy.source_country.name == source_country.name and 
            policy.target_country.name == target_country.name
        ]
    
    def finalize_update(self, year: int, quarter: int) -> None:
        """
        Finalize the state update for the current time period.
        
        Args:
            year: Current simulation year
            quarter: Current simulation quarter
        """
        self.year = year
        self.quarter = quarter
        
        # Update economic indicators for each country
        for country in self.countries:
            indicator = EconomicIndicator(
                country=country,
                year=year,
                quarter=quarter,
                gdp_growth=self._calculate_gdp_growth(country),
                inflation=self._calculate_inflation(country),
                unemployment=self._calculate_unemployment(country),
                trade_balance=self._calculate_trade_balances(country),
                consumer_confidence=self._calculate_consumer_confidence(country),
                business_confidence=self._calculate_business_confidence(country),
                currency_value=country.currency_value
            )
            
            self.economic_indicators[country.name].append(indicator)
        
        # Clean up expired policies and events
        self._remove_expired_items()
    
    def _calculate_gdp_growth(self, country: Country) -> float:
        """Calculate GDP growth rate for a country."""
        current_step = self.year * 4 + self.quarter
        history = self.gdp_snapshots.get(country.name, [])
        previous_values = [gdp for step, gdp in history if step < current_step]
        if not previous_values:
            return 0.02
        previous_gdp = previous_values[-1]
        if previous_gdp <= 0:
            return 0.0
        return (country.gdp - previous_gdp) / previous_gdp
    
    def _calculate_inflation(self, country: Country) -> float:
        """Calculate inflation rate for a country."""
        base_inflation = 0.02
        # All policies targeting this country (tariffs imposed ON it raise domestic prices)
        incoming_policies = [
            policy for policy in self.active_tariff_policies
            if policy.target_country.name == country.name
        ]
        # All policies this country is imposing (raise input costs slightly)
        outgoing_policies = [
            policy for policy in self.active_tariff_policies
            if policy.source_country.name == country.name
        ]

        incoming_rates = [
            sum(policy.sector_rates.values()) / max(1, len(policy.sector_rates))
            for policy in incoming_policies
        ]
        outgoing_rates = [
            sum(policy.sector_rates.values()) / max(1, len(policy.sector_rates))
            for policy in outgoing_policies
        ]
        tariff_pressure = 0.0
        if incoming_rates:
            tariff_pressure += (sum(incoming_rates) / len(incoming_rates)) * 0.12
        if outgoing_rates:
            tariff_pressure += (sum(outgoing_rates) / len(outgoing_rates)) * 0.04

        growth = self._calculate_gdp_growth(country)
        demand_pressure = max(0.0, growth - 0.005) * 0.2
        return max(-0.02, min(0.2, base_inflation + tariff_pressure + demand_pressure))
    
    def _calculate_unemployment(self, country: Country) -> float:
        """Calculate unemployment rate for a country."""
        previous = self.economic_indicators.get(country.name, [])
        previous_unemployment = previous[-1].unemployment if previous else country.unemployment_rate or 0.05
        trend_growth = 0.005
        gdp_growth = self._calculate_gdp_growth(country)
        updated = previous_unemployment - 0.5 * (gdp_growth - trend_growth)
        return max(0.02, min(0.2, updated))
    
    def _calculate_trade_balances(self, country: Country) -> Dict[str, float]:
        """Calculate trade balances with all partners."""
        balances = {}
        for partner in self.countries:
            if partner.name != country.name:
                balances[partner.name] = self.get_trade_balance(country, partner)
        return balances
    
    def _calculate_consumer_confidence(self, country: Country) -> float:
        """Calculate consumer confidence index."""
        previous = self.economic_indicators.get(country.name, [])
        prev_conf = previous[-1].consumer_confidence if previous else 100.0
        inflation = self._calculate_inflation(country)
        unemployment = self._calculate_unemployment(country)
        gdp_growth = self._calculate_gdp_growth(country)

        delta = (gdp_growth * 180) - (abs(inflation - 0.02) * 220) - (max(0.0, unemployment - 0.05) * 140)
        return max(60.0, min(130.0, prev_conf + delta))
    
    def _calculate_business_confidence(self, country: Country) -> float:
        """Calculate business confidence index."""
        previous = self.economic_indicators.get(country.name, [])
        prev_conf = previous[-1].business_confidence if previous else 100.0
        gdp_growth = self._calculate_gdp_growth(country)

        trade_balances = self._calculate_trade_balances(country)
        trade_signal = sum(trade_balances.values())

        outgoing_policies = [
            policy for policy in self.active_tariff_policies
            if policy.source_country.name == country.name
        ]
        avg_tariff = 0.0
        if outgoing_policies:
            avg_tariff = sum(
                sum(policy.sector_rates.values()) / max(1, len(policy.sector_rates))
                for policy in outgoing_policies
            ) / len(outgoing_policies)

        delta = (gdp_growth * 200) + (trade_signal * 0.03) - (avg_tariff * 30)
        return max(60.0, min(130.0, prev_conf + delta))
    
    def _remove_expired_items(self) -> None:
        """Remove expired policies and events based on their duration."""
        current_step = self.year * 4 + self.quarter

        active_policies: List[TariffPolicy] = []
        for policy in self.active_tariff_policies:
            started = self.policy_start_steps.get(id(policy), current_step)
            if (current_step - started) < policy.duration_quarters:
                active_policies.append(policy)
            else:
                self.policy_start_steps.pop(id(policy), None)
        self.active_tariff_policies = active_policies

        active_events: List[EventConfig] = []
        for event in self.active_events:
            started = self.event_start_steps.get(id(event), current_step)
            if (current_step - started) < event.duration_quarters:
                active_events.append(event)
            else:
                self.event_start_steps.pop(id(event), None)
        self.active_events = active_events
    
    def clone(self) -> "SimulationState":
        """
        Create a deep copy of the current state.
        
        Returns:
            A copy of the current simulation state
        """
        current_step = self.year * 4 + self.quarter
        for country in self.countries:
            history = self.gdp_snapshots.setdefault(country.name, [])
            if not history or history[-1][0] != current_step:
                history.append((current_step, country.gdp))
        return copy.deepcopy(self)
