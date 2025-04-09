#!/usr/bin/env python3
"""Post-simulation analysis and report generation."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Add parent directory to Python path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tradewar.config import config
from tradewar.simulation.stability import StabilityAnalyzer

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tradewar-reports")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate reports from simulation results")
    
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Path to simulation results CSV file"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Directory for generated reports"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["pdf", "html", "md", "all"],
        default="all",
        help="Output report format"
    )
    
    parser.add_argument(
        "--title",
        type=str,
        default="Trade War Simulation Analysis",
        help="Report title"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def load_simulation_data(input_file: str) -> pd.DataFrame:
    """
    Load simulation results from CSV file.
    
    Args:
        input_file: Path to CSV file
        
    Returns:
        DataFrame with simulation data
    """
    try:
        df = pd.read_csv(input_file)
        logger.info(f"Loaded data from {input_file}: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error loading simulation data: {str(e)}")
        sys.exit(1)


def create_overview_charts(df: pd.DataFrame, output_dir: str) -> Dict[str, str]:
    """
    Create overview charts for the simulation results.
    
    Args:
        df: DataFrame with simulation data
        output_dir: Directory to save charts
        
    Returns:
        Dictionary mapping chart types to file paths
    """
    chart_files = {}
    
    # Ensure output directory exists
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    try:
        # 1. GDP over time for each country
        plt.figure(figsize=(12, 6))
        
        # Get list of countries from column names
        gdp_cols = [col for col in df.columns if col.endswith("_gdp")]
        countries = [col.split("_")[0] for col in gdp_cols]
        
        for country, col in zip(countries, gdp_cols):
            plt.plot(df.index, df[col], label=f"{country} GDP", linewidth=2)
        
        plt.title("GDP Over Time")
        plt.xlabel("Time Step")
        plt.ylabel("GDP (trillion USD)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the chart
        gdp_chart_path = os.path.join(charts_dir, "gdp_over_time.png")
        plt.savefig(gdp_chart_path, dpi=150, bbox_inches="tight")
        plt.close()
        
        chart_files["gdp"] = gdp_chart_path
        
        # 2. Inflation rates over time
        plt.figure(figsize=(12, 6))
        
        inflation_cols = [col for col in df.columns if col.endswith("_inflation")]
        
        for country, col in zip(countries, inflation_cols):
            plt.plot(df.index, df[col] * 100, label=f"{country} Inflation", linewidth=2)
        
        plt.title("Inflation Rates Over Time")
        plt.xlabel("Time Step")
        plt.ylabel("Inflation Rate (%)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the chart
        inflation_chart_path = os.path.join(charts_dir, "inflation_over_time.png")
        plt.savefig(inflation_chart_path, dpi=150, bbox_inches="tight")
        plt.close()
        
        chart_files["inflation"] = inflation_chart_path
        
        # 3. Trade balances heatmap for the final time step
        plt.figure(figsize=(10, 8))
        
        # Get all trade balance columns
        balance_cols = [col for col in df.columns if col.startswith("trade_balance_")]
        
        # Create a matrix of final trade balances
        balance_matrix = []
        row_labels = []
        col_labels = []
        
        for country1 in countries:
            row = []
            for country2 in countries:
                if country1 != country2:
                    col_name = f"trade_balance_{country1}_{country2}"
                    if col_name in balance_cols:
                        balance = df[col_name].iloc[-1]
                    else:
                        balance = 0
                    row.append(balance)
                else:
                    row.append(0)  # No trade with self
            
            balance_matrix.append(row)
            row_labels.append(country1)
            col_labels = countries.copy()  # Same labels for columns
        
        # Create heatmap
        sns.heatmap(
            balance_matrix,
            annot=True,
            fmt=".1f",
            cmap="RdBu",
            center=0,
            xticklabels=col_labels,
            yticklabels=row_labels
        )
        
        plt.title("Final Trade Balances (billion USD)")
        plt.tight_layout()
        
        # Save the chart
        balance_chart_path = os.path.join(charts_dir, "trade_balances.png")
        plt.savefig(balance_chart_path, dpi=150, bbox_inches="tight")
        plt.close()
        
        chart_files["trade_balance"] = balance_chart_path
        
        logger.info(f"Created {len(chart_files)} overview charts")
        return chart_files
    
    except Exception as e:
        logger.error(f"Error creating overview charts: {str(e)}")
        return chart_files


def analyze_policy_impacts(df: pd.DataFrame) -> Dict:
    """
    Analyze the impacts of different policy actions.
    
    Args:
        df: DataFrame with simulation data
        
    Returns:
        Dictionary with policy impact analysis
    """
    # This would be a more sophisticated analysis in a real implementation
    # For now, we'll create a simple placeholder analysis
    
    # Get list of countries from column names
    gdp_cols = [col for col in df.columns if col.endswith("_gdp")]
    countries = [col.split("_")[0] for col in gdp_cols]
    
    # Calculate GDP growth rates
    gdp_growth = {}
    for country, col in zip(countries, gdp_cols):
        initial_gdp = df[col].iloc[0]
        final_gdp = df[col].iloc[-1]
        total_growth = (final_gdp / initial_gdp) - 1
        gdp_growth[country] = total_growth
    
    # Calculate average inflation
    avg_inflation = {}
    inflation_cols = [col for col in df.columns if col.endswith("_inflation")]
    for country, col in zip(countries, inflation_cols):
        avg_inflation[country] = df[col].mean()
    
    # Calculate trade balance trends
    trade_balance_trends = {}
    for country1 in countries:
        total_initial_balance = 0
        total_final_balance = 0
        
        for country2 in countries:
            if country1 != country2:
                col_name = f"trade_balance_{country1}_{country2}"
                if col_name in df.columns:
                    total_initial_balance += df[col_name].iloc[0]
                    total_final_balance += df[col_name].iloc[-1]
        
        # Calculate if balance improved or worsened
        if total_initial_balance < 0:
            # Started with deficit
            trend = "improved" if total_final_balance > total_initial_balance else "worsened"
        else:
            # Started with surplus
            trend = "improved" if total_final_balance > total_initial_balance else "worsened"
        
        trade_balance_trends[country1] = {
            "initial": total_initial_balance,
            "final": total_final_balance,
            "trend": trend
        }
    
    return {
        "gdp_growth": gdp_growth,
        "avg_inflation": avg_inflation,
        "trade_balance_trends": trade_balance_trends,
    }


def calculate_stability_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculate economic stability metrics for the simulation.
    
    Args:
        df: DataFrame with simulation data
        
    Returns:
        Dictionary with stability metrics
    """
    # Initialize a StabilityAnalyzer
    analyzer = StabilityAnalyzer()
    
    # Get list of countries
    gdp_cols = [col for col in df.columns if col.endswith("_gdp")]
    countries = [col.split("_")[0] for col in gdp_cols]
    
    # Calculate GDP volatility
    gdp_volatility = {}
    for country, col in zip(countries, gdp_cols):
        # Calculate normalized quarter-to-quarter changes
        gdp_series = df[col].values
        if len(gdp_series) > 1:
            changes = np.diff(gdp_series) / gdp_series[:-1]
            volatility = np.std(changes)
            gdp_volatility[country] = volatility
    
    # Calculate inflation volatility
    inflation_volatility = {}
    inflation_cols = [col for col in df.columns if col.endswith("_inflation")]
    for country, col in zip(countries, inflation_cols):
        inflation_volatility[country] = df[col].std()
    
    # Calculate average trade balance volatility
    trade_volatility = {}
    for country in countries:
        volatilities = []
        for partner in countries:
            if country != partner:
                col_name = f"trade_balance_{country}_{partner}"
                if col_name in df.columns:
                    volatilities.append(df[col_name].std())
        
        if volatilities:
            trade_volatility[country] = sum(volatilities) / len(volatilities)
    
    # Overall stability ratings
    stability_ratings = {}
    for country in countries:
        # Combine factors with weights
        gdp_factor = 1.0 - min(1.0, gdp_volatility.get(country, 0) * 10)
        inflation_factor = 1.0 - min(1.0, inflation_volatility.get(country, 0) * 20)
        trade_factor = 1.0 - min(1.0, trade_volatility.get(country, 0) * 0.02)
        
        # Calculate weighted score
        score = 0.5 * gdp_factor + 0.3 * inflation_factor + 0.2 * trade_factor
        
        stability_ratings[country] = {
            "score": score,
            "rating": _get_stability_rating(score),
            "factors": {
                "gdp_volatility": gdp_volatility.get(country, 0),
                "inflation_volatility": inflation_volatility.get(country, 0),
                "trade_volatility": trade_volatility.get(country, 0)
            }
        }
    
    return {
        "country_stability": stability_ratings,
        "global_stability": _calculate_global_stability(stability_ratings)
    }


