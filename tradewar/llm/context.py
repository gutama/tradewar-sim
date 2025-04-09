def create_country_context(country: Country) -> str:
    """Create context for a country based on its attributes."""
    if country.name == "US":
        return f"""
The United States ({country.name}) is the world's largest economy with significant influence in global trade.
Key economic characteristics:
- GDP: ${country.gdp} trillion
- Major sectors: technology, services, manufacturing
- Trade policy: focus on trade deficit reduction
- Strategic priorities: protecting intellectual property, maintaining technological edge
"""
    elif country.name == "China":
        return f"""
China ({country.name}) is the world's second-largest economy with rapidly growing global influence.
Key economic characteristics:
- GDP: ${country.gdp} trillion
- Major sectors: manufacturing, technology, agriculture
- Trade policy: export-driven growth, developing domestic consumption
- Strategic priorities: technological self-sufficiency, Belt and Road Initiative
"""
    elif country.name == "Indonesia":
        return f"""
Indonesia ({country.name}) is Southeast Asia's largest economy and an emerging middle power.
Key economic characteristics:
- GDP: ${country.gdp} trillion
- Major sectors: natural resources, agriculture, manufacturing, services
- Trade policy: balancing relations with major powers, regional integration
- Strategic priorities: infrastructure development, economic diversification
"""
    else:
        return f"""
{country.name} is a participant in the global economy.
GDP: ${country.gdp} trillion
"""