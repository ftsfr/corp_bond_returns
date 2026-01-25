"""Generate interactive HTML chart for Corporate Bond Returns."""

import pandas as pd
import plotly.express as px
import os
from pathlib import Path

# Get the project root (one level up from src/)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "_data"
OUTPUT_DIR = PROJECT_ROOT / "_output"


def generate_corp_bond_returns_chart():
    """Generate corporate bond portfolio returns time series chart."""
    # Load corporate bond portfolio returns data
    df = pd.read_parquet(DATA_DIR / "ftsfr_corp_bond_portfolio_returns.parquet")

    # Create line chart
    fig = px.line(
        df.sort_values("ds"),
        x="ds",
        y="y",
        color="unique_id",
        title="Corporate Bond Portfolio Returns",
        labels={
            "ds": "Date",
            "y": "Return",
            "unique_id": "Portfolio"
        }
    )

    # Update layout
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save chart
    output_path = OUTPUT_DIR / "corp_bond_returns_replication.html"
    fig.write_html(str(output_path))
    print(f"Chart saved to {output_path}")

    return fig


def generate_corp_bond_cumulative_returns_chart():
    """Generate corporate bond portfolio cumulative returns time series chart."""
    # Load corporate bond portfolio returns data
    df = pd.read_parquet(DATA_DIR / "ftsfr_corp_bond_portfolio_returns.parquet")

    # Calculate cumulative returns
    df = df.sort_values(['unique_id', 'ds'])
    df['cumulative'] = df.groupby('unique_id')['y'].transform(
        lambda x: (1 + x).cumprod()
    )

    # Create line chart
    fig = px.line(
        df,
        x="ds",
        y="cumulative",
        color="unique_id",
        title="Corporate Bond Portfolio Cumulative Returns",
        labels={
            "ds": "Date",
            "cumulative": "Cumulative Return (Growth of $1)",
            "unique_id": "Portfolio"
        }
    )

    # Update layout
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        yaxis_type="log"
    )

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save chart
    output_path = OUTPUT_DIR / "corp_bond_cumulative_returns.html"
    fig.write_html(str(output_path))
    print(f"Chart saved to {output_path}")

    return fig


if __name__ == "__main__":
    generate_corp_bond_returns_chart()
    generate_corp_bond_cumulative_returns_chart()