def _get_stability_rating(score: float) -> str:
    """Convert a stability score to a descriptive rating."""
    if score >= 0.8:
        return "Very Stable"
    elif score >= 0.6:
        return "Stable"
    elif score >= 0.4:
        return "Moderately Stable"
    elif score >= 0.2:
        return "Unstable"
    else:
        return "Very Unstable"


def _calculate_global_stability(country_ratings: Dict) -> Dict:
    """Calculate global economic stability from country ratings."""
    scores = [data["score"] for data in country_ratings.values()]
    if not scores:
        return {"score": 0.5, "rating": "Unknown"}
    
    avg_score = sum(scores) / len(scores)
    
    return {
        "score": avg_score,
        "rating": _get_stability_rating(avg_score),
        "min_country": min(country_ratings.items(), key=lambda x: x[1]["score"])[0],
        "max_country": max(country_ratings.items(), key=lambda x: x[1]["score"])[0],
    }


def generate_markdown_report(
    df: pd.DataFrame,
    overview_charts: Dict[str, str],
    policy_analysis: Dict,
    stability_metrics: Dict,
    output_dir: str,
    title: str
) -> str:
    """
    Generate a Markdown report from the simulation analysis.
    
    Args:
        df: DataFrame with simulation data
        overview_charts: Dictionary of chart file paths
        policy_analysis: Policy impact analysis
        stability_metrics: Economic stability metrics
        output_dir: Directory to save report
        title: Report title
        
    Returns:
        Path to the generated report
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, "simulation_report.md")
    
    try:
        with open(report_path, 'w') as f:
            # Title and introduction
            f.write(f"# {title}\n\n")
            f.write(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("## Overview\n\n")
            
            # Count countries using GDP columns to ensure accuracy
            gdp_cols = [col for col in df.columns if col.endswith("_gdp")]
            num_countries = len(gdp_cols)
            
            # Use 'year' column if present, otherwise estimate
            if 'year' in df.columns:
                num_years = df['year'].max() + 1  # Years are 0-indexed
            else:
                num_quarters = len(df)
                num_years = num_quarters / 4  # Assuming 4 quarters per year
                
            f.write(f"This report analyzes the results of a trade war simulation with "
                   f"{num_countries} countries over "
                   f"{num_years:.1f} years.\n\n")
            
            # Embed charts
            f.write("## Economic Indicators\n\n")
            
            for chart_type, file_path in overview_charts.items():
                if chart_type == "gdp":
                    f.write("### GDP Trends\n\n")
                    # Use relative path for the image
                    rel_path = os.path.relpath(file_path, output_dir)
                    f.write(f"![GDP Over Time]({rel_path})\n\n")
                elif chart_type == "inflation":
                    f.write("### Inflation Trends\n\n")
                    rel_path = os.path.relpath(file_path, output_dir)
                    f.write(f"![Inflation Rates]({rel_path})\n\n")
                elif chart_type == "trade_balance":
                    f.write("### Final Trade Balances\n\n")
                    rel_path = os.path.relpath(file_path, output_dir)
                    f.write(f"![Trade Balances]({rel_path})\n\n")
            
            # Policy impact analysis
            f.write("## Policy Impact Analysis\n\n")
            
            # GDP Growth
            f.write("### GDP Growth\n\n")
            f.write("| Country | Total Growth | Annualized |\n")
            f.write("|---------|--------------|------------|\n")
            
            for country, growth in policy_analysis["gdp_growth"].items():
                years = num_years
                annualized = (1 + growth) ** (1 / years) - 1
                f.write(f"| {country} | {growth:.2%} | {annualized:.2%} |\n")
            
            f.write("\n")
            
            # Trade Balance Trends
            f.write("### Trade Balance Trends\n\n")
            f.write("| Country | Initial Balance | Final Balance | Trend |\n")
            f.write("|---------|-----------------|--------------|-------|\n")
            
            for country, data in policy_analysis["trade_balance_trends"].items():
                f.write(f"| {country} | ${data['initial']:.1f}B | ${data['final']:.1f}B | {data['trend']} |\n")
            
            f.write("\n")
            
            # Stability Metrics
            f.write("## Economic Stability Analysis\n\n")
            
            # Global Stability
            global_stability = stability_metrics["global_stability"]
            f.write("### Global Economic Stability\n\n")
            f.write(f"**Overall Stability Rating:** {global_stability['rating']} ")
            f.write(f"({global_stability['score']:.2f}/1.0)\n\n")
            f.write(f"Most stable economy: **{global_stability['max_country']}**\n\n")
            f.write(f"Least stable economy: **{global_stability['min_country']}**\n\n")
            
            # Country Stability
            f.write("### Country Stability Ratings\n\n")
            f.write("| Country | Stability Score | Rating | GDP Volatility | Inflation Volatility |\n")
            f.write("|---------|----------------|--------|----------------|----------------------|\n")
            
            for country, data in stability_metrics["country_stability"].items():
                factors = data["factors"]
                f.write(f"| {country} | {data['score']:.2f} | {data['rating']} | ")
                f.write(f"{factors['gdp_volatility']:.4f} | {factors['inflation_volatility']:.4f} |\n")
            
            f.write("\n")
            
            # Conclusion
            f.write("## Conclusion\n\n")
            
            # Simple conclusion based on stability
            if global_stability['score'] >= 0.7:
                f.write("The simulation resulted in a generally stable economic environment despite trade tensions. ")
                f.write("Policy decisions effectively managed potential economic disruptions.")
            elif global_stability['score'] >= 0.4:
                f.write("The simulation showed moderate economic stability with some volatility. ")
                f.write("Trade tensions had notable but not severe economic impacts.")
            else:
                f.write("The simulation resulted in significant economic instability. ")
                f.write("Trade war policies created substantial economic disruption and volatility.")
                
            # Policy recommendations
            f.write("\n\n### Policy Recommendations\n\n")
            
            # Create recommendations based on the analysis
            most_stable = global_stability['max_country']
            least_stable = global_stability['min_country']
            
            f.write(f"1. **For {least_stable}**: Consider reducing trade barriers and seeking ")
            f.write("bilateral negotiations to stabilize economic indicators.\n\n")
            
            f.write(f"2. **For {most_stable}**: The current policy approach appears effective. ")
            f.write("Continue the balanced approach to trade policy.\n\n")
            
            # General recommendations
            f.write("3. **For all countries**: Gradual tariff adjustments are preferable to ")
            f.write("sudden large increases, which tend to create more volatility.\n\n")
            
            f.write("4. **Trade diversification**: Countries should diversify trading partners ")
            f.write("to reduce dependency on specific bilateral relationships.\n\n")
            
            # Simulation metadata
            f.write("\n---\n\n")
            f.write("*Report generated using Trade War Simulation v0.1.0*\n")
            
        logger.info(f"Markdown report generated at {report_path}")
        return report_path
    
    except Exception as e:
        logger.error(f"Error generating markdown report: {str(e)}")
        return ""


def generate_html_report(
    markdown_path: str,
    output_dir: str,
    title: str
) -> str:
    """
    Generate an HTML report from the Markdown report.
    
    Args:
        markdown_path: Path to markdown report
        output_dir: Directory to save report
        title: Report title
        
    Returns:
        Path to the generated HTML report
    """
    try:
        import markdown
        from markdown.extensions.tables import TableExtension
        
        html_path = os.path.join(output_dir, "simulation_report.html")
        
        # Read markdown content
        with open(markdown_path, 'r') as f:
            md_content = f.read()
        
        # Convert to HTML
        html = markdown.markdown(
            md_content,
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.toc',
                TableExtension(),
                'markdown.extensions.fenced_code',
                'markdown.extensions.nl2br'
            ]
        )
        
        # Create full HTML document
        html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #1a5276;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 8px;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border: 1px solid #ddd;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 0.8em;
            color: #666;
        }}
    </style>
</head>
<body>
    {html}
    <div class="footer">
        <p>Generated using Trade War Simulation Tool on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>"""
        
        # Write HTML file
        with open(html_path, 'w') as f:
            f.write(html_doc)
        
        logger.info(f"HTML report generated at {html_path}")
        return html_path
    
    except ImportError:
        logger.warning("Python-markdown package not available. Cannot generate HTML report.")
        return ""
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return ""


