"""
Economics module for trade war simulation.

This module provides economic models and algorithms for calculating
trade impacts, tariff effects, and GDP changes in trade war scenarios.
"""

from tradewar.economics.gdp import calculate_gdp_impact
from tradewar.economics.models import (ActionType, Country, EconomicAction,
                                      EconomicIndicator, EventConfig,
                                      TariffPolicy, TradeFlow)
from tradewar.economics.tariff import calculate_tariff_impact, calculate_optimal_tariff
from tradewar.economics.trade_balance import update_trade_balance

__all__ = [
    "Country",
    "ActionType",
    "EconomicAction",
    "TariffPolicy",
    "TradeFlow",
    "EconomicIndicator",
    "EventConfig",
    "calculate_tariff_impact",
    "calculate_optimal_tariff",
    "update_trade_balance",
    "calculate_gdp_impact",
]
