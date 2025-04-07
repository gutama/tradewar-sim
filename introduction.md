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
def step(self) -> SimulationState:
    # Get actions from all country agents
    actions = [agent.decide_action(self.state) for agent in self.agents.values()]
    
    # Apply economic actions to simulation state
    self._apply_actions(actions)
    
    # Update economic indicators based on actions and events
    self._update_economic_indicators()
    
    # Check for and apply any external events
    self._handle_events()
    
    # Advance time
    self.current_quarter += 1
    if self.current_quarter > 4:
        self.current_quarter = 1
        self.current_year += 1
        
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
1. Decide economic actions (tariffs, subsidies, etc.)
2. Calculate tariff policies
3. Update their strategy based on evolving conditions

### Economic Models

The system implements various economic models to calculate impacts:

1. **Tariff Impacts**: Calculates how tariffs affect trade volumes, prices, and GDP
2. **GDP Impacts**: Determines how trade actions influence economic growth
3. **Trade Balances**: Tracks bilateral trade relationships
4. **Stability Analysis**: Evaluates economic stability of countries and the global system

### Simulation State

The `SimulationState` class tracks all economic variables, including:

- List of countries with economic indicators
- Current time (year and quarter)
- Trade flows between countries
- Active tariff policies
- Economic indicators (GDP, inflation, unemployment, etc.)
- Recent economic actions
- Active external events

### Event System

The simulation includes an `EventGenerator` that creates random or scheduled external events such as:
- Economic recessions
- Supply chain disruptions
- Natural disasters
- Presidential elections
- Global pandemics

These events affect economic indicators across countries.

## Decision Making Process

### Rule-Based Decisions

When not using LLM integration, country agents make decisions based on rule sets:

```python
# Example from ChinaAgent
def decide_action(self, state: SimulationState) -> EconomicAction:
    # Check recent actions from US
    us_actions = [
        action for action in state.recent_actions 
        if action.country.name == "US" and action.target_country and 
        action.target_country.name == "China"
    ]
    
    # If US increased tariffs, retaliate
    if us_actions and us_actions[-1].action_type == "tariff_increase":
        return EconomicAction(
            country=self.country,
            action_type="tariff_increase",
            target_country=Country(name="US"),
            sectors=us_action.sectors,
            magnitude=us_action.magnitude * self.retaliatory_factor,
            justification="Reciprocal measures in response to US tariffs"
        )
    
    # Otherwise focus on strategic sectors
    return EconomicAction(
        country=self.country,
        action_type="investment",
        target_country=None,
        sectors=self.strategic_sectors,
        magnitude=0.1,
        justification="Strategic sector development"
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

- Start/stop simulations
- Control simulation parameters
- Retrieve economic data
- Apply manual policy changes

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
from tradewar.simulation import SimulationEngine
from tradewar.economics.models import Country

# Create country instances
countries = [
    Country(name="US", gdp=21.0, population=330000000),
    Country(name="China", gdp=15.0, population=1400000000),
    Country(name="Indonesia", gdp=1.0, population=270000000)
]

# Initialize engine
engine = SimulationEngine(countries)

# Run simulation for 20 quarters
states = []
for _ in range(20):
    state = engine.step()
    states.append(state)

# Analyze results
from tradewar.simulation import StabilityAnalyzer
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