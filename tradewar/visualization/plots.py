"""Plotly visualization helpers for the trade war simulation dashboard."""

from typing import Dict, List

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_gdp_plot(gdp_series: List[Dict]) -> go.Figure:
    """
    Create a GDP time series plot for multiple countries.
    
    Args:
        gdp_series: List of time series data for each country's GDP
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    for series in gdp_series:
        country = series["country"]
        times = series["times"]
        values = series["values"]
        
        fig.add_trace(
            go.Scatter(
                x=times,
                y=values,
                mode="lines+markers",
                name=f"{country} GDP",
                hovertemplate="GDP: $%{y:.2f} trillion<br>%{x}",
            )
        )
    
    fig.update_layout(
        title="GDP Over Time",
        xaxis_title="Time Period",
        yaxis_title="GDP (trillion USD)",
        legend_title="Countries",
        hovermode="x unified",
    )
    
    return fig


def create_trade_balance_plot(trade_balances: Dict[str, Dict[str, float]]) -> go.Figure:
    """
    Create a trade balance heatmap between countries.
    
    Args:
        trade_balances: Dictionary of trade balances by country pair
        
    Returns:
        Plotly figure object
    """
    countries = list(trade_balances.keys())
    
    # Create matrix of trade balances
    balance_matrix = []
    for country1 in countries:
        row = []
        for country2 in countries:
            if country1 == country2:
                row.append(0)  # No trade with self
            else:
                row.append(trade_balances[country1].get(country2, 0))
        balance_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=balance_matrix,
        x=countries,
        y=countries,
        colorscale="RdBu",
        zmid=0,  # Center colorscale at 0
        text=[[f"${val:.1f}B" for val in row] for row in balance_matrix],
        hovertemplate="From %{y} to %{x}<br>Balance: %{text}<extra></extra>",
    ))
    
    fig.update_layout(
        title="Bilateral Trade Balances (Billion USD)",
        xaxis_title="Country",
        yaxis_title="Country",
    )
    
    return fig


def create_tariff_heatmap(tariff_policies: List[Dict]) -> go.Figure:
    """
    Create a heatmap of tariff rates between countries.
    
    Args:
        tariff_policies: List of tariff policies
        
    Returns:
        Plotly figure object
    """
    # Extract all countries
    source_countries = set()
    target_countries = set()
    for policy in tariff_policies:
        source_countries.add(policy["source_country"])
        target_countries.add(policy["target_country"])
    
    source_countries = sorted(list(source_countries))
    target_countries = sorted(list(target_countries))
    
    # Create matrix of average tariff rates
    tariff_matrix = np.zeros((len(source_countries), len(target_countries)))
    
    for policy in tariff_policies:
        source_idx = source_countries.index(policy["source_country"])
        target_idx = target_countries.index(policy["target_country"])
        
        # Calculate average tariff rate
        rates = policy["sector_rates"].values()
        avg_rate = sum(rates) / len(rates) if rates else 0
        
        tariff_matrix[source_idx, target_idx] = avg_rate
    
    # Format for display
    text_matrix = [[f"{val:.1%}" for val in row] for row in tariff_matrix]
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=tariff_matrix,
        x=target_countries,
        y=source_countries,
        colorscale="Reds",
        text=text_matrix,
        hovertemplate="%{y} tariffs on %{x}: %{text}<extra></extra>",
    ))
    
    fig.update_layout(
        title="Average Tariff Rates",
        xaxis_title="Target Country",
        yaxis_title="Source Country",
    )
    
    return fig


def create_trade_network_graph(trade_flows: List[Dict]) -> go.Figure:
    """
    Create a network graph of trade flows between countries.
    
    Args:
        trade_flows: List of trade flow data
        
    Returns:
        Plotly figure object
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Collect nodes (countries)
    countries = set()
    for flow in trade_flows:
        countries.add(flow["exporter"])
        countries.add(flow["importer"])
    
    # Add nodes
    for country in countries:
        G.add_node(country)
    
    # Add edges with weights
    for flow in trade_flows:
        exporter = flow["exporter"]
        importer = flow["importer"]
        value = flow["total_value"]
        
        # Skip very small values to avoid clutter
        if value < 0.1:
            continue
        
        G.add_edge(exporter, importer, weight=value)
    
    # Set up positions using a spring layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Create edges
    edge_x = []
    edge_y = []
    edge_width = []
    edge_text = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Draw curved edges
        curve_factor = 0.1
        cx = (x0 + x1) / 2 + curve_factor * (y1 - y0)
        cy = (y0 + y1) / 2 + curve_factor * (x0 - x1)
        
        # Add to path
        edge_x.extend([x0, cx, x1, None])
        edge_y.extend([y0, cy, y1, None])
        
        # Width based on trade value (normalized)
        width = 1 + 9 * (edge[2]["weight"] / max(1, max(e[2]["weight"] for e in G.edges(data=True))))
        edge_width.append(width)
        
        edge_text.append(f"From: {edge[0]}<br>To: {edge[1]}<br>Value: ${edge[2]['weight']:.2f}B")
    
    # Create edge traces
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=edge_width, color="#888"),
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    )
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            color="#39A2DB",
            size=15,
            line=dict(width=2, color="#333")
        ),
        hoverinfo='text'
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title="Trade Flow Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
             ))
    
    return fig


def create_policy_timeline(actions: List[Dict]) -> go.Figure:
    """
    Create a timeline of policy actions.
    
    Args:
        actions: List of economic actions
        
    Returns:
        Plotly figure object
    """
    if not actions:
        # Empty chart if no actions
        fig = go.Figure()
        fig.update_layout(
            title="Policy Action Timeline",
            xaxis_title="Time",
            yaxis_title="Country",
        )
        return fig
    
    # Prepare data
    data = []
    for action in actions:
        data.append({
            "Country": action["country"],
            "Action": action["action_type"],
            "Target": action.get("target_country", "None"),
            "Time": f"Y{action['year']+1}Q{action['quarter']+1}",
            "Magnitude": action["magnitude"],
            "Description": (
                f"{action['country']} {action['action_type']} "
                f"({action['magnitude']:.1%}) against {action.get('target_country', 'None')}"
            )
        })
    
    df = pd.DataFrame(data)
    
    # Create grouped timeline
    fig = px.timeline(
        df, 
        x_start="Time", 
        y="Country",
        color="Action",
        hover_name="Description",
        hover_data=["Target", "Magnitude"]
    )
    
    fig.update_layout(
        title="Policy Action Timeline",
        xaxis_title="Simulation Time",
        yaxis_title="Country",
    )
    
    return fig
