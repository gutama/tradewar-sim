# Examples

This directory contains example scripts demonstrating various features of the Trade War Simulation.

## Modern Trade Scenarios (2024-2026)

**File:** `modern_trade_scenarios.py`

Demonstrates the latest features added to the simulation to model current trade war dynamics:

### Scenario 1: US-China Technology Export Controls
- US imposes export controls on advanced semiconductors and AI chips
- China retaliates with rare earth export restrictions
- Models the strategic technology competition

### Scenario 2: Green Technology Subsidy Race
- US implements IRA-style green tech subsidies
- China counters with aggressive industrial subsidies
- Demonstrates competition in EVs, batteries, and clean energy

### Scenario 3: Indonesia Nearshoring Opportunity
- US friend-shoring initiative to Indonesia
- Indonesia positions itself as alternative manufacturing hub
- Leverages critical minerals for battery supply chains

### Running the Examples

```bash
python examples/modern_trade_scenarios.py
```

## Creating Your Own Scenarios

Use the examples as templates to create custom scenarios:

```python
from tradewar.economics.models import ActionType, Country, EconomicAction

# Create countries with 2024 baseline GDPs (trillions USD)
us = Country(name="US", gdp=28.8, population=335_000_000)
china = Country(name="China", gdp=17.8, population=1_400_000_000)
indonesia = Country(name="Indonesia", gdp=1.42, population=275_000_000)

# Create an action
action = EconomicAction(
    country=us,
    action_type=ActionType.TECH_EXPORT_CONTROL,
    target_country=china,
    sectors=["semiconductors"],
    magnitude=0.8,
    justification="Export controls for national security"
)

# Add to simulation
state.add_action(action)
```

## Available Action Types

All action types are strongly typed via the `ActionType` enum. See `TRADE_WAR_2024_UPDATES.md` for full documentation.

**Traditional actions:**
- `tariff_increase`, `tariff_decrease`, `tariff_adjustment`
- `import_quota` — applies a volume quota factor to import flows
- `export_subsidy`
- `currency_devaluation`

**Modern actions (2024-2026):**
- `tech_export_control` — restrict advanced technology exports
- `industrial_subsidy` — government manufacturing subsidies
- `supply_chain_diversification` — reduce single-country dependencies
- `green_tech_investment` — clean energy and EV investment
- `friend_shoring` — allied-country supply chain relocation
- `data_sovereignty` — digital infrastructure protection

**Available sectors:** `semiconductors`, `ai`, `green_tech`, `batteries`, `rare_earths`, `automotive`, `mining`, `digital_services`, `electronics`, `manufacturing`, and legacy sectors.

## Further Documentation

- [TRADE_WAR_2024_UPDATES.md](../TRADE_WAR_2024_UPDATES.md) - Detailed guide to 2024-2026 updates
- [README.md](../README.md) - General project overview
- [introduction.md](../introduction.md) - Technical documentation