def generate_pdf_report(
    html_path: str,
    output_dir: str
) -> str:
    """
    Generate a PDF report from the HTML report.
    
    Args:
        html_path: Path to HTML report
        output_dir: Directory to save report
        
    Returns:
        Path to the generated PDF report
    """
    pdf_path = os.path.join(output_dir, "simulation_report.pdf")
    
    try:
        import weasyprint
        
        # Convert HTML to PDF
        weasyprint.HTML(filename=html_path).write_pdf(pdf_path)
        
        logger.info(f"PDF report generated at {pdf_path}")
        return pdf_path
    
    except ImportError:
        logger.warning("WeasyPrint package not available. Cannot generate PDF report.")
        return ""
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return ""


def main():
    """Main entry point for the report generation script."""
    args = parse_args()
    
    if args.verbose:
        logging.getLogger("tradewar-reports").setLevel(logging.DEBUG)
    
    logger.info("Starting report generation")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load simulation data
    df = load_simulation_data(args.input_file)
    
    # Generate charts
    logger.info("Creating overview charts")
    chart_files = create_overview_charts(df, args.output_dir)
    
    # Perform analyses
    logger.info("Analyzing policy impacts")
    policy_analysis = analyze_policy_impacts(df)
    
    logger.info("Calculating stability metrics")
    stability_metrics = calculate_stability_metrics(df)
    
    # Generate reports in requested formats
    md_path = ""
    html_path = ""
    pdf_path = ""
    
    if args.format in ["md", "all"]:
        logger.info("Generating Markdown report")
        md_path = generate_markdown_report(
            df, chart_files, policy_analysis, stability_metrics, 
            args.output_dir, args.title
        )
    
    if args.format in ["html", "all"] and md_path:
        logger.info("Generating HTML report")
        html_path = generate_html_report(
            md_path, args.output_dir, args.title
        )
    
    if args.format in ["pdf", "all"] and html_path:
        logger.info("Generating PDF report")
        pdf_path = generate_pdf_report(
            html_path, args.output_dir
        )
    
    # Final output summary
    available_formats = []
    if md_path:
        available_formats.append("Markdown")
    if html_path:
        available_formats.append("HTML")
    if pdf_path:
        available_formats.append("PDF")
    
    if available_formats:
        logger.info(f"Report generation completed. Available formats: {', '.join(available_formats)}")
        print(f"\nReport generation completed. Reports saved in {args.output_dir}")
        print(f"Available formats: {', '.join(available_formats)}")
    else:
        logger.error("No reports were generated")
        print("\nError: No reports were generated")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
