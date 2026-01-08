"""
Example scenarios demonstrating 2024-2026 trade war features.

This script shows how to use the new action types, sectors, and events
to model modern trade dynamics including technology competition,
green tech races, and supply chain restructuring.
"""

from tradewar.economics.models import (
    ActionType,
    Country,
    EconomicAction,
)
from tradewar.simulation.engine import SimulationEngine
from tradewar.simulation.state import SimulationState


def scenario_1_us_china_tech_war():
    """
    Scenario 1: US-China Technology Export Controls
    
    Models the strategic competition in semiconductors and AI,
    with US imposing export controls and China retaliating.
    """
    print("\n" + "="*70)
    print("SCENARIO 1: US-China Technology Export Controls")
    print("="*70 + "\n")
    
    # Initialize countries
    us = Country(
        name="US",
        gdp=25.0,
        population=335000000,
        sectors={
            "semiconductors": 0.15,
            "ai": 0.20,
            "technology": 0.25,
        }
    )
    
    china = Country(
        name="China",
        gdp=17.0,
        population=1400000000,
        sectors={
            "semiconductors": 0.10,
            "manufacturing": 0.35,
            "technology": 0.15,
        }
    )
    
    # US Action: Technology export controls on advanced chips
    us_action = EconomicAction(
        country=us,
        action_type=ActionType.TECH_EXPORT_CONTROL,
        target_country=china,
        sectors=["semiconductors", "ai"],
        magnitude=0.85,  # 85% restriction
        justification=(
            "Restricting exports of advanced semiconductors (sub-7nm) and AI chips "
            "to protect national security and maintain technological advantage"
        )
    )
    
    print("US ACTION:")
    print(f"  Type: {us_action.action_type}")
    print(f"  Target: {us_action.target_country.name}")
    print(f"  Sectors: {', '.join(us_action.sectors)}")
    print(f"  Magnitude: {us_action.magnitude:.0%}")
    print(f"  Justification: {us_action.justification}\n")
    
    # China Retaliation: Export controls on rare earth minerals
    china_action = EconomicAction(
        country=china,
        action_type=ActionType.TECH_EXPORT_CONTROL,
        target_country=us,
        sectors=["rare_earths", "critical_minerals"],
        magnitude=0.60,  # 60% restriction
        justification=(
            "Retaliatory export restrictions on rare earth elements critical "
            "for semiconductors, EVs, and defense systems"
        )
    )
    
    print("CHINA RETALIATION:")
    print(f"  Type: {china_action.action_type}")
    print(f"  Target: {china_action.target_country.name}")
    print(f"  Sectors: {', '.join(china_action.sectors)}")
    print(f"  Magnitude: {china_action.magnitude:.0%}")
    print(f"  Justification: {china_action.justification}\n")
    
    print("EXPECTED OUTCOMES:")
    print("  - US maintains technological edge in advanced chips")
    print("  - China accelerates domestic semiconductor development")
    print("  - Global tech supply chains fragment")
    print("  - Innovation costs increase for both sides")
    print("  - Third countries (Taiwan, S. Korea, Japan) gain leverage\n")


def scenario_2_green_tech_subsidy_race():
    """
    Scenario 2: Green Technology Subsidy Competition
    
    Models the competition between US and China in EVs, batteries,
    and renewable energy through massive industrial subsidies.
    """
    print("\n" + "="*70)
    print("SCENARIO 2: Green Technology Subsidy Race")
    print("="*70 + "\n")
    
    us = Country(name="US", gdp=25.0)
    china = Country(name="China", gdp=17.0)
    
    # US Action: IRA-style green tech subsidies
    us_subsidy = EconomicAction(
        country=us,
        action_type=ActionType.GREEN_TECH_INVESTMENT,
        sectors=["green_tech", "batteries", "automotive"],
        magnitude=0.50,  # 50% subsidy level
        justification=(
            "Inflation Reduction Act subsidies for domestic EV production, "
            "battery manufacturing, and clean energy to compete with China"
        )
    )
    
    print("US GREEN TECH INVESTMENT:")
    print(f"  Type: {us_subsidy.action_type}")
    print(f"  Sectors: {', '.join(us_subsidy.sectors)}")
    print(f"  Magnitude: {us_subsidy.magnitude:.0%}")
    print(f"  Justification: {us_subsidy.justification}\n")
    
    # China Action: Aggressive industrial subsidies
    china_subsidy = EconomicAction(
        country=china,
        action_type=ActionType.INDUSTRIAL_SUBSIDY,
        sectors=["green_tech", "batteries", "automotive", "solar"],
        magnitude=0.65,  # 65% subsidy level
        justification=(
            "Comprehensive industrial subsidies to dominate global EV, "
            "battery, and solar panel markets through scale and cost advantages"
        )
    )
    
    print("CHINA INDUSTRIAL SUBSIDIES:")
    print(f"  Type: {china_subsidy.action_type}")
    print(f"  Sectors: {', '.join(china_subsidy.sectors)}")
    print(f"  Magnitude: {china_subsidy.magnitude:.0%}")
    print(f"  Justification: {china_subsidy.justification}\n")
    
    print("EXPECTED OUTCOMES:")
    print("  - Accelerated global green technology adoption")
    print("  - Trade tensions over green tech subsidies")
    print("  - China maintains cost leadership in batteries and EVs")
    print("  - US builds domestic green tech manufacturing capacity")
    print("  - Europe caught between competing subsidy regimes\n")


