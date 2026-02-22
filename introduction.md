# TradeWar Simulation - Technical Documentation

## Overview

TradeWar Sim is a sophisticated agent-based framework for simulating trade war dynamics between countries, with particular focus on US-China-Indonesia interactions. The system models economic impacts of trade policies, tariffs, and retaliatory measures using economic theory combined with AI-powered decision making.

## System Architecture

The simulation is built around several core components:

```
tradewar-sim/
├── tradewar/
│   ├── agents/         # Country-specific policy agents
│   ├── economics/      # Economic models and calculations
│   ├── simulation/     # Simulation engine and state management
│   ├── visualization/  # Data visualization components
│   ├── api/            # REST API for controlling simulation
│   ├── llm/            # LLM integration for policy decisions
│   └── data/           # Baseline economic data
```

## Core Components

### Simulation Engine

The `SimulationEngine` orchestrates the entire simulation:

1. Manages the simulation state
2. Coordinates agent decisions and actions
3. Processes economic impacts and updates
4. Handles external events
5. Advances the simulation over time

```python
# Main simulation loop
def step(self, year: int, quarter: int) -> SimulationState:
    # Get actions from all country agents
    actions = [agent.decide_action(self.state) for agent in self.agents.values()]
    
    # Apply economic actions to simulation state
    self._apply_actions(actions)
    
    # Update economic indicators based on actions and events
    self._update_economic_indicators()
    
    # Check for and apply any external events
    self._handle_events()
    
    # Update agent strategies
    for agent in self.agents.values():
        agent.update_strategy(self.state)
    
    return self.state
```

### Country Agents

Each country is represented by a specialized agent that determines trade policy actions:

- **USAgent**: Models US trade policy with focus on protectionism and deficit reduction
- **ChinaAgent**: Models China's trade policy with focus on export growth and retaliation
- **IndonesiaAgent**: Models Indonesia's policy, balancing relations with both powers

Each agent can:
1. Decide economic actions using **LLM-powered reasoning** or a deterministic **rule-based fallback**
2. Parse LLM responses into typed `EconomicAction` objects via `LLMResponseParser`
3. Calculate and apply tariff policies
4. Update their strategy based on evolving conditions

All action types are strongly typed via the `ActionType` enum (11 values):
- Traditional: `TARIFF_INCREASE`, `TARIFF_DECREASE`, `TARIFF_ADJUSTMENT`, `IMPORT_QUOTA`, `EXPORT_SUBSIDY`, `CURRENCY_DEVALUATION`
- Modern (2024-2026): `TECH_EXPORT_CONTROL`, `INDUSTRIAL_SUBSIDY`, `SUPPLY_CHAIN_DIVERSIFICATION`, `GREEN_TECH_INVESTMENT`, `FRIEND_SHORING`, `DATA_SOVEREIGNTY`

### Economic Models

The system implements several economic models:

