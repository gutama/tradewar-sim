"""
Data module for trade war simulation.

This module provides functionality for loading economic and trade data
needed for initializing and running trade war simulations.
"""

from tradewar.data.loaders import load_country_data, load_historical_trade_data

__all__ = ["load_country_data", "load_historical_trade_data"]
