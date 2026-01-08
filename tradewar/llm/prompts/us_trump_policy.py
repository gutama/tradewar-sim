"""US-specific prompt additions for trade policy decisions (2024-2026 era).

This module generates prompts for US trade policy reflecting current strategic
priorities including technology competition with China, industrial policy,
supply chain resilience, and green technology leadership.

Note: The filename 'us_trump_policy' is retained for backward compatibility,
but the implementation now reflects broader US trade policy beyond any single
administration, covering the 2024-2026 era strategic priorities.
"""

from typing import List

from tradewar.economics.models import Country, EconomicAction
from tradewar.llm.prompts.base_prompt import (create_country_context,
                                             create_economic_context,
                                             create_simulation_context)
from tradewar.simulation.state import SimulationState


def generate_us_policy_prompt(
    state: SimulationState,
    country: Country,
    previous_actions: List[EconomicAction]
) -> str:
    """
    Generate a prompt for US policy decisions reflecting current era (2024-2026) policies.
    
    Args:
        state: Current simulation state
        country: The US country object
        previous_actions: Previous actions taken by this country
        
    Returns:
        Prompt for LLM to generate US policy decisions
    """
    # Build context from base prompts
    simulation_context = create_simulation_context(state)
    economic_context = create_economic_context(state, country)
    country_context = create_country_context(country)
    
    # US policy focus - updated for 2024-2026 era
    us_policy_focus = """
US TRADE POLICY PRIORITIES (2024-2026 ERA)
- Strategic Competition with China: Focus on technology leadership, semiconductors, and AI
- Industrial Policy: Major subsidies for domestic manufacturing (CHIPS Act, IRA)
- Supply Chain Resilience: "Friend-shoring" and nearshoring to reduce China dependencies
- Green Technology Race: Leading in EVs, batteries, solar panels, and clean energy
- Technology Export Controls: Restricting advanced chip and AI technology exports
- Allied Cooperation: Working with allies (EU, Japan, South Korea) on coordinated approaches
- Critical Minerals Security: Ensuring access to rare earths and battery materials
- Data Sovereignty: Protecting digital infrastructure and limiting foreign tech access
- Worker-Centered Trade: Focus on labor standards and middle-class benefits
- Selective Tariffs: Targeted tariffs on strategic sectors rather than broad-based
"""
    
    # Previous policy continuity
    policy_history = "PREVIOUS POLICY ACTIONS\n"
    if previous_actions:
        for action in previous_actions[-5:]:  # Last 5 actions
            target = f" against {action.target_country.name}" if action.target_country else ""
            sectors = f" in {', '.join(action.sectors)}" if action.sectors else ""
            policy_history += f"- {action.action_type}{target}{sectors} "
            policy_history += f"({action.magnitude:.1%} magnitude). Justification: {action.justification}\n"
    else:
        policy_history += "No significant previous policy actions taken.\n"
    
    # Build the decision prompt
    decision_prompt = f"""
You are a strategic advisor to the US government on international trade policy.
Based on the information provided, recommend a specific trade action that aligns with
current US strategic priorities.

{simulation_context}

{economic_context}

{country_context}

{us_policy_focus}

{policy_history}

INSTRUCTIONS:
Recommend ONE specific trade policy action the US should take this quarter.
Your response should be structured as follows:

ACTION: [tariff_increase, tariff_decrease, investment, export_subsidy, tech_export_control, industrial_subsidy, supply_chain_diversification, green_tech_investment, friend_shoring, status_quo]
TARGET_COUNTRY: [country name, or "none" if not targeting a specific country]
SECTORS: [comma-separated list of affected economic sectors - can include: semiconductors, ai, green_tech, batteries, automotive, etc.]
MAGNITUDE: [numerical percentage between 0-100]
JUSTIFICATION: [2-3 sentence explanation aligned with current US policy priorities]
EXPECTED_OUTCOMES: [brief description of expected results]
"""
    
    return decision_prompt