def scenario_3_indonesia_nearshoring_opportunity():
    """
    Scenario 3: Indonesia Benefits from Supply Chain Diversification
    
    Models how Indonesia attracts manufacturing from China as companies
    pursue "China+1" strategies and nearshoring.
    """
    print("\n" + "="*70)
    print("SCENARIO 3: Indonesia Nearshoring Opportunity")
    print("="*70 + "\n")
    
    us = Country(name="US", gdp=25.0)
    china = Country(name="China", gdp=17.0)
    indonesia = Country(
        name="Indonesia",
        gdp=1.2,
        population=275000000,
        sectors={
            "mining": 0.15,
            "manufacturing": 0.20,
            "agriculture": 0.12,
        }
    )
    
    # US Action: Friend-shoring to Indonesia
    us_friendshoring = EconomicAction(
        country=us,
        action_type=ActionType.FRIEND_SHORING,
        target_country=indonesia,
        sectors=["electronics", "manufacturing", "textiles"],
        magnitude=0.35,  # 35% of supply chains
        justification=(
            "Relocating electronics and manufacturing supply chains to Indonesia "
            "as part of China+1 strategy and Indo-Pacific Economic Framework"
        )
    )
    
    print("US FRIEND-SHORING INITIATIVE:")
    print(f"  Type: {us_friendshoring.action_type}")
    print(f"  Target: {us_friendshoring.target_country.name}")
    print(f"  Sectors: {', '.join(us_friendshoring.sectors)}")
    print(f"  Magnitude: {us_friendshoring.magnitude:.0%}")
    print(f"  Justification: {us_friendshoring.justification}\n")
    
    # Indonesia Action: Attract manufacturing with strategic investments
    indonesia_action = EconomicAction(
        country=indonesia,
        action_type=ActionType.SUPPLY_CHAIN_DIVERSIFICATION,
        sectors=["electronics", "batteries", "rare_earths"],
        magnitude=0.40,  # 40% investment increase
        justification=(
            "Strategic investments in infrastructure, skills, and incentives "
            "to position Indonesia as alternative manufacturing hub to China"
        )
    )
    
    print("INDONESIA STRATEGIC RESPONSE:")
    print(f"  Type: {indonesia_action.action_type}")
    print(f"  Sectors: {', '.join(indonesia_action.sectors)}")
    print(f"  Magnitude: {indonesia_action.magnitude:.0%}")
    print(f"  Justification: {indonesia_action.justification}\n")
    
    # Indonesia leverages critical minerals
    indonesia_minerals = EconomicAction(
        country=indonesia,
        action_type=ActionType.INDUSTRIAL_SUBSIDY,
        sectors=["rare_earths", "batteries", "mining"],
        magnitude=0.45,  # 45% support
        justification=(
            "Subsidizing nickel processing and battery manufacturing to move "
            "up the value chain from raw materials to finished products"
        )
    )
    
    print("INDONESIA CRITICAL MINERALS STRATEGY:")
    print(f"  Type: {indonesia_minerals.action_type}")
    print(f"  Sectors: {', '.join(indonesia_minerals.sectors)}")
    print(f"  Magnitude: {indonesia_minerals.magnitude:.0%}")
    print(f"  Justification: {indonesia_minerals.justification}\n")
    
    print("EXPECTED OUTCOMES:")
    print("  - Indonesia GDP growth accelerates (5-7% annually)")
    print("  - Manufacturing employment increases significantly")
    print("  - Indonesia becomes key battery supply chain hub")
    print("  - Reduced Chinese manufacturing dominance")
    print("  - Strategic importance of Indonesia rises\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TRADE WAR SIMULATION - 2024-2026 SCENARIOS")
    print("Demonstrating modern trade dynamics including tech competition,")
    print("green tech races, and supply chain restructuring")
    print("="*70)
    
    # Run all scenarios
    scenario_1_us_china_tech_war()
    scenario_2_green_tech_subsidy_race()
    scenario_3_indonesia_nearshoring_opportunity()
    
    print("\n" + "="*70)
    print("All scenarios completed!")
    print("See TRADE_WAR_2024_UPDATES.md for more information")
    print("="*70 + "\n")
