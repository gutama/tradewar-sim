# Trade War Simulation — Gap-Closing Task List

> Generated: 2026-02-22  
> Baseline quality: **4.8 / 10**  
> Target quality: **~8 / 10**  
> Total tasks: **27**
> Status update: **2026-02-22 — 27/27 completed**

---

## Phase 1 — Fix Foundation Models & State
*Fix data models, expired-item cleanup, type correctness, and baseline data. No downstream breakage; safe to ship independently.*

- [x] **1.1** Fix `TariffPolicy.end_date` crash  
  **File:** `tradewar/economics/models.py` line 78–83  
  **Problem:** `self.start_date.replace(day=self.start_date.day + days)` raises `ValueError` when `day > 31`  
  **Fix:** Replace with `self.start_date + timedelta(days=self.duration_quarters * 90)`; add `from datetime import timedelta`

- [x] **1.2** Change `EconomicAction.action_type` from `str` to `ActionType`  
  **File:** `tradewar/economics/models.py` line 58  
  **Fix:** Change type annotation to `ActionType`. Update all agent files and tests that construct `EconomicAction` with raw strings (`"tariff_increase"`, `"status_quo"`, etc.) to use enum values (`ActionType.TARIFF_INCREASE`, etc.)  
  **Affected:** `tradewar/agents/us_agent.py` L67, L76; `tradewar/agents/china_agent.py` L64, L74; `tradewar/agents/indonesia_agent.py` L67, L78, L85; all `assert action.action_type == "..."` in test files

- [x] **1.3** Add `trigger_time` and `one_time` fields to `EventConfig`  
  **File:** `tradewar/economics/models.py` lines 103–112  
  **Fix:** Add `trigger_time: Optional[int] = None` and `one_time: bool = False` to the `EventConfig` dataclass. Then in `tradewar/simulation/events.py` remove all `setattr(event, "trigger_time", ...)` and `setattr(event, "one_time", ...)` hacks (lines 156–158, 265) and replace with direct dataclass field assignment. Remove all `hasattr(event, ...)` guards (lines 82–84, 96–97) and use direct attribute access instead.

- [x] **1.4** Implement `_remove_expired_items()` in `SimulationState`  
  **File:** `tradewar/simulation/state.py` line 180  
  **Problem:** Body is `pass` — tariff policies and events accumulate forever, growing memory and distorting calculations  
  **Fix:** Remove expired entries from `self.active_tariff_policies` by comparing each policy's `end_date` vs current datetime; remove expired entries from `self.active_events` by tracking how many quarters each event has been active vs its `duration_quarters`. Requires task 1.1 first (working `end_date`).

- [x] **1.5** Fix `_format_events` type annotation  
  **File:** `tradewar/llm/prompts/base_prompt.py` line 145  
  **Problem:** Signature says `events: List[dict]` but receives `List[EventConfig]` objects  
  **Fix:** Change to `events: List[EventConfig]` and add `from tradewar.economics.models import EventConfig` import

- [x] **1.6** Update baseline economy JSON files to 2024-era values  
  **Files:**
  - `tradewar/data/baseline/us_economy.json` — change `"gdp"` from `21.43` → `28.8` (trillion USD, 2024)
  - `tradewar/data/baseline/china_economy.json` — change `"gdp"` from `14.72` → `17.8`
  - `tradewar/data/baseline/indonesia_economy.json` — change `"gdp"` from `1.06` → `1.42`
  
  **Also update to match:**
  - `tests/conftest.py` `mock_countries` fixture (US: 21.0 → 28.8, China: 15.0 → 17.8, Indonesia: 1.0 → 1.42)
  - `tradewar/visualization/dashboard.py` new-simulation form defaults (lines 139–159)

---

## Phase 2 — Wire the Real Economics Engine
*Connect the existing-but-unused sophisticated models into the live simulation loop.*

- [x] **2.1** Fix double time-increment bug  
  **File:** `tradewar/simulation/engine.py`  
  **Problem:** `run_full_simulation()` sets `self.current_year` and `self.current_quarter` in the loop (lines 111, 113), then `step()` increments them again at lines 122–125 — every step advances time twice  
  **Fix:** Remove the `self.current_quarter += 1` / year-rollover block from the top of `step()`. Instead, pass `(year, quarter)` as parameters into `step(year, quarter)` and have it set both `self.state.year` and `self.state.quarter`. Keep `run_full_simulation` as the sole source of time advancement.

- [x] **2.2** Wire `calculate_gdp_impact()` into the engine  
  **Files:** `tradewar/simulation/engine.py` lines 177–202; `tradewar/economics/gdp.py` line 19  
  **Problem:** `_apply_economic_impacts()` applies crude inline `gdp *= 0.995` multipliers; the full `gdp.py` model is dead code  
  **Fix:** Import `calculate_gdp_impact` in `engine.py`. In `_apply_economic_impacts()`, replace all inline `gdp *=` multipliers with a `calculate_gdp_impact(self.state, country, year, quarter)` call per country. Apply the returned growth rate: `country.gdp *= (1 + growth_rate)`.

- [x] **2.3** Replace placeholder `_calculate_*` methods in `SimulationState`  
  **File:** `tradewar/simulation/state.py` lines 148–175  
  **Replace all 5 stubs:**

  | Method | Current | Replacement logic |
  |--------|---------|-------------------|
  | `_calculate_gdp_growth` | `return 0.02` | `(country.gdp - prev_gdp) / prev_gdp` from previous indicator; fall back to 0.02 if no history |
  | `_calculate_inflation` | `return 0.025` | Base rate + weighted average tariff price pass-through from recent `TariffImpact` price effects |
  | `_calculate_unemployment` | `return 0.05` | Okun's law: `prev_unemployment - 0.5 * (gdp_growth - trend_growth)`; clamp to [0.02, 0.20] |
  | `_calculate_consumer_confidence` | `return 100.0` | Composite index: penalize high inflation deviation (>2%) and rising unemployment; reward GDP growth |
  | `_calculate_business_confidence` | `return 100.0` | Composite index: penalize tariff severity and trade balance deterioration; reward GDP growth |

- [x] **2.4** Handle all `ActionType` values in the engine  
  **File:** `tradewar/simulation/engine.py` lines 154–202  
  **Problem:** Only `"tariff_increase"` and `"tariff_adjustment"` are handled in `_apply_actions`; only `"tariff_increase"`, `"investment"`, `"subsidy"` in `_apply_economic_impacts`; all new 2024 action types are silently ignored  
  **Fix:** Add handling for each missing type:

  | Action type | `_apply_actions` | `_apply_economic_impacts` |
  |-------------|-----------------|--------------------------|
  | `TARIFF_DECREASE` | Create TariffPolicy with negative rates | Boost target country GDP slightly |
  | `EXPORT_SUBSIDY` | Record in state | Boost exporter output/trade slightly |
  | `IMPORT_QUOTA` | Record quota in state | Reduce import flows for affected sectors |
  | `CURRENCY_DEVALUATION` | Reduce `country.currency_value` | Boost exports, inflate imports |
  | `STATUS_QUO` | No-op | No-op |
  | `TECH_EXPORT_CONTROL` | Reduce bilateral tech-sector trade flows | GDP penalty on target; small GDP gain on source |
  | `INDUSTRIAL_SUBSIDY` | Record | Boost source manufacturing sectors GDP |
  | `SUPPLY_CHAIN_DIVERSIFICATION` | Redirect supply chain flows toward `target_country` | Boost target trade flows |
  | `GREEN_TECH_INVESTMENT` | Record | Boost source green/batteries/EV sectors GDP |
  | `FRIEND_SHORING` | Redirect supply chain flows | Similar to supply chain diversification |
  | `DATA_SOVEREIGNTY` | Reduce digital services trade flows | Minor GDP impact on both sides |

- [x] **2.5** Seed `random` in the engine for reproducibility  
  **File:** `tradewar/simulation/engine.py` `__init__` (line 37 area)  
  **Fix:** Add `import random` and `random.seed(config.simulation.random_seed)` in `SimulationEngine.__init__`. This ensures `gdp.py` and `trade_balance.py` random calls are deterministic across runs.

---

## Phase 3 — Connect Agent → LLM Parser Pipeline
*Wire the real `LLMResponseParser` to agents and expand fallback decision logic.*

- [x] **3.1** Replace stub `_parse_llm_response()` in all three agents  
  **Files:** `tradewar/agents/us_agent.py` line 118; `tradewar/agents/china_agent.py` line 118; `tradewar/agents/indonesia_agent.py` line 123  
  **Problem:** All three return a hardcoded `EconomicAction` with `action_type="tariff_adjustment"` regardless of LLM output  
  **Fix:** Import `LLMResponseParser` from `tradewar.llm.parser`. Replace stub bodies with:
  ```python
  parser = LLMResponseParser()
  action = parser.parse_action_response(llm_response, self.country)
  if action is None:
      return self._decide_without_llm(state)
  return action
  ```

- [x] **3.2** Add LLM error-string detection in `decide_action()`  
  **Files:** all three agent `decide_action()` methods  
  **Fix:** Before calling `_parse_llm_response`, check `if llm_response.startswith("ERROR:")` and fall back to `_decide_without_llm(state)` immediately.

