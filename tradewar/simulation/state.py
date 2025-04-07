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
    
    def __post_init__(self):
        """Initialize dictionaries for each country."""
        for country in self.countries:
            if country.name not in self.economic_indicators:
                self.economic_indicators[country.name] = []
    
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
    
    def add_events(self, events: List[EventConfig]) -> None:
        """
        Add external events to the simulation.
        
        Args:
            events: List of events to add
        """
        self.active_events.extend(events)
    
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
        # Placeholder implementation
        return 0.02  # 2% base growth rate
    
    def _calculate_inflation(self, country: Country) -> float:
        """Calculate inflation rate for a country."""
        # Placeholder implementation
        return 0.025  # 2.5% base inflation rate
    
    def _calculate_unemployment(self, country: Country) -> float:
        """Calculate unemployment rate for a country."""
        # Placeholder implementation
        return 0.05  # 5% base unemployment rate
    
    def _calculate_trade_balances(self, country: Country) -> Dict[str, float]:
        """Calculate trade balances with all partners."""
        balances = {}
        for partner in self.countries:
            if partner.name != country.name:
                balances[partner.name] = self.get_trade_balance(country, partner)
        return balances
    
    def _calculate_consumer_confidence(self, country: Country) -> float:
        """Calculate consumer confidence index."""
        # Placeholder implementation
        return 100.0  # Base confidence index
    
    def _calculate_business_confidence(self, country: Country) -> float:
        """Calculate business confidence index."""
        # Placeholder implementation
        return 100.0  # Base confidence index
    
    def _remove_expired_items(self) -> None:
        """Remove expired policies and events based on their duration."""
        # Implementation would check durations and remove as needed
        pass
    
    def clone(self) -> "SimulationState":
        """
        Create a deep copy of the current state.
        
        Returns:
            A copy of the current simulation state
        """
        return copy.deepcopy(self)
