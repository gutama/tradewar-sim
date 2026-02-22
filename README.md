# Trade War Simulation

A sophisticated simulation framework for modeling trade wars between countries, with a specific focus on the dynamics between the US, China, and Indonesia. Built for the 2024-2026 era of strategic competition: technology export controls, green tech races, supply chain restructuring, and reciprocal tariff regimes.

## Overview

This project simulates the economic impacts of trade policies, tariffs, and retaliatory measures between countries in a trade war scenario. It combines real economic models with LLM-based (or rule-based) agent decision-making to produce realistic quarterly policy cycles and their downstream consequences.

**Baseline economies (2024 data):** US $28.8T · China $17.8T · Indonesia $1.42T

## Features

- **Agent-based modeling** for US, China, and Indonesia — each with distinct strategic priorities
- **11 action types** covering traditional tariffs, modern tech restrictions, green-economy subsidies, and supply chain moves
- **Quarterly simulation loop** with GDP, inflation, unemployment, and confidence tracking
- **LLM-powered decisions** via OpenAI (v1+), Anthropic Messages API, or LiteLLM — with rule-based fallback
- **External event system** — semiconductor shortages, AI breakthroughs, rare earth crises, cyber attacks, and more
- **REST API** (FastAPI) for programmatic control with `SimulationManager` session isolation
- **Interactive Streamlit dashboard** for real-time visualization
- **Trade diversion model** — bilateral tariff gaps trigger third-country demand reallocation
- **62 automated tests** covering economics, agents, LLM parsing, API, and edge cases

## Action Types

| Category | Action Type | Description |
|---|---|---|
| Traditional | `tariff_increase` | Raise import duties on target country |
| Traditional | `tariff_decrease` | Reduce import duties |
| Traditional | `tariff_adjustment` | Adjust sector-specific tariff rates |
| Traditional | `import_quota` | Restrict import volumes (quota_factor applied to trade flows) |
| Traditional | `export_subsidy` | Subsidize domestic exports |
| Traditional | `currency_devaluation` | Depreciate currency to improve trade competitiveness |
| Modern | `tech_export_control` | Restrict advanced technology exports (semiconductors, AI) |
| Modern | `industrial_subsidy` | Government subsidies for strategic industries |
| Modern | `supply_chain_diversification` | Reduce single-country supply dependencies |
| Modern | `green_tech_investment` | Investment in clean energy and EV technology |
| Modern | `friend_shoring` | Relocate supply chains to allied countries |
| Modern | `data_sovereignty` | Protect digital infrastructure and data |

## Installation

```bash
# Clone the repository
git clone https://github.com/gutama/tradewar-sim.git
cd tradewar-sim

# Set up virtual environment (Python >= 3.8)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package and all dependencies
pip install -e .
```

## Configuration

Create a `.env` file in the project root to supply API keys:

```bash
# LLM provider (openai | anthropic | litellm | none)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Simulation defaults
SIMULATION_YEARS=10
QUARTERS_PER_YEAR=4
RANDOM_SEED=42
```

## Running the Simulation

### Python script

```bash
python3 scripts/run_simulation.py
```

### REST API server

```bash
python3 scripts/run_api.py
# API docs available at http://localhost:8000/docs
```

### Interactive dashboard

```bash
python3 scripts/run_dashboard.py
# Dashboard at http://localhost:8501
```

### Docker

```bash
docker-compose up
```

## API Endpoints

Base path: `http://localhost:8000`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/simulation/start` | Start a new simulation, returns `simulation_id` |
| `POST` | `/api/simulation/{id}/step` | Advance one quarter |
| `GET` | `/api/simulation/{id}/state` | Full simulation state |
| `GET` | `/api/simulation/{id}/status` | Lightweight status (year, quarter, step count) |
| `GET` | `/api/simulation/{id}/stability` | Global and per-country stability scores |
| `GET` | `/api/results/{id}` | Full results summary |
| `GET` | `/api/results/{id}/trade-flows` | Bilateral trade flow data |
| `GET` | `/api/results/{id}/actions` | Action history with optional year filter |

Interactive Swagger UI: `http://localhost:8000/docs`

## Development

```bash
# Install dev extras
pip install -e ".[dev]"

# Run full test suite
pytest tests/ -q

# Run with coverage
pytest tests/ --cov=tradewar --cov-report=term-missing
```

Current test results: **62 passed, 0 failures**

## 2024-2026 Update Highlights

See [TRADE_WAR_2024_UPDATES.md](TRADE_WAR_2024_UPDATES.md) for full details:

- **6 modern action types** added: tech export controls, industrial subsidies, supply chain diversification, green tech investment, friend-shoring, data sovereignty
- **8 new event types**: semiconductor shortages, AI breakthroughs, EV market disruptions, rare earth crises, cyber attacks, green tech subsidy races, regional trade agreements, nearshoring waves
- **US-Indonesia reciprocal trade** — bilateral preference boost and trade diversion logic
- **Trump 2.0 US policy framework** — aggressive tariffs, technology decoupling, re-industrialization
- **Modern sectors**: semiconductors, AI, green_tech, batteries, rare_earths, automotive, mining, digital_services
- **OpenAI SDK v1+ and Anthropic Messages API** support with 3-attempt exponential backoff
- **Deterministic mode** — `RANDOM_SEED` config for reproducible runs

## Project Structure

```
tradewar/
├── agents/          # USAgent, ChinaAgent, IndonesiaAgent + factory
├── economics/       # Models (ActionType, EconomicAction, TariffPolicy, Country)
│                    # GDP impact, tariff calculations, trade balance
├── simulation/      # SimulationEngine, SimulationState, EventGenerator, StabilityAnalyzer
├── llm/             # LLM client (OpenAI/Anthropic/LiteLLM), parser, country prompts
├── api/             # FastAPI app + SimulationManager, simulation & results routes
├── visualization/   # Streamlit dashboard, Plotly charts
└── data/            # Baseline JSON for US, China, Indonesia
```

## License

MIT
