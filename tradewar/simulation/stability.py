"""Stability detection algorithms for the trade war simulation."""

import logging
import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from tradewar.economics.models import Country, EconomicAction
from tradewar.simulation.state import SimulationState

logger = logging.getLogger(__name__)


class StabilityAnalyzer:
    """
    Analyzes economic stability in the trade war simulation.
    
    This class provides methods to assess the stability of the global economic system
    as well as individual country economies based on various economic indicators,
    tariff levels, and trade patterns.
    """
    
    def __init__(self, threshold_params: Optional[Dict] = None):
        """
        Initialize the stability analyzer.
        
        Args:
            threshold_params: Optional parameters to customize stability thresholds
        """
        self.threshold_params = threshold_params or {}
        self.tariff_threshold = self.threshold_params.get("tariff_threshold", 0.25)
        self.volatility_threshold = self.threshold_params.get("volatility_threshold", 0.03)
        self.deficit_threshold = self.threshold_params.get("deficit_threshold", 0.1)
        self.previous_scores: Dict[str, List[float]] = {}
    
    def analyze_global_stability(self, state: SimulationState) -> Tuple[float, Dict]:
        """
        Analyze the stability of the global economic system.
        
        Args:
            state: Current simulation state
            
        Returns:
            Tuple of (stability score from 0-1, factors dictionary)
        """
        stability_factors = {}
        
        # 1. Analyze average tariff rates
        avg_tariff_score = self._analyze_tariff_levels(state)
        stability_factors["tariff_level"] = avg_tariff_score
        
        # 2. Check for retaliatory tariff cycles
        retaliation_score = self._detect_tariff_retaliation(state)
        stability_factors["retaliation"] = retaliation_score
        
        # 3. Evaluate trade imbalances
        imbalance_score = self._evaluate_trade_imbalances(state)
        stability_factors["trade_imbalance"] = imbalance_score
        
        # 4. Analyze economic indicator volatility
        volatility_score = self._analyze_indicator_volatility(state)
        stability_factors["economic_volatility"] = volatility_score
        
        # 5. Check for external shock events
        event_score = self._assess_external_events(state)
        stability_factors["external_events"] = event_score
        
        # Calculate weighted average stability score
        weights = {
            "tariff_level": 0.25,
            "retaliation": 0.25,
            "trade_imbalance": 0.20,
            "economic_volatility": 0.20,
            "external_events": 0.10,
        }
        
        stability_score = sum(
            score * weights[factor] for factor, score in stability_factors.items()
        )
        
        # Add a stability trend analysis
        stability_factors["trend"] = self._analyze_stability_trend(stability_score)
        
        return stability_score, stability_factors
    
    def analyze_country_stability(
        self, state: SimulationState, country: Country
    ) -> Tuple[float, Dict]:
        """
        Analyze the economic stability of an individual country.
        
        Args:
            state: Current simulation state
            country: The country to analyze
            
        Returns:
            Tuple of (stability score from 0-1, factors dictionary)
        """
        stability_factors = {}
        
        # 1. Analyze economic indicators
        indicators = state.economic_indicators.get(country.name, [])
        if not indicators:
            return 0.5, {"error": "No economic data available"}
        
        latest_indicator = indicators[-1]
        
        # GDP growth (higher is better)
        gdp_score = min(1.0, max(0.0, 0.5 + latest_indicator.gdp_growth * 10))
        stability_factors["gdp_growth"] = gdp_score
        
        # Inflation (closer to target is better)
        ideal_inflation = 0.02  # 2% is often considered ideal
        inflation_deviation = abs(latest_indicator.inflation - ideal_inflation)
        inflation_score = max(0.0, 1.0 - inflation_deviation * 10)
        stability_factors["inflation"] = inflation_score
        
        # Unemployment (lower is better)
        unemployment_score = max(0.0, 1.0 - latest_indicator.unemployment * 5)
        stability_factors["unemployment"] = unemployment_score
        
        # 2. Analyze incoming tariffs
        incoming_tariffs = [
            policy for policy in state.active_tariff_policies
            if policy.target_country.name == country.name
        ]
        
        if incoming_tariffs:
            avg_incoming_rate = sum(
                sum(policy.sector_rates.values()) / len(policy.sector_rates)
                for policy in incoming_tariffs
            ) / len(incoming_tariffs)
            
            tariff_impact_score = max(0.0, 1.0 - avg_incoming_rate * 2)
            stability_factors["tariff_impact"] = tariff_impact_score
        else:
            stability_factors["tariff_impact"] = 1.0
        
        # 3. Analyze trade balances
        trade_balances = latest_indicator.trade_balance
        if trade_balances:
            # Calculate trade balance as percentage of GDP
            total_trade_balance = sum(trade_balances.values())
            trade_balance_ratio = total_trade_balance / country.gdp
            
            # Large imbalances (positive or negative) can be destabilizing
            trade_balance_score = 1.0 - min(1.0, abs(trade_balance_ratio) / self.deficit_threshold)
            stability_factors["trade_balance"] = trade_balance_score
        else:
            stability_factors["trade_balance"] = 0.5
        
        # 4. Analyze confidence indicators
        confidence_score = (latest_indicator.consumer_confidence + 
                           latest_indicator.business_confidence) / 200.0
        stability_factors["confidence"] = confidence_score
        
        # Calculate weighted average stability score
        weights = {
            "gdp_growth": 0.25,
            "inflation": 0.15,
            "unemployment": 0.15,
            "tariff_impact": 0.20,
            "trade_balance": 0.15,
            "confidence": 0.10,
        }
        
        # Handle missing factors
        valid_weights = {k: v for k, v in weights.items() if k in stability_factors}
        weight_sum = sum(valid_weights.values())
        
        stability_score = sum(
            stability_factors[factor] * (valid_weights[factor] / weight_sum)
            for factor in valid_weights
        )
        
        return stability_score, stability_factors
    
    def _analyze_tariff_levels(self, state: SimulationState) -> float:
        """Analyze global tariff levels and their stability implications."""
        if not state.active_tariff_policies:
            return 1.0  # No tariffs = high stability
        
        # Calculate average tariff rate across all policies
        total_rate = 0.0
        rate_count = 0
        
        for policy in state.active_tariff_policies:
            for rate in policy.sector_rates.values():
                total_rate += rate
                rate_count += 1
        
        if rate_count == 0:
            return 1.0
        
        avg_rate = total_rate / rate_count
        
        # Higher tariffs lead to lower stability
        # Scale from 0-1 where 0 = high tariffs, 1 = low tariffs
        stability_score = max(0.0, 1.0 - (avg_rate / self.tariff_threshold))
        
        return stability_score
    
    def _detect_tariff_retaliation(self, state: SimulationState) -> float:
        """Detect retaliatory tariff cycles between countries."""
        if not state.active_tariff_policies or len(state.active_tariff_policies) < 2:
            return 1.0  # No retaliation detected
        
        # Count bilateral tariff pairs
        country_pairs = set()
        bilateral_pairs = set()
        
        for policy in state.active_tariff_policies:
            source = policy.source_country.name
            target = policy.target_country.name
            country_pairs.add((source, target))
            
            # Check if there's a corresponding policy in the opposite direction
            if any(p.source_country.name == target and 
                  p.target_country.name == source
                  for p in state.active_tariff_policies):
                bilateral_pairs.add(frozenset([source, target]))
        
        if not country_pairs:
            return 1.0
        
        # Calculate percentage of pairs that are retaliatory
        retaliation_ratio = len(bilateral_pairs) / (len(country_pairs) / 2)
        stability_score = max(0.0, 1.0 - retaliation_ratio)
        
        return stability_score
    
    def _evaluate_trade_imbalances(self, state: SimulationState) -> float:
        """Evaluate the severity of trade imbalances."""
        # Get the most recent economic indicators for all countries
        latest_indicators = {}
        for country_name, indicators in state.economic_indicators.items():
            if indicators:
                latest_indicators[country_name] = indicators[-1]
        
        if not latest_indicators:
            return 0.5  # Neutral score if no data
        
        # Calculate the average absolute trade imbalance as percentage of GDP
        imbalance_ratios = []
        for country_name, indicator in latest_indicators.items():
            country = next((c for c in state.countries if c.name == country_name), None)
            if not country or not indicator.trade_balance:
                continue
            
            total_balance = sum(indicator.trade_balance.values())
            gdp = country.gdp
            imbalance_ratio = abs(total_balance / gdp)
            imbalance_ratios.append(imbalance_ratio)
        
        if not imbalance_ratios:
            return 0.5
        
        avg_imbalance = sum(imbalance_ratios) / len(imbalance_ratios)
        
        # Higher imbalances lead to lower stability
        stability_score = max(0.0, 1.0 - (avg_imbalance / self.deficit_threshold))
        
        return stability_score
    
    def _analyze_indicator_volatility(self, state: SimulationState) -> float:
        """Analyze the volatility of key economic indicators."""
        volatility_scores = []
        
        for country_name, indicators in state.economic_indicators.items():
            if len(indicators) < 3:
                continue  # Need at least 3 points to measure volatility
            
            # Calculate volatility of GDP growth
            gdp_growth_values = [ind.gdp_growth for ind in indicators]
            gdp_volatility = np.std(gdp_growth_values) if len(gdp_growth_values) > 1 else 0
            
            # Calculate volatility of inflation
            inflation_values = [ind.inflation for ind in indicators]
            inflation_volatility = np.std(inflation_values) if len(inflation_values) > 1 else 0
            
            # Combine volatilities
            combined_volatility = (gdp_volatility + inflation_volatility) / 2
            
            # Higher volatility leads to lower stability
            country_score = max(0.0, 1.0 - (combined_volatility / self.volatility_threshold))
            volatility_scores.append(country_score)
        
        if not volatility_scores:
            return 0.5  # Neutral score if not enough data
        
        return sum(volatility_scores) / len(volatility_scores)
    
    def _assess_external_events(self, state: SimulationState) -> float:
        """Assess the impact of external events on stability."""
        if not state.active_events:
            return 1.0  # No events = high stability
        
        # Calculate average impact of active events
        total_impact = 0.0
        impact_count = 0
        
        for event in state.active_events:
            for country_impact in event.gdp_impact.values():
                total_impact += abs(country_impact)
                impact_count += 1
        
        if impact_count == 0:
            return 1.0
        
        avg_impact = total_impact / impact_count
        
        # Larger impacts lead to lower stability
        # Scale from 0-1 where 0 = large impacts, 1 = small impacts
        stability_score = max(0.0, 1.0 - (avg_impact / 0.02))  # 0.02 = 2% GDP impact threshold
        
        return stability_score
    
    def _analyze_stability_trend(self, current_score: float) -> str:
        """
        Analyze the trend in stability scores.
        
        Args:
            current_score: The current stability score
            
        Returns:
            String describing the trend: "improving", "stable", or "deteriorating"
        """
        global_scores = self.previous_scores.get("global", [])
        global_scores.append(current_score)
        
        # Keep only the last 5 scores
        if len(global_scores) > 5:
            global_scores = global_scores[-5:]
        
        self.previous_scores["global"] = global_scores
        
        if len(global_scores) < 3:
            return "insufficient data"
        
        # Calculate linear regression slope to determine trend
        x = np.arange(len(global_scores))
        y = np.array(global_scores)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "deteriorating"
        else:
            return "stable"
