"""Indonesia-specific prompt additions for trade policy decisions."""

from typing import List

from tradewar.economics.models import Country, EconomicAction
from tradewar.llm.prompts.base_prompt import (create_country_context,
                                             create_economic_context,
                                             create_simulation_context)
from tradewar.simulation.state import SimulationState


def generate_indonesia_policy_prompt(
    state: SimulationState,
    country: Country,
    previous_actions: List[EconomicAction]
) -> str:
    """
    Generate a prompt for Indonesia policy decisions.
    
    Args:
        state: Current simulation state
        country: The Indonesia country object
        previous_actions: Previous actions taken by this country
        
    Returns:
        Prompt for LLM to generate Indonesia policy decisions
    """
    # Build context from base prompts
    simulation_context = create_simulation_context(state)
    economic_context = create_economic_context(state, country)
    country_context = create_country_context(country)
    
    # Indonesia-specific additions
    indonesia_policy_focus = """
INDONESIAN GOVERNMENT POLICY PRIORITIES
- Economic Development: Focus on sustained economic growth and poverty reduction
- Resource Nationalism: Protecting natural resource industries and increasing value added
- Balancing Great Powers: Navigating US-China tensions while maintaining relations with both
- ASEAN Integration: Strengthening regional economic ties within Southeast Asia
- Domestic Industry Protection: Selective protectionism for strategic industries
- Foreign Investment: Attracting investment while maintaining economic sovereignty
- Palm Oil Exports: Protecting access to markets for key agricultural exports
- Infrastructure Development: Building necessary infrastructure for economic growth
- Tourism Development: Growing the tourism sector as a source of foreign exchange
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
    
    # Special context: US-China trade war impacts
    us_china_context = _analyze_us_china_dynamics(state)
    
    # Build the decision prompt
    decision_prompt = f"""
You are a senior economic advisor to the Indonesian government.
Based on the information provided, recommend a specific trade action that benefits
Indonesia's economy, especially in the context of US-China trade tensions.

{simulation_context}

{economic_context}

{country_context}

{indonesia_policy_focus}

{us_china_context}

{policy_history}

INSTRUCTIONS:
Recommend ONE specific trade policy action Indonesia should take this quarter.
Your response should be structured as follows:

ACTION: [tariff_increase, tariff_decrease, investment, export_subsidy, import_quota, status_quo]
TARGET_COUNTRY: [country name, or "none" if not targeting a specific country]
SECTORS: [comma-separated list of affected economic sectors]
MAGNITUDE: [numerical percentage between 0-100]
JUSTIFICATION: [2-3 sentence explanation aligned with Indonesian policy priorities]
EXPECTED_OUTCOMES: [brief description of expected results]
"""
    
    return decision_prompt


def _analyze_us_china_dynamics(state: SimulationState) -> str:
    """Analyze US-China trade war dynamics for Indonesian context."""
    us_actions = [
        action for action in state.recent_actions 
        if action.country.name == "US" and action.target_country and 
        action.target_country.name == "China"
    ]
    
    china_actions = [
        action for action in state.recent_actions 
        if action.country.name == "China" and action.target_country and 
        action.target_country.name == "US"
    ]
    
    if not us_actions and not china_actions:
        return """
US-CHINA TRADE DYNAMICS
Currently, there are no significant trade tensions between the US and China that
create immediate opportunities or threats for Indonesia.
"""
    
    # Analyze tension level
    tension_level = "high" if (us_actions and china_actions) else "moderate"
    
    # Identify potential opportunities
    opportunities = []
    
    if any(action.action_type == "tariff_increase" for action in us_actions):
        affected_sectors = set()
        for action in us_actions:
            if action.action_type == "tariff_increase":
                affected_sectors.update(action.sectors)
        
        opportunities.append(
            f"Potential to replace Chinese exports to US in: {', '.join(affected_sectors)}"
        )
    
    if any(action.action_type == "tariff_increase" for action in china_actions):
        affected_sectors = set()
        for action in china_actions:
            if action.action_type == "tariff_increase":
                affected_sectors.update(action.sectors)
        
        opportunities.append(
            f"Potential to replace US exports to China in: {', '.join(affected_sectors)}"
        )
    
    opportunities_text = "\n- ".join([""] + opportunities) if opportunities else "\nNo clear opportunities identified."
    
    return f"""
US-CHINA TRADE DYNAMICS
Current tension level: {tension_level.upper()}
Recent US actions: {len(us_actions)} trade measures against China
Recent China actions: {len(china_actions)} trade measures against US

Potential opportunities for Indonesia:{opportunities_text}

Strategic considerations:
- Maintaining neutrality while benefiting from trade diversion
- Avoiding being caught in retaliatory measures
- Potential to attract manufacturing relocating from China
"""