1. **Tariff Impacts**: Price elasticity-based trade volume changes, tariff revenue, and deadweight loss
2. **GDP Impacts**: `calculate_gdp_impact()` called per-action per-country each step
3. **Trade Balances**: Bilateral flow tracking with trade-diversion logic for preferential agreements
4. **Dynamic Indicators**: GDP growth (snapshot diff), unemployment (Okun's law), inflation (tariff-adjusted), composite confidence
5. **Stability Analysis**: Country and global stability scores from multi-factor composite (0–1 scale)

### Simulation State

The `SimulationState` class tracks all economic variables, including:

- List of countries with economic indicators (GDP, inflation, unemployment, confidence)
- Current time (year and quarter)
- Trade flows between countries with sector-level volumes
- Active tariff policies (with step-based expiration via `_remove_expired_items()`)
- Recent economic actions
- Active external events
- GDP snapshots for growth-rate calculations

### Event System

The simulation includes an `EventGenerator` that creates random or scheduled external events such as:
- Economic recessions
- Supply chain disruptions
- Natural disasters
- Presidential elections
- Global pandemics

These events affect economic indicators across countries and are governed by typed `EventConfig` objects with `trigger_time`, `one_time`, and sector fields.

## Decision Making Process

### Rule-Based Decisions

When not using LLM integration, country agents make decisions based on rule sets:

```python
# Example from ChinaAgent (rule-based fallback using ActionType enum)
def _decide_without_llm(self, state: SimulationState) -> EconomicAction:
    # Check recent actions from US
    us_actions = [
        action for action in state.recent_actions
        if action.country.name == "US" and action.target_country and
        action.target_country.name == "China"
    ]
    
    # If US increased tariffs or imposed controls, retaliate
    if us_actions and us_actions[-1].action_type in (
        ActionType.TARIFF_INCREASE, ActionType.TECH_EXPORT_CONTROL
    ):
        return EconomicAction(
            country=self.country,
            action_type=ActionType.INDUSTRIAL_SUBSIDY,
            target_country=None,
            sectors=["semiconductors", "ai", "green_tech"],
            magnitude=0.4,
            justification="Strategic subsidy response to US pressure"
        )
    
    # Otherwise invest in green tech leadership
    return EconomicAction(
        country=self.country,
        action_type=ActionType.GREEN_TECH_INVESTMENT,
        target_country=None,
        sectors=["batteries", "green_tech", "automotive"],
        magnitude=0.3,
        justification="Continuing green technology leadership strategy"
    )
```

### LLM-Based Decisions

The simulation can use Large Language Models to generate more nuanced policy decisions:

1. A context-specific prompt is generated for each country
2. The LLM considers economic conditions, previous actions, and country characteristics
3. The LLM response is parsed into actionable economic policies
4. These policies are applied in the simulation

## Economic Impact Calculations

### Tariff Impact Calculation

When a country imposes tariffs:

1. Trade volume changes are estimated based on price elasticity
2. Price effects are calculated
3. Tariff revenue and deadweight loss are determined
4. GDP impacts are calculated for both imposing and targeted countries

```python
def calculate_tariff_impact(
    state: SimulationState,
    policy: TariffPolicy, 
    imposing_country: Country,
    targeted_country: Country
) -> TariffImpact:
    # Find relevant trade flows
    trade_flows = [...]
    
    # Calculate trade volume changes and price effects
    trade_volume_change = {}
    price_effects = {}
    
    for sector, rate in policy.sector_rates.items():
        # Calculate price increase
        price_increase = rate * 0.7  # 70% pass-through
        price_effects[sector] = price_increase
        
        # Calculate volume change based on elasticity
        volume_change = sector_volume * price_elasticity * price_increase
        trade_volume_change[sector] = volume_change
    
    # Calculate GDP impacts
    exporter_gdp_impact = total_export_loss * 0.8
    importer_gdp_impact = tariff_revenue - consumer_surplus_loss
    
    return TariffImpact(...)
```

### Stability Analysis

The simulation continuously analyzes economic stability:

1. **Country Stability**: Based on GDP growth, inflation, unemployment, tariff impacts, etc.
2. **Global Stability**: Based on average tariff levels, retaliation cycles, trade imbalances, and economic volatility

A stability score between 0-1 is calculated, where higher values indicate greater stability.

## Interface and Visualization

### API

The system provides a REST API built with FastAPI for programmatic control:

- `POST /api/simulation/start` — start a simulation, returns `simulation_id`
- `POST /api/simulation/{id}/step` — advance one quarter
- `GET /api/simulation/{id}/state` — full simulation state
- `GET /api/simulation/{id}/status` — lightweight status
- `GET /api/simulation/{id}/stability` — stability scores
- `GET /api/results/{id}` — full results summary
- `GET /api/results/{id}/trade-flows` — bilateral trade flows
- `GET /api/results/{id}/actions` — action history

Session isolation is handled by `SimulationManager` — a module-level singleton that maps `simulation_id → SimulationEngine`. Interactive Swagger UI: `http://localhost:8000/docs`

### Dashboard

An interactive dashboard built with Streamlit allows users to:

- Visualize economic indicators over time
- Examine trade relationships
- Track policy decisions
- Analyze stability metrics
- Start new simulations with custom parameters

## Usage Examples

### Starting a New Simulation

```python
from tradewar.simulation.engine import SimulationEngine
from tradewar.economics.models import Country

# Create country instances (2024 baseline GDPs in trillions USD)
countries = [
    Country(name="US", gdp=28.8, population=335_000_000),
    Country(name="China", gdp=17.8, population=1_400_000_000),
    Country(name="Indonesia", gdp=1.42, population=275_000_000)
]

# Initialize engine (seeds random for reproducibility)
engine = SimulationEngine(countries)

# Run simulation for 20 quarters (5 years)
states = []
for year in range(2024, 2029):
    for quarter in range(1, 5):
        state = engine.step(year, quarter)
        states.append(state)

# Analyze results
from tradewar.simulation.stability import StabilityAnalyzer
analyzer = StabilityAnalyzer()
for i, state in enumerate(states):
    stability, factors = analyzer.analyze_global_stability(state)
    print(f"Quarter {i+1}: Global stability = {stability:.2f}")
```

## Conceptual Modeling

The simulation models several key aspects of international trade wars:

1. **Tariff Cycles**: How increasing tariffs lead to retaliatory measures
2. **Economic Impacts**: How trade restrictions affect growth and employment
3. **Strategic Sectors**: How countries protect industries of national importance
4. **External Shocks**: How events like pandemics affect global trade
5. **Policy Decisions**: How countries decide on economic actions based on their interests