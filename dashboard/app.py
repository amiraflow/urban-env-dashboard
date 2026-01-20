"""
Urban Environmental Quality Dashboard
=====================================

Main Dash application entry point.

This dashboard analyzes air quality and livability across world cities with
a focus on Vienna. It includes 7 interactive visualizations with full
brushing & linking support.

Features:
- Geographic map with PM2.5 color encoding
- Time series trends (2020-2023)
- Cluster-based analysis (K-means with 4 clusters)
- Scatter plots, correlation heatmap, city comparisons
- Parallel coordinates for multi-dimensional analysis
- Full brushing & linking: click anywhere → highlights everywhere

Run locally:
    python dashboard/app.py

Deploy:
    See README.md for deployment instructions
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import Dash
import dash_bootstrap_components as dbc

from dashboard.layouts import create_main_layout
from dashboard.callbacks import register_callbacks, load_data


def create_app():
    """
    Create and configure the Dash application.

    Returns:
        Dash: Configured application instance
    """
    # Initialize Dash app with Bootstrap theme for professional styling
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,  # Clean, professional styling
        ],
        title="Urban Environmental Quality Dashboard",
        update_title="Loading...",
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"name": "description", "content": "Interactive dashboard analyzing urban air quality across world cities"},
        ],
    )

    # Set assets folder for custom CSS
    app._favicon = None  # Disable default favicon

    # Load data
    print("Loading data...")
    df_summary, df_timeseries = load_data()
    print(f"Loaded {len(df_summary)} cities with {len(df_timeseries)} time series records")

    # Create layout
    app.layout = create_main_layout()

    # Register callbacks (passes data to callback functions)
    register_callbacks(app, df_summary, df_timeseries)

    return app


# Create the app instance
app = create_app()

# Expose the server for deployment (gunicorn looks for this)
server = app.server


if __name__ == '__main__':
    # Run in development mode
    print("\n" + "=" * 60)
    print("Urban Environmental Quality Dashboard")
    print("=" * 60)
    print("\nStarting development server...")
    print("Open http://127.0.0.1:8050 in your browser")
    print("Press Ctrl+C to stop\n")

    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050,
    )
