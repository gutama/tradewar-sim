"""Streamlit dashboard for visualizing trade war simulation results."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
from plotly.subplots import make_subplots

from tradewar.config import config
from tradewar.visualization.plots import (create_gdp_plot, create_tariff_heatmap,
                                         create_trade_balance_plot,
                                         create_trade_network_graph)

# API connection settings
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", config.api.port)
API_URL = f"http://{API_HOST}:{API_PORT}"


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Trade War Simulation Dashboard",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title("Trade War Simulation Dashboard")
    st.sidebar.header("Controls")
    
    # Check if API is available
    try:
        response = requests.get(f"{API_URL}/")
        api_available = True
    except:
        api_available = False
    
    if not api_available:
        st.error(
            f"Cannot connect to API at {API_URL}. "
            "Make sure the API server is running."
        )
        return
    
    # Sidebar controls
    st.sidebar.subheader("Simulation Control")
    
    # Active simulations dropdown
    active_simulations = _get_active_simulations()
    
    if not active_simulations:
        simulation_id = "new"
        st.sidebar.info("No active simulations. Start a new one.")
    else:
        simulation_options = ["new"] + active_simulations
        simulation_id = st.sidebar.selectbox(
            "Select Simulation", 
            options=simulation_options,
            format_func=lambda x: "Start New Simulation" if x == "new" else f"Simulation {x}"
        )
    
    # If starting a new simulation, show configuration options
    if simulation_id == "new":
        _show_new_simulation_form()
        return
    
    # If using existing simulation, show controls and results
    _show_simulation_controls(simulation_id)
    _show_simulation_results(simulation_id)


def _get_active_simulations() -> List[str]:
    """Get list of active simulations from the API."""
    try:
        # This endpoint would need to be implemented in the API
        response = requests.get(f"{API_URL}/api/simulations")
        return response.json()
    except:
        # If there's an error or the endpoint doesn't exist yet
        return []


def _show_new_simulation_form():
    """Show form for creating a new simulation."""
    st.header("Start New Simulation")
    
    with st.form("simulation_config"):
        # Basic simulation parameters
        col1, col2 = st.columns(2)
        with col1:
            years = st.number_input("Simulation Years", min_value=1, max_value=20, value=5)
            steps_per_year = st.number_input("Steps Per Year", min_value=1, max_value=12, value=4)
        
        with col2:
            random_seed = st.number_input("Random Seed", min_value=0, value=42)
            use_events = st.checkbox("Enable Random Events", value=True)
        
        # Country selection
        st.subheader("Countries")
        include_us = st.checkbox("United States", value=True)
        include_china = st.checkbox("China", value=True)
        include_indonesia = st.checkbox("Indonesia", value=True)
        
        # Advanced options (collapsed by default)
        with st.expander("Advanced Configuration"):
            us_aggression = st.slider(
                "US Protectionist Tendency", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.7 if include_us else 0.0,
                step=0.1
            )
            
            china_retaliation = st.slider(
                "China Retaliatory Factor", 
                min_value=0.0, 
                max_value=1.5, 
                value=1.0 if include_china else 0.0,
                step=0.1
            )
            
            indo_protection = st.slider(
                "Indonesia Protectionist Tendency", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.5 if include_indonesia else 0.0,
                step=0.1
            )
        
        submit = st.form_submit_button("Start Simulation")
    
    if submit:
        # Collect countries
        countries = []
        if include_us:
            countries.append({
                "name": "US",
                "gdp": 21.0,
                "population": 330000000,
                "inflation_rate": 0.02,
                "unemployment_rate": 0.04,
                "currency_value": 1.0,
                "strategy_params": {"is_aggressive": us_aggression > 0.5}
            })
        
        if include_china:
            countries.append({
                "name": "China",
                "gdp": 15.0,
                "population": 1400000000,
                "inflation_rate": 0.025,
                "unemployment_rate": 0.05,
                "currency_value": 1.0,
                "strategy_params": {"retaliatory_factor": china_retaliation}
            })
        
        if include_indonesia:
            countries.append({
                "name": "Indonesia",
                "gdp": 1.0,
                "population": 270000000,
                "inflation_rate": 0.03,
                "unemployment_rate": 0.06,
                "currency_value": 1.0,
                "strategy_params": {"protectionist_tendency": indo_protection}
            })
        
        if not countries:
            st.error("Please select at least one country for the simulation.")
            return
        
        # Create simulation configuration
        config = {
            "years": years,
            "steps_per_year": steps_per_year,
            "random_seed": random_seed,
            "countries": countries,
            "enable_events": use_events
        }
        
        # Start the simulation
        try:
            response = requests.post(f"{API_URL}/api/simulation/start", json=config)
            if response.status_code == 200:
                simulation_id = response.json()
                st.success(f"Simulation started with ID: {simulation_id}")
                st.experimental_rerun()
            else:
                st.error(f"Failed to start simulation: {response.text}")
        except Exception as e:
            st.error(f"Error starting simulation: {str(e)}")


def _show_simulation_controls(simulation_id: str):
    """Show controls for an existing simulation."""
    st.sidebar.subheader("Simulation Actions")
    
    # Get current state
    state = _get_simulation_state(simulation_id)
    
    if not state:
        st.error(f"Could not retrieve state for simulation {simulation_id}")
        return
    
    # Display current time
    st.sidebar.write(f"Year: {state['year'] + 2023}, Quarter: {state['quarter'] + 1}")
    
    # Step simulation button
    if st.sidebar.button("Advance One Quarter"):
        try:
            response = requests.post(f"{API_URL}/api/simulation/{simulation_id}/step")
            if response.status_code == 200:
                st.sidebar.success("Advanced simulation by one quarter")
                # Force refresh
                st.experimental_rerun()
            else:
                st.sidebar.error(f"Failed to advance simulation: {response.text}")
        except Exception as e:
            st.sidebar.error(f"Error advancing simulation: {str(e)}")
    
    # Auto-run options
    with st.sidebar.expander("Auto-run Settings"):
        auto_steps = st.number_input("Number of steps", min_value=1, max_value=20, value=4)
        auto_delay = st.slider("Delay between steps (sec)", min_value=1, max_value=10, value=2)
        auto_run = st.button("Run Multiple Steps")
    
    if auto_run:
        progress_bar = st.sidebar.progress(0)
        for i in range(auto_steps):
            try:
                response = requests.post(f"{API_URL}/api/simulation/{simulation_id}/step")
                if response.status_code != 200:
                    st.sidebar.error(f"Failed at step {i+1}: {response.text}")
                    break
                
                # Update progress
                progress = (i + 1) / auto_steps
                progress_bar.progress(progress)
                
                # Display current state if not the last step
                if i < auto_steps - 1:
                    with st.spinner(f"Running step {i+1}/{auto_steps}..."):
                        import time
                        time.sleep(auto_delay)
            
            except Exception as e:
                st.sidebar.error(f"Error at step {i+1}: {str(e)}")
                break
        
        # Force refresh after all steps
        st.experimental_rerun()


def _show_simulation_results(simulation_id: str):
    """Show results for a simulation."""
    # Get simulation state and results
    state = _get_simulation_state(simulation_id)
    results = _get_simulation_results(simulation_id)
    
    if not state:
        st.error("Could not retrieve simulation data")
        return
    
    # Current year/quarter
    current_time = f"Year {state['year'] + 2023}, Quarter {state['quarter'] + 1}"
    st.header(f"Simulation Results - {current_time}")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "Economic Indicators", "Trade Relations", "Policies & Actions"
    ])
    
    with tab1:
        _show_overview_tab(state, results)
    
    with tab2:
        _show_economic_indicators_tab(state, results)
    
    with tab3:
        _show_trade_relations_tab(state, results)
    
    with tab4:
        _show_policies_tab(state, results)


def _get_simulation_state(simulation_id: str) -> Optional[Dict]:
    """Get current state of a simulation from the API."""
    try:
        response = requests.get(f"{API_URL}/api/simulation/{simulation_id}/state")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get simulation state: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error getting simulation state: {str(e)}")
        return None


def _get_simulation_results(simulation_id: str) -> Optional[Dict]:
    """Get full results of a simulation from the API."""
    try:
        response = requests.get(f"{API_URL}/api/results/{simulation_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get simulation results: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error getting simulation results: {str(e)}")
        return None


def _show_overview_tab(state: Dict, results: Optional[Dict]):
    """Show overview tab with key metrics and summary."""
    countries = state.get("countries", [])
    
    if not countries:
        st.warning("No country data available in the current state.")
        return

    # Display country cards with key metrics
    cols = st.columns(len(countries))
    for i, country in enumerate(countries):
        with cols[i]:
            st.subheader(country["name"])
            st.metric("GDP (trillion USD)", f"${country['gdp']:.2f}")
            st.metric("Inflation", f"{country['inflation_rate']:.1%}")
            st.metric("Unemployment", f"{country['unemployment_rate']:.1%}")
    
    # GDP comparison chart
    st.subheader("GDP Comparison")
    if results and "gdp_series" in results:
        gdp_fig = create_gdp_plot(results["gdp_series"])
        st.plotly_chart(gdp_fig, use_container_width=True)
    else:
        # Create simple bar chart from current state
        import plotly.express as px
        gdp_df = pd.DataFrame([
            {"Country": c["name"], "GDP": c["gdp"]} for c in countries
        ])
        gdp_fig = px.bar(
            gdp_df, x="Country", y="GDP", 
            title="Current GDP by Country",
            color="Country"
        )
        st.plotly_chart(gdp_fig, use_container_width=True)
    
    # Recent policies and actions
    st.subheader("Recent Trade Actions")
    if "recent_actions" in state and state["recent_actions"]:
        actions_df = pd.DataFrame(state["recent_actions"])
        st.dataframe(
            actions_df[["country", "action_type", "target_country", "magnitude", "justification"]],
            use_container_width=True
        )
    else:
        st.info("No recent trade actions to display")


def _show_economic_indicators_tab(state: Dict, results: Optional[Dict]):
    """Show economic indicators tab with detailed metrics over time."""
    # If we have time-series data, use it
    if results and all(k in results for k in ["gdp_series", "inflation_series", "unemployment_series"]):
        # Tabs for different indicators
        ind_tab1, ind_tab2, ind_tab3 = st.tabs(["GDP", "Inflation", "Unemployment"])
        
        with ind_tab1:
            gdp_fig = create_gdp_plot(results["gdp_series"])
            st.plotly_chart(gdp_fig, use_container_width=True)
        
        with ind_tab2:
            inflation_df = pd.DataFrame()
            for series in results["inflation_series"]:
                inflation_df[series["country"]] = series["values"]
            
            import plotly.express as px
            inflation_fig = px.line(
                inflation_df, 
                title="Inflation Rate Over Time",
                labels={"value": "Inflation Rate", "variable": "Country"}
            )
            st.plotly_chart(inflation_fig, use_container_width=True)
        
        with ind_tab3:
            unemployment_df = pd.DataFrame()
            for series in results["unemployment_series"]:
                unemployment_df[series["country"]] = series["values"]
            
            unemployment_fig = px.line(
                unemployment_df, 
                title="Unemployment Rate Over Time",
                labels={"value": "Unemployment Rate", "variable": "Country"}
            )
            st.plotly_chart(unemployment_fig, use_container_width=True)
    
    else:
        # Otherwise, show current state
        countries = state.get("countries", [])
        
        if not countries:
            st.warning("No country data available")
            return
        
        # Create comparison charts
        import plotly.express as px
        
        # GDP
        gdp_df = pd.DataFrame([
            {"Country": c["name"], "GDP": c["gdp"]} for c in countries
        ])
        gdp_fig = px.bar(
            gdp_df, x="Country", y="GDP", 
            title="Current GDP by Country"
        )
        st.plotly_chart(gdp_fig, use_container_width=True)
        
        # Inflation
        inflation_df = pd.DataFrame([
            {"Country": c["name"], "Inflation": c["inflation_rate"]} for c in countries
        ])
        inflation_fig = px.bar(
            inflation_df, x="Country", y="Inflation", 
            title="Current Inflation Rate by Country"
        )
        st.plotly_chart(inflation_fig, use_container_width=True)
        
        # Unemployment
        unemployment_df = pd.DataFrame([
            {"Country": c["name"], "Unemployment": c["unemployment_rate"]} for c in countries
        ])
        unemployment_fig = px.bar(
            unemployment_df, x="Country", y="Unemployment", 
            title="Current Unemployment Rate by Country"
        )
        st.plotly_chart(unemployment_fig, use_container_width=True)


def _show_trade_relations_tab(state: Dict, results: Optional[Dict]):
    """Show trade relations tab with trade balances and flows."""
    # Trade flows
    if "trade_flows" in state and state["trade_flows"]:
        st.subheader("Trade Flows")
        trade_network = create_trade_network_graph(state["trade_flows"])
        st.plotly_chart(trade_network, use_container_width=True)
        
        # Trade balances
        st.subheader("Trade Balances")
        if results and "trade_balances" in results:
            trade_balance_fig = create_trade_balance_plot(results["trade_balances"])
            st.plotly_chart(trade_balance_fig, use_container_width=True)
        else:
            st.info("Insufficient data to show trade balance trends")
    else:
        st.info("No trade flow data available yet")


def _show_policies_tab(state: Dict, results: Optional[Dict]):
    """Show policies tab with current and historical policies."""
    # Display active tariff policies
    st.subheader("Active Tariff Policies")
    
    if "active_tariff_policies" in state and state["active_tariff_policies"]:
        tariff_policies = state["active_tariff_policies"]
        
        # Create tariff heatmap
        st.plotly_chart(
            create_tariff_heatmap(tariff_policies),
            use_container_width=True
        )
        
        # Show detailed policy table
        policy_data = []
        for policy in tariff_policies:
            # Calculate average tariff rate
            avg_rate = sum(policy["sector_rates"].values()) / len(policy["sector_rates"])
            
            policy_data.append({
                "Source": policy["source_country"],
                "Target": policy["target_country"],
                "Average Rate": f"{avg_rate:.1%}",
                "Duration": f"{policy['duration_quarters']} quarters",
                "Sectors": ", ".join(policy["sector_rates"].keys())
            })
        
        policy_df = pd.DataFrame(policy_data)
        st.dataframe(policy_df, use_container_width=True)
    else:
        st.info("No active tariff policies")
    
    # Display all actions history
    st.subheader("Policy Action History")
    
    if "all_actions" in state and state["all_actions"]:
        actions = state["all_actions"]
        
        action_data = []
        for action in actions:
            action_data.append({
                "Year": f"{action['year'] + 2023}",
                "Quarter": action["quarter"] + 1,
                "Country": action["country"],
                "Action": action["action_type"],
                "Target": action.get("target_country", "None"),
                "Magnitude": f"{action['magnitude']:.1%}",
                "Justification": action["justification"]
            })
        
        action_df = pd.DataFrame(action_data)
        st.dataframe(action_df, use_container_width=True)
    else:
        st.info("No action history available")


if __name__ == "__main__":
    main()
