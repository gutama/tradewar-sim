"""Base prompt structure for LLM interactions in the trade war simulation."""

from typing import Dict, List, Optional

from tradewar.economics.models import Country, EconomicAction
from tradewar.simulation.state import SimulationState


def create_simulation_context(state: SimulationState) -> str:
    """
    Create a context description of the current simulation state.
    
    Args:
        state: Current simulation state
    
    Returns:
        String with context about the simulation
    """
    context = f"""
SIMULATION CONTEXT
Year: {state.year + 2023}, Quarter: {state.quarter + 1}

Current global economic situation:
- Global economic cycle status: {"expansion" if (state.year * 4 + state.quarter) % 20 < 10 else "contraction"}
- Recent significant events: {_format_events(state.active_events)}
- Ongoing trade tensions: {_format_tensions(state)}

Countries in simulation:
{_format_countries(state.countries)}

Recent trade actions:
{_format_recent_actions(state.recent_actions)}
"""
    return context


def create_economic_context(state: SimulationState, country: Country) -> str:
    """
    Create a context description of a country's economic state.
    
    Args:
        state: Current simulation state
        country: The country to describe
    
    Returns:
        String with economic context
    """
    # Get country indicators
    indicators = state.economic_indicators.get(country.name, [])
    
    if not indicators:
        return f"No economic data available for {country.name}."
    
    latest = indicators[-1]
    
    # Get trade balances with other countries
    trade_balance_text = ""
    for partner_name, balance in latest.trade_balance.items():
        status = "surplus" if balance > 0 else "deficit"
        trade_balance_text += f"- {partner_name}: {abs(balance):.1f} billion USD {status}\n"
    
    # Get active tariff policies against this country
    incoming_tariffs = [
        policy for policy in state.active_tariff_policies
        if policy.target_country.name == country.name
    ]
    
    incoming_tariffs_text = ""
    for policy in incoming_tariffs:
        avg_rate = sum(policy.sector_rates.values()) / len(policy.sector_rates)
        incoming_tariffs_text += f"- {policy.source_country.name}: {avg_rate:.1%} average tariff rate\n"
    
    context = f"""
ECONOMIC CONTEXT FOR {country.name}
Current economic indicators:
- GDP: {country.gdp:.1f} trillion USD
- GDP Growth: {latest.gdp_growth:.2%} (annualized)
- Inflation: {latest.inflation:.2%}
- Unemployment: {latest.unemployment:.2%}
- Consumer Confidence: {latest.consumer_confidence:.1f}/100
- Business Confidence: {latest.business_confidence:.1f}/100
- Currency Value Index: {latest.currency_value:.2f} (1.00 = baseline)

Trade balances:
{trade_balance_text}

Incoming tariffs:
{incoming_tariffs_text or "No significant tariffs imposed on this country."}
"""
    return context


def create_country_context(country: Country) -> str:
    """
    Create a context description of a country's characteristics.
    
    Args:
        country: The country to describe
    
    Returns:
        String with country context
    """
    # Country-specific descriptions
    descriptions = {
        "US": """
The United States is the world's largest economy with significant influence in global trade.
Key economic characteristics:
- Strong focus on services, technology, and advanced manufacturing
- Major exports: machinery, electronics, aircraft, vehicles, pharmaceuticals
- Major imports: consumer goods, vehicles, machinery, oil
- Political factors: America First policies, focus on trade deficit reduction
- Strategic priorities: protecting intellectual property, maintaining technological edge
""",
        "China": """
China is the world's second-largest economy and a manufacturing powerhouse.
Key economic characteristics:
- Focus on manufacturing, increasingly moving toward high-tech and services
- Major exports: electronics, machinery, textiles, furniture, plastics
- Major imports: oil, electronic components, machinery, minerals
- Political factors: state-directed economic development, industrial policies
- Strategic priorities: technological advancement, export market growth, domestic consumption
""",
        "Indonesia": """
Indonesia is Southeast Asia's largest economy with significant natural resources.
Key economic characteristics:
- Focus on natural resources, agriculture, and growing manufacturing
- Major exports: palm oil, coal, natural gas, rubber, electronics
- Major imports: machinery, chemicals, fuels, foodstuffs
- Political factors: economic nationalism, balancing relations with major powers
- Strategic priorities: infrastructure development, value-added industry growth
"""
    }
    
    return descriptions.get(country.name, f"No detailed context available for {country.name}.")


def _format_countries(countries: List[Country]) -> str:
    """Format a list of countries with key economic data."""
    result = ""
    for country in countries:
        result += f"- {country.name}: GDP ${country.gdp:.1f} trillion, "
        result += f"Population {country.population/1e6:.1f}M, "
        result += f"Inflation {country.inflation_rate:.1%}, "
        result += f"Unemployment {country.unemployment_rate:.1%}\n"
    return result


def _format_recent_actions(actions: List[EconomicAction]) -> str:
    """Format a list of recent economic actions."""
    if not actions:
        return "No significant recent actions."
    
    result = ""
    for action in actions[-5:]:  # Show only the 5 most recent actions
        target = f" against {action.target_country.name}" if action.target_country else ""
        sectors = f" in {', '.join(action.sectors)}" if action.sectors else ""
        result += f"- {action.country.name} implemented {action.action_type}{target}{sectors} "
        result += f"({action.magnitude:.1%} magnitude). Justification: {action.justification}\n"
    return result


def _format_events(events: List[dict]) -> str:
    """Format a list of active events."""
    if not events:
        return "No significant events."
    
    result = ""
    for event in events:
        countries = ", ".join(event.affected_countries)
        result += f"- {event.name}: Affecting {countries}. {event.description}\n"
    return result


def _format_tensions(state: SimulationState) -> str:
    """Format information about trade tensions between countries."""
    # Look for countries with active tariff policies against each other
    tensions = []
    
    for policy in state.active_tariff_policies:
        source = policy.source_country.name
        target = policy.target_country.name
        avg_rate = sum(policy.sector_rates.values()) / len(policy.sector_rates)
        
        # Check if there's a corresponding policy in the opposite direction
        reverse_policies = [
            p for p in state.active_tariff_policies
            if p.source_country.name == target and p.target_country.name == source
        ]
        
        if reverse_policies:
            reverse_avg = sum(reverse_policies[0].sector_rates.values()) / len(reverse_policies[0].sector_rates)
            tensions.append(f"{source}-{target} bilateral tariffs ({avg_rate:.1%} vs {reverse_avg:.1%})")
        else:
            tensions.append(f"{source} imposing {avg_rate:.1%} tariffs on {target}")
    
    if not tensions:
        return "No major trade tensions observed."
    
    return ", ".join(tensions)
