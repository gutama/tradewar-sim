"""US-specific prompt additions focused on Trump administration policies."""

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
    Generate a prompt for US policy decisions with Trump administration focus.
    
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
    
    # US Trump-specific additions
    trump_policy_focus = """
TRUMP ADMINISTRATION POLICY PRIORITIES
- America First: Prioritizing US economic interests above global considerations
- Trade Deficit Reduction: Particular focus on reducing deficits with China and other major partners
- Manufacturing Revival: Protecting and growing US manufacturing jobs
- Aggressive Bargaining: Using tariffs as leverage to negotiate better trade deals
- Bilateral over Multilateral: Preference for direct country-to-country negotiations
- Protectionism: Willingness to use tariffs and other measures to protect US industries
- Less Concern for WTO: Skepticism of multilateral trade institutions and their rules
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
You are a strategic advisor to the Trump administration on international trade policy.
Based on the information provided, recommend a specific trade action that aligns with
the administration's priorities.

{simulation_context}

{economic_context}

{country_context}

{trump_policy_focus}

{policy_history}

INSTRUCTIONS:
Recommend ONE specific trade policy action the US should take this quarter.
Your response should be structured as follows:

ACTION: [tariff_increase, tariff_decrease, investment, export_subsidy, status_quo]
TARGET_COUNTRY: [country name, or "none" if not targeting a specific country]
SECTORS: [comma-separated list of affected economic sectors]
MAGNITUDE: [numerical percentage between 0-100]
JUSTIFICATION: [2-3 sentence explanation aligned with Trump's policy priorities]
EXPECTED_OUTCOMES: [brief description of expected results]
"""
    
    return decision_prompt
