"""API schemas (Pydantic models) for the trade war simulation API."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CountryData(BaseModel):
    """API schema for country data."""
    
    name: str
    gdp: float
    population: Optional[int] = None
    inflation_rate: float = 0.0
    unemployment_rate: float = 0.0
    interest_rate: Optional[float] = None
    currency_value: float = 1.0
    sectors: Optional[Dict[str, float]] = None


class EconomicActionData(BaseModel):
    """API schema for economic actions."""
    
    country: str
    action_type: str
    target_country: Optional[str] = None
    sectors: List[str] = []
    magnitude: float
    justification: str


class SimulationConfig(BaseModel):
    """API schema for simulation configuration."""
    
    years: int = Field(5, description="Number of years to simulate")
    steps_per_year: int = Field(4, description="Simulation steps per year")
    random_seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    countries: List[CountryData] = Field(..., description="Countries in simulation")
    initial_events: Optional[List[str]] = Field(None, description="Initial events to trigger")


class TariffPolicyData(BaseModel):
    """API schema for tariff policies."""
    
    source_country: str
    target_country: str
    sector_rates: Dict[str, float]
    duration_quarters: int


class TradeFlowData(BaseModel):
    """API schema for trade flows."""
    
    exporter: str
    importer: str
    year: int
    quarter: int
    total_value: float
    sectors: Dict[str, float] = {}


class SimulationState(BaseModel):
    """API schema for simulation state."""
    
    year: int
    quarter: int
    countries: List[CountryData]
    trade_flows: Optional[List[TradeFlowData]] = None
    recent_actions: Optional[List[EconomicActionData]] = None
    active_tariff_policies: Optional[List[TariffPolicyData]] = None


class EconomicTimeSeriesData(BaseModel):
    """API schema for time series economic data."""
    
    country: str
    metric: str
    times: List[str]
    values: List[float]


class SimulationResult(BaseModel):
    """API schema for simulation results."""
    
    simulation_id: str
    total_years: int
    current_year: int
    current_quarter: int
    countries: List[str]
    trade_balances: Optional[Dict[str, Dict[str, float]]] = None
    gdp_series: Optional[List[EconomicTimeSeriesData]] = None
    unemployment_series: Optional[List[EconomicTimeSeriesData]] = None
    inflation_series: Optional[List[EconomicTimeSeriesData]] = None
    currency_series: Optional[List[EconomicTimeSeriesData]] = None
