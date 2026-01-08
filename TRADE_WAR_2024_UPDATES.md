# Trade War Simulation - 2024-2026 Updates

## Overview

This document describes the enhancements made to the Trade War Simulation framework to reflect the latest developments in global trade dynamics as of 2024-2026.

## Latest Trade War Developments Incorporated

### 1. US-China Strategic Competition Evolution

**Key Changes:**
- Shift from broad tariffs to targeted technology restrictions
- Focus on semiconductors, AI, and advanced manufacturing
- Export controls as primary policy tool
- Industrial policy through subsidies (CHIPS Act, IRA)

**Implementation:**
- New action types: `tech_export_control`, `industrial_subsidy`
- Updated US policy prompts to reflect Biden-era priorities
- New events: AI breakthroughs, semiconductor shortages

### 2. Green Technology Race

**Key Changes:**
- Global competition in EVs, batteries, and solar panels
- Critical minerals (rare earths, lithium, cobalt) as strategic assets
- Massive government subsidies for green tech

**Implementation:**
- New action type: `green_tech_investment`
- New sectors: batteries, green_tech, rare_earths, ev
- Events: EV market disruption, rare earth crisis, green tech subsidy race

### 3. Supply Chain Restructuring

**Key Changes:**
- "Nearshoring" and "friend-shoring" replacing globalization
- Indonesia and other countries benefiting from China+1 strategies
- Resilience prioritized over efficiency

**Implementation:**
- New action types: `supply_chain_diversification`, `friend_shoring`
- Events: Supply chain nearshoring wave
- Updated Indonesia policy to reflect beneficiary position

### 4. Digital and Data Sovereignty

**Key Changes:**
- Trade restrictions on technology platforms and data
- Concerns about digital infrastructure security
- National cloud and software ecosystems

**Implementation:**
- New action type: `data_sovereignty`
- Events: Major cyber attacks on infrastructure

### 5. Regional Trade Agreements

**Key Changes:**
- RCEP, CPTPP, and other regional agreements gaining importance
- Shift from multilateral to regional/bilateral approaches

**Implementation:**
- New events: Regional trade agreement formation
- Updated policy priorities for all countries

## New Features

### New Economic Action Types

The simulation now supports these additional action types:

1. **tech_export_control**: Restrict exports of advanced technology (semiconductors, AI)
2. **industrial_subsidy**: Government subsidies for domestic manufacturing
3. **supply_chain_diversification**: Reduce dependency on single country/region
4. **green_tech_investment**: Investment in clean energy and EV technology
5. **friend_shoring**: Relocate supply chains to allied countries
6. **data_sovereignty**: Protect digital infrastructure and data

### New Economic Sectors

The following sectors are now recognized in the simulation:

- **semiconductors**: Advanced chip manufacturing
- **ai**: Artificial intelligence and machine learning
- **green_tech**: Clean energy technologies
- **batteries**: EV and energy storage batteries
- **rare_earths**: Critical minerals for technology
- **automotive**: Traditional and electric vehicles
- **mining**: Resource extraction
- **digital_services**: Cloud, software, platforms

### New Events

#### Technology Events
- **Global Semiconductor Shortage**: Reflects ongoing chip supply challenges
- **Major AI Breakthrough**: Represents advances in AI technology
- **Major Technology Breakthrough**: General tech advances

#### Green Economy Events
- **Electric Vehicle Market Disruption**: Major shifts in EV markets
- **Green Technology Subsidy Race**: Government competition in green tech
- **Rare Earth Minerals Crisis**: Critical mineral supply disruptions

#### Supply Chain Events
- **Supply Chain Nearshoring Wave**: Companies relocating production
- **Global Supply Chain Disruption**: Major logistics challenges

#### Digital Security Events
- **Major Cyber Attack on Infrastructure**: Digital infrastructure threats

#### Trade Policy Events
- **New Regional Trade Agreement**: Formation of new trade blocs

### Updated Policy Prompts

#### United States (2024-2026 Era)
Focus areas:
- Strategic competition with China in technology
- Industrial policy and domestic manufacturing subsidies
- Supply chain resilience through friend-shoring
- Green technology leadership
- Technology export controls
- Allied cooperation
- Critical minerals security
- Data sovereignty

#### China (2024-2026 Era)
Focus areas:
- Technological self-sufficiency (overcoming US controls)
- Green technology leadership (EVs, batteries, solar)
- Strategic retaliation using rare earths
- Dual circulation strategy
- Regional integration (RCEP, BRI)
- Massive industrial subsidies
- Supply chain security
- Independent tech ecosystem

#### Indonesia (2024-2026 Era)
Focus areas:
- Strategic neutrality between US and China
- Nearshoring beneficiary positioning
- Critical minerals hub (nickel, cobalt)
- Green economy manufacturing
- ASEAN leadership
- Resource value addition
- Digital economy growth
- Selective industrial policy

## Usage Examples

### Example 1: Technology Export Controls

```python
from tradewar.economics.models import Country, EconomicAction, ActionType

us = Country(name="US", gdp=25.0)
china = Country(name="China", gdp=17.0)

action = EconomicAction(
    country=us,
    action_type=ActionType.TECH_EXPORT_CONTROL,
    target_country=china,
    sectors=["semiconductors", "ai"],
    magnitude=0.9,  # 90% restriction
    justification="Restricting advanced chip exports to protect national security"
)
```

### Example 2: Green Technology Investment

```python
action = EconomicAction(
    country=china,
    action_type=ActionType.GREEN_TECH_INVESTMENT,
    sectors=["batteries", "green_tech", "automotive"],
    magnitude=0.5,  # 50% increase in investment
    justification="Massive subsidies for EV and battery manufacturing to dominate global markets"
)
```

### Example 3: Supply Chain Diversification

```python
action = EconomicAction(
    country=us,
    action_type=ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
    target_country=indonesia,
    sectors=["electronics", "manufacturing"],
    magnitude=0.3,  # 30% of supply chains
    justification="Moving electronics manufacturing to Indonesia as part of China+1 strategy"
)
```

## Impact on Simulation Dynamics

### 1. More Realistic Modern Trade Wars
- Captures shift from tariffs to technology controls
- Represents industrial policy and subsidies
- Models supply chain restructuring

### 2. Broader Strategic Competition
- Beyond trade deficits to technology leadership
- Green economy competition
- Critical resources as strategic assets

### 3. Multi-Dimensional Trade Policy
- Trade, technology, environment, and security interlinked
- More complex decision-making for AI agents
- Richer simulation outcomes

### 4. Emerging Economy Opportunities
- Indonesia and similar countries can benefit from decoupling
- Nearshoring creates new manufacturing hubs
- Critical mineral suppliers gain leverage

## Testing

Run the test suite to verify new features:

```bash
pytest tests/ -v
```

Key test areas:
- New action types are recognized
- Events with new sectors work correctly
- Policy prompts include new action types
- Economic calculations handle new mechanics

## Future Enhancements

Potential areas for further development:

1. **Quantitative Impact Models**: More detailed economic models for new action types
2. **Technology Leadership Metrics**: Track relative tech competitiveness
3. **Supply Chain Networks**: Model complex multi-country supply chains
4. **Carbon Border Adjustments**: Environmental trade measures
5. **Digital Trade Rules**: Data flow restrictions and regulations
6. **Critical Mineral Markets**: Detailed modeling of resource dependencies
7. **Allied Coordination**: Joint actions by allied countries
8. **Sanctions Modeling**: Comprehensive sanctions beyond trade

## References

These updates are based on:
- US-China trade and technology competition (2020-2024)
- CHIPS and Science Act (2022)
- Inflation Reduction Act (2022)
- China's Made in China 2025 and Dual Circulation strategies
- RCEP implementation (2022)
- Global supply chain disruptions (2020-2024)
- EV and battery market developments
- Semiconductor supply chain challenges

## Contributing

To add new features or suggest improvements:

1. Review current trade war developments
2. Identify gaps in simulation capabilities
3. Propose new action types, sectors, or events
4. Update policy prompts to reflect current strategies
5. Add tests for new features
6. Update documentation

## License

MIT License - Same as main project
