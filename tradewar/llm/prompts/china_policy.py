"""China-specific prompt additions for trade policy decisions."""

from typing import List

from tradewar.economics.models import Country, EconomicAction
from tradewar.llm.prompts.base_prompt import (create_country_context,
                                             create_economic_context,
                                             create_simulation_context)
from tradewar.simulation.state import SimulationState


def generate_china_policy_prompt(
    state: SimulationState,
    country: Country,
    previous_actions: List[EconomicAction]
) -> str:
    """
    Generate a prompt for China policy decisions.
    
    Args:
        state: Current simulation state
        country: The China country object
        previous_actions: Previous actions taken by this country
        
    Returns:
        Prompt for LLM to generate China policy decisions
    """
    # Build context from base prompts
    simulation_context = create_simulation_context(state)
    economic_context = create_economic_context(state, country)
    country_context = create_country_context(country)
    
    # China-specific additions
    china_policy_focus = """
CHINESE GOVERNMENT POLICY PRIORITIES
- Economic Stability: Maintaining GDP growth targets and social stability
- Made in China 2025: Advancing technological self-sufficiency in key industries
- Export Market Access: Preserving access to major export markets, especially the US and EU
- Controlled Retaliation: Responding to trade aggression while avoiding excessive escalation
- Strategic Resources: Securing supply chains for critical resources and components
- Political Considerations: Balancing economic pragmatism with nationalistic sentiment
- Belt and Road Initiative: Expanding economic influence in developing markets
- Dual Circulation: Developing domestic consumption while maintaining export strength
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
You are a senior advisor to the Chinese government on international trade policy.
Based on the information provided, recommend a specific trade action that aligns with
China's strategic economic and political interests.

{simulation_context}

{economic_context}

{country_context}

{china_policy_focus}

{policy_history}

INSTRUCTIONS:
Recommend ONE specific trade policy action China should take this quarter.
Your response should be structured as follows:

ACTION: [tariff_increase, tariff_decrease, investment, export_subsidy, currency_devaluation, status_quo]
TARGET_COUNTRY: [country name, or "none" if not targeting a specific country]
SECTORS: [comma-separated list of affected economic sectors]
MAGNITUDE: [numerical percentage between 0-100]
JUSTIFICATION: [2-3 sentence explanation aligned with Chinese policy priorities]
EXPECTED_OUTCOMES: [brief description of expected results]
"""
    
    return decision_prompt
