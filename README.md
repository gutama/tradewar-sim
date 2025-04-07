# Trade War Simulation

A sophisticated simulation framework for modeling trade wars between countries, with a specific focus on the dynamics between the US, China, and Indonesia.

## Overview

This project simulates the economic impacts of trade policies, tariffs, and retaliatory measures between countries in a trade war scenario. It uses economic models combined with LLM-based agent behaviors to create realistic policy decisions and their consequences.

## Features

- Agent-based modeling for country-specific trade policies
- Economic impact simulations for tariffs, trade balances, and GDP
- External event integration to model real-world disruptions
- LLM-powered decision making to simulate realistic policy responses
- Interactive dashboard for visualization and analysis
- API for programmatic control and data retrieval

## Installation

```bash
# Clone the repository
git clone https://github.com/gutama/tradewar-sim.git
cd tradewar-sim

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

## Running the Simulation

### Using Python

```bash
python scripts/run_simulation.py
```

### Using Docker

```bash
docker-compose up
```

## API Documentation

The API is available at `http://localhost:8000` when running the simulation. Key endpoints:

- `POST /api/simulation/start`: Start a new simulation
- `GET /api/results/summary`: Get current simulation results

## Dashboard

Access the interactive visualization dashboard at `http://localhost:8501` when running the simulation.

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT
