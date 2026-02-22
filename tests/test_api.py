"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from tradewar.api.server import app


client = TestClient(app)


def _sample_config() -> dict:
    return {
        "years": 2,
        "steps_per_year": 4,
        "random_seed": 42,
        "countries": [
            {
                "name": "US",
                "gdp": 28.8,
                "population": 330000000,
                "inflation_rate": 0.02,
                "unemployment_rate": 0.04,
                "currency_value": 1.0,
                "sectors": {"technology": 0.3, "manufacturing": 0.2},
            },
            {
                "name": "China",
                "gdp": 17.8,
                "population": 1400000000,
                "inflation_rate": 0.025,
                "unemployment_rate": 0.05,
                "currency_value": 1.0,
                "sectors": {"technology": 0.2, "manufacturing": 0.35},
            },
            {
                "name": "Indonesia",
                "gdp": 1.42,
                "population": 270000000,
                "inflation_rate": 0.03,
                "unemployment_rate": 0.06,
                "currency_value": 1.0,
                "sectors": {"manufacturing": 0.2, "natural_resources": 0.25},
            },
        ],
    }


def test_simulation_lifecycle_endpoints():
    """Simulation can be started, stepped, queried, and results retrieved."""
    start_response = client.post("/api/simulation/start", json=_sample_config())
    assert start_response.status_code == 200
    simulation_id = start_response.json()
    assert simulation_id.startswith("sim_")

    status_response = client.get(f"/api/simulation/{simulation_id}/status")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["simulation_id"] == simulation_id

    step_response = client.post(f"/api/simulation/{simulation_id}/step")
    assert step_response.status_code == 200

    state_response = client.get(f"/api/simulation/{simulation_id}/state")
    assert state_response.status_code == 200
    state_payload = state_response.json()
    assert "countries" in state_payload
    assert len(state_payload["countries"]) == 3

    results_response = client.get(f"/api/results/{simulation_id}")
    assert results_response.status_code == 200
    results_payload = results_response.json()
    assert results_payload["simulation_id"] == simulation_id


def test_nonexistent_simulation_returns_404():
    """Missing simulations should return 404 from status endpoint."""
    response = client.get("/api/simulation/sim_does_not_exist/status")
    assert response.status_code == 404
