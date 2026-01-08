"""Economic models and data structures for the trade war simulation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


@dataclass
class Country:
    """Represents a country in the simulation."""
    
    name: str
    gdp: float = 0.0
    population: int = 0
    inflation_rate: float = 0.0
    unemployment_rate: float = 0.0
    interest_rate: float = 0.0
    currency_value: float = 1.0
    sectors: Dict[str, float] = field(default_factory=dict)
    trading_partners: Dict[str, float] = field(default_factory=dict)
    historical_gdp_growth: List[float] = field(default_factory=list)  # Add this field
    policy_characteristics: Dict[str, float] = field(default_factory=dict)  # Add this field
    
    def __eq__(self, other):
        if not isinstance(other, Country):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


class ActionType(str, Enum):
    """Types of economic actions a country can take."""
    
    TARIFF_INCREASE = "tariff_increase"
    TARIFF_DECREASE = "tariff_decrease"
    TARIFF_ADJUSTMENT = "tariff_adjustment"
    EXPORT_SUBSIDY = "export_subsidy"
    IMPORT_QUOTA = "import_quota"
    INVESTMENT = "investment"
    CURRENCY_DEVALUATION = "currency_devaluation"
    STATUS_QUO = "status_quo"
    # New action types based on 2024-2026 trade dynamics
    TECH_EXPORT_CONTROL = "tech_export_control"
    INDUSTRIAL_SUBSIDY = "industrial_subsidy"
    SUPPLY_CHAIN_DIVERSIFICATION = "supply_chain_diversification"
    GREEN_TECH_INVESTMENT = "green_tech_investment"
    FRIEND_SHORING = "friend_shoring"
    DATA_SOVEREIGNTY = "data_sovereignty"


@dataclass
class EconomicAction:
    """Represents an economic action taken by a country."""
    
    country: Country
    action_type: str
    sectors: List[str]
    magnitude: float
    justification: str
    timestamp: datetime = field(default_factory=datetime.now)
    target_country: Optional[Country] = None
    duration_quarters: int = 4


@dataclass
class TariffPolicy:
    """Represents a tariff policy between two countries."""
    
    source_country: Country
    target_country: Country
    sector_rates: Dict[str, float]
    duration_quarters: int
    start_date: datetime = field(default_factory=datetime.now)
    
    @property
    def end_date(self) -> datetime:
        """Calculate the end date based on duration."""
        # Rough approximation: 1 quarter = 90 days
        days = self.duration_quarters * 90
        return self.start_date.replace(
            day=self.start_date.day + days
        )


@dataclass
class TradeFlow:
    """Represents trade flows between two countries."""
    
    exporter: Country
    importer: Country
    year: int
    quarter: int
    sector_volumes: Dict[str, float]
    sector_values: Dict[str, float]
    
    @property
    def total_value(self) -> float:
        """Calculate the total value of trade flow."""
        return sum(self.sector_values.values())


@dataclass
class EconomicIndicator:
    """Represents an economic indicator for a country at a point in time."""
    
    country: Country
    year: int
    quarter: int
    gdp_growth: float
    inflation: float
    unemployment: float
    trade_balance: Dict[str, float]  # By trading partner
    consumer_confidence: float
    business_confidence: float
    currency_value: float


@dataclass
class EventConfig:
    """Configuration for an external event."""
    
    name: str
    probability: float
    affected_countries: Set[str]
    affected_sectors: Set[str]
    gdp_impact: Dict[str, float]
    duration_quarters: int
    description: str