- [x] **3.3** Expand rule-based fallback to use 2024 action types  
  **Files:** `tradewar/agents/us_agent.py`, `tradewar/agents/china_agent.py`, `tradewar/agents/indonesia_agent.py`  
  **Fix:** In `_decide_without_llm()`, add branches for realistic modern actions:
  - **US:** if `tech_deficit_risk > threshold` → `TECH_EXPORT_CONTROL`; if `ally_trade_gap > threshold` → `FRIEND_SHORING`
  - **China:** if US recently imposed tech controls → `INDUSTRIAL_SUBSIDY`; if GDP growth slowing → `GREEN_TECH_INVESTMENT`
  - **Indonesia:** if US-China tension is high → `SUPPLY_CHAIN_DIVERSIFICATION`; default more often to `INVESTMENT` over `TARIFF_INCREASE`

---

## Phase 4 — Modernize LLM Client
*Update to current OpenAI v1+ and Anthropic Messages APIs. Add resilience.*

- [x] **4.1** Update `_generate_openai()` to use OpenAI SDK v1+  
  **File:** `tradewar/llm/client.py` line 119  
  **Problem:** Uses `self.client.ChatCompletion.create(...)` (pre-v1.0 API, removed in v1.0)  
  **Fix:** Change to:
  ```python
  response = self.client.chat.completions.create(
      model=self.model,
      messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
      temperature=self.temperature,
      max_tokens=self.max_tokens,
  )
  return response.choices[0].message.content
  ```

- [x] **4.2** Update `_generate_anthropic()` to use Anthropic Messages API  
  **File:** `tradewar/llm/client.py` line 143  
  **Problem:** Uses deprecated `client.completions.create()` with `Human:/Assistant:` prompt format  
  **Fix:** Change to:
  ```python
  response = self.client.messages.create(
      model=self.model,
      system=system,
      messages=[{"role": "user", "content": prompt}],
      max_tokens=self.max_tokens,
  )
  return response.content[0].text
  ```

- [x] **4.3** Add retry logic with exponential backoff  
  **File:** `tradewar/llm/client.py` in `generate_response()` / provider methods  
  **Fix:** Wrap each provider call in a retry loop (3 attempts, delays: 1s, 2s, 4s). Catch provider-specific errors (`openai.APIError`, `openai.RateLimitError`, `anthropic.APIError`). Re-raise on 3rd failure. Log each retry attempt at WARN level.

---

## Phase 5 — Repair API & Visualization Layer

- [x] **5.1** Add `SimulationManager` and `get_simulation_manager()` to `server.py`  
  **File:** `tradewar/api/server.py`  
  **Problem:** `routes/simulation.py` and `routes/results.py` both import `get_simulation_manager` from `server.py`, which doesn't define this function, causing `ImportError` at startup  
  **Fix:** In `server.py`, add:
  - A `SimulationManager` class that owns the `active_simulations: Dict[str, SimulationEngine]` dict and a counter. Expose `create(countries)`, `get(sim_id)`, and `delete(sim_id)` methods.
  - A FastAPI dependency: `def get_simulation_manager() -> SimulationManager: return _manager` (using a module-level singleton `_manager`)

- [x] **5.2** Register routers with `app.include_router()`  
  **File:** `tradewar/api/server.py`  
  **Problem:** `routes/simulation.py` and `routes/results.py` define `APIRouter` instances but they are never mounted on `app`  
  **Fix:** After fixing 5.1, add:
  ```python
  from tradewar.api.routes.simulation import router as simulation_router
  from tradewar.api.routes.results import router as results_router
  app.include_router(simulation_router, prefix="/api")
  app.include_router(results_router, prefix="/api")
  ```
  Remove the duplicate bare endpoints from `server.py` that overlap with the router endpoints.

- [x] **5.3** Fix type mismatch in `start_simulation` endpoint  
  **File:** `tradewar/api/server.py` line 60 area  
  **Problem:** `country.dict()` creates dicts but `SimulationEngine(countries=...)` expects `List[Country]` objects  
  **Fix:** Construct `Country` objects: `countries = [Country(**c.dict()) for c in request.countries]` before passing to `SimulationEngine`.

- [x] **5.4** Replace deprecated `st.experimental_rerun()` in dashboard  
  **File:** `tradewar/visualization/dashboard.py` lines 184, 225, 244  
  **Fix:** Replace all 3 occurrences of `st.experimental_rerun()` with `st.rerun()`

- [x] **5.5** Fix `create_policy_timeline()` x-axis  
  **File:** `tradewar/visualization/plots.py` line 258–314  
  **Problem:** Uses `px.timeline()` with string "Y1Q1" values for `x_start`; no `x_end` provided; `px.timeline` requires datetime  
  **Fix:** Either (a) convert "Y1Q1" strings to `datetime` objects (quarter 0 = 2026-01-01, each quarter = 3 months) and compute `x_end = x_start + timedelta(days=duration_quarters*90)`, or (b) switch to `px.bar` horizontal chart with categorical x-axis for simplicity.

---

## Phase 6 — Harden Tests

- [x] **6.1** Seed `random` in `mock_state` fixture  
  **File:** `tests/conftest.py` line 72  
  **Fix:** Add `random.seed(42)` at the top of the `mock_state` fixture body (before the `random.uniform` calls) to make test trade-flow values deterministic across runs.

- [x] **6.2** Update test assertions from string to `ActionType` enum  
  **Files:** `tests/test_agents.py` line 46; any other tests with `assert action.action_type == "..."`  
  **Fix:** Replace string comparisons with enum comparisons, e.g. `assert action.action_type in [ActionType.TARIFF_INCREASE, ...]`

- [x] **6.3** Add action-type handling tests  
  **File:** `tests/test_simulation.py`  
  **Add:** One test per new action type verifying that when the engine processes that action, the expected economic change occurs (GDP delta, trade flow delta, or state mutation). Focus on: `TECH_EXPORT_CONTROL`, `INDUSTRIAL_SUBSIDY`, `SUPPLY_CHAIN_DIVERSIFICATION`, `GREEN_TECH_INVESTMENT`.

- [x] **6.4** Add policy/event expiration tests  
  **File:** `tests/test_economics.py`  
  **Add:** Test that creates a state with an expired `TariffPolicy` (end_date in the past) and a `duration_quarters=1` event that has been active for 2 quarters, calls `_remove_expired_items()`, and asserts both were removed from state.

- [x] **6.5** Add dynamic indicator tests  
  **File:** `tests/test_economics.py`  
  **Add:** Test that sets up a state with a high-tariff shock, runs `finalize_update()`, and asserts that `inflation > 0.025` (base) and `consumer_confidence < 100`. Verifies the placeholder replacements from task 2.3 are working.

- [x] **6.6** Add API integration tests  
  **File:** `tests/test_api.py` (new file)  
  **Add:** Using FastAPI's `TestClient`:
  - `POST /api/simulation/start` → verify 200 and returns a `sim_id`
  - `GET /api/simulation/{sim_id}/status` → verify 200 and state structure
  - `POST /api/simulation/{sim_id}/step` → verify 200
  - `GET /api/results/{sim_id}` → verify 200 and results structure
  - `GET /api/simulation/nonexistent/status` → verify 404

- [x] **6.7** Add edge-case tests  
  **File:** `tests/test_economics.py`  
  **Add:**
  - Zero-GDP country: verify `calculate_gdp_impact` doesn't divide by zero
  - Empty country list: verify `SimulationEngine([])` raises `ValueError` cleanly
  - Negative tariff rates: verify `calculate_tariff_impact` handles negative rates (tariff decrease) without negative volumes
  - Missing sector in trade flow: verify `_calculate_updated_trade_flow` skips gracefully when policy references a sector not in the flow

---

## Verification Checkpoints

| After Phase | Command | Expected outcome |
|-------------|---------|-----------------|
| 1 | `pytest tests/ -v` | All existing tests pass (with updated enum assertions) |
| 2 | `python scripts/run_simulation.py` | GDP values change non-uniformly across quarters; different countries show different growth rates |
| 3 | `pytest tests/test_agents.py -v` | Agent tests pass; verify LLM fallback path works |
| 4 | `python -c "from tradewar.llm.client import LLMClient; c = LLMClient('test'); print('ok')"` | No import errors |
| 5 | `python scripts/run_api.py` then `curl http://localhost:8000/docs` | Swagger UI loads; no import errors |
| 5 | `curl -X POST http://localhost:8000/api/simulation/start -H 'Content-Type: application/json' -d '{"countries": [...]}'` | Returns `{"simulation_id": "sim_1", ...}` |
| 6 | `pytest tests/ -v --tb=short` | 0 failures |
| 6 | `pytest tests/ -x --count=3` (with pytest-repeat) | 0 flaky tests across 3 runs |

---

## Dependency Graph

```
1.1 ──► 1.4
1.2 ──► 3.1, 3.3, 6.2
1.3 ──► 1.4
1.4   (independent after 1.1, 1.3)
1.6 ──► 6.1

2.1 ──► 2.2, 2.3
2.2 ──► 2.3 (gdp.py must be wired before indicators can use its output)
2.3 ──► 6.5
2.4 ──► 3.3, 6.3 (action types must be handled before new fallback logic or tests)
2.5   (independent)

3.1 ──► 3.2
3.2 ──► 3.3
4.1, 4.2 ──► 4.3

5.1 ──► 5.2 ──► 5.3, 6.6
5.4, 5.5   (independent)
```

> **Recommended order within each phase:** strictly top-to-bottom as listed.  
> Phases 3 and 4 can be worked in parallel after Phase 2.  
> Phase 5 can be worked in parallel after Phase 1.  
> Phase 6 should be the last thing done in each phase as a sign-off step.
