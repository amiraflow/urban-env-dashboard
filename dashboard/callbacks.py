"""
Callbacks for Urban Environmental Quality Dashboard

This module implements all interactive callbacks including:
- Brushing & Linking: Selections in one view affect ALL other views
- Global Filters: Region, Year, Cluster filters
- Quick Filters: Vienna's cluster, top cleanest, reset

CRITICAL: Brushing & Linking Implementation
============================================
The brushing & linking pattern works through:
1. dcc.Store components to maintain shared state (selected-cities-store, selected-cluster-store)
2. Each chart can UPDATE the store when clicked/selected
3. Each chart READS from the store and updates its visualization accordingly
4. All charts re-render when the store changes, highlighting selected items

Flow:
User clicks city on map → Store updates → All charts re-render with that city highlighted
User lasso selects in scatter → Store updates → All charts highlight those cities
User clicks cluster box → Store updates → All charts filter to that cluster
"""

from dash import callback, Output, Input, State, ctx, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
import json

from dashboard.visualizations import (
    create_map,
    create_time_series,
    create_cluster_boxplot,
    create_scatter_plot,
    create_correlation_heatmap,
    create_city_comparison,
    create_parallel_coordinates,
)
from dashboard.styles import CLUSTER_NAMES


def register_callbacks(app, df_summary, df_timeseries):
    """
    Register all dashboard callbacks.

    Args:
        app: Dash application instance
        df_summary: DataFrame with city summary data
        df_timeseries: DataFrame with time series data
    """

    # =========================================================================
    # MASTER CALLBACK: Update all charts based on filters and selections
    # =========================================================================
    # This callback handles the core brushing & linking functionality.
    # It takes inputs from:
    # - Global filters (region, year, cluster)
    # - Selected cities store (from clicking/selecting on charts)
    # - Individual chart controls (indicator dropdowns)
    #
    # It outputs to all 7 charts plus the metric cards.

    @app.callback(
        # Chart outputs
        Output('map-chart', 'figure'),
        Output('timeseries-chart', 'figure'),
        Output('boxplot-chart', 'figure'),
        Output('scatter-chart', 'figure'),
        Output('correlation-chart', 'figure'),
        Output('comparison-chart', 'figure'),
        Output('parallel-chart', 'figure'),
        # Metric card outputs
        Output('cities-value', 'children'),
        Output('avg-pm25-value', 'children'),
        Output('vienna-pm25-value', 'children'),
        Output('selected-value', 'children'),
        # Filter inputs
        Input('region-filter', 'value'),
        Input('year-slider', 'value'),
        Input('cluster-filter', 'value'),
        # Selection store input (for brushing & linking)
        Input('selected-cities-store', 'data'),
        # Chart control inputs
        Input('boxplot-indicator', 'value'),
        Input('scatter-x-var', 'value'),
        Input('comparison-indicator', 'value'),
    )
    def update_all_charts(region, year_range, clusters, selected_cities,
                          boxplot_indicator, scatter_x_var, comparison_indicator):
        """
        Master callback that updates all charts based on current filters and selections.

        This is the heart of the brushing & linking implementation:
        - Filters data based on region, year range, and cluster selections
        - Passes selected_cities to each visualization for highlighting
        - Each chart dims unselected items and highlights selected ones
        """
        # Apply filters to data
        df_filtered = df_summary.copy()
        df_ts_filtered = df_timeseries.copy()

        # Region filter
        if region and region != 'all':
            df_filtered = df_filtered[df_filtered['region'] == region]
            df_ts_filtered = df_ts_filtered[df_ts_filtered['region'] == region]

        # Cluster filter
        if clusters and len(clusters) > 0:
            df_filtered = df_filtered[df_filtered['cluster'].isin(clusters)]
            df_ts_filtered = df_ts_filtered[
                df_ts_filtered['city'].isin(df_filtered['city'])
            ]

        # Year filter (for time series)
        if year_range:
            df_ts_filtered = df_ts_filtered[
                (df_ts_filtered['year'] >= year_range[0]) &
                (df_ts_filtered['year'] <= year_range[1])
            ]

        # Ensure Vienna is always included for reference
        vienna_data = df_summary[df_summary['city'] == 'Vienna']
        if len(df_filtered[df_filtered['city'] == 'Vienna']) == 0:
            df_filtered = pd.concat([df_filtered, vienna_data], ignore_index=True)

        # Prepare selected cities list for brushing
        selected = selected_cities if selected_cities else []

        # Generate all charts with current data and selection state
        # Each chart receives selected_cities and highlights those items

        # 1. Map
        map_fig = create_map(df_filtered, selected_cities=selected)

        # 2. Time Series
        timeseries_fig = create_time_series(
            df_ts_filtered, df_filtered, selected_cities=selected
        )

        # 3. Box Plot
        boxplot_fig = create_cluster_boxplot(
            df_filtered, indicator=boxplot_indicator
        )

        # 4. Scatter Plot
        scatter_fig = create_scatter_plot(
            df_filtered, selected_cities=selected,
            x_var=scatter_x_var, y_var='pm25'
        )

        # 5. Correlation Heatmap
        correlation_fig = create_correlation_heatmap(df_filtered)

        # 6. City Comparison
        # If cities are selected, compare those; otherwise compare Vienna's cluster
        comparison_cities = selected if selected else None
        comparison_fig = create_city_comparison(
            df_filtered,
            comparison_cities=comparison_cities,
            indicator=comparison_indicator
        )

        # 7. Parallel Coordinates
        parallel_fig = create_parallel_coordinates(df_filtered, selected_cities=selected)

        # Update metric cards
        num_cities = str(len(df_filtered))
        avg_pm25 = f"{df_filtered['pm25'].mean():.1f} μg/m³"

        # Vienna PM2.5
        vienna_data = df_filtered[df_filtered['city'] == 'Vienna']
        vienna_pm25 = f"{vienna_data['pm25'].values[0]:.1f} μg/m³" if len(vienna_data) > 0 else "--"

        selected_text = f"{len(selected)} selected" if selected else "All Cities"

        return (
            map_fig, timeseries_fig, boxplot_fig, scatter_fig,
            correlation_fig, comparison_fig, parallel_fig,
            num_cities, avg_pm25, vienna_pm25, selected_text
        )

    # =========================================================================
    # CLICK HANDLERS: Update selected-cities-store on chart interactions
    # =========================================================================
    # These callbacks capture user interactions (clicks, selections) on each
    # chart and update the shared store, which then triggers the master callback
    # to update all other charts.

    @app.callback(
        Output('selected-cities-store', 'data'),
        # Map click
        Input('map-chart', 'clickData'),
        # Scatter selection (lasso/box select or click)
        Input('scatter-chart', 'selectedData'),
        Input('scatter-chart', 'clickData'),
        # Box plot click
        Input('boxplot-chart', 'clickData'),
        # Comparison bar click
        Input('comparison-chart', 'clickData'),
        # Quick filter buttons
        Input('btn-vienna-cluster', 'n_clicks'),
        Input('btn-top-clean', 'n_clicks'),
        Input('btn-reset', 'n_clicks'),
        # Current state
        State('selected-cities-store', 'data'),
        prevent_initial_call=True,
    )
    def update_selection(map_click, scatter_selected, scatter_click,
                         box_click, bar_click,
                         btn_vienna, btn_clean, btn_reset,
                         current_selection):
        """
        Handle all click/selection events and update the shared selection store.

        This is the "brushing" part - capturing user selections.
        The "linking" happens when other charts read from this store.
        """
        triggered_id = ctx.triggered_id

        # Reset button - clear all selections
        if triggered_id == 'btn-reset':
            return []

        # Vienna's Cluster button
        if triggered_id == 'btn-vienna-cluster':
            vienna_cluster = df_summary[df_summary['city'] == 'Vienna']['cluster'].values[0]
            cluster_cities = df_summary[df_summary['cluster'] == vienna_cluster]['city'].tolist()
            return cluster_cities

        # Top 10 Cleanest button
        if triggered_id == 'btn-top-clean':
            top_cities = df_summary.nsmallest(10, 'pm25')['city'].tolist()
            return top_cities

        # Map click - select single city
        if triggered_id == 'map-chart' and map_click:
            try:
                city = map_click['points'][0]['customdata']
                if city:
                    # Toggle selection (add or remove)
                    current = current_selection or []
                    if city in current:
                        current.remove(city)
                    else:
                        current.append(city)
                    return current
            except (KeyError, IndexError, TypeError):
                pass

        # Scatter lasso/box selection - select multiple cities
        if triggered_id == 'scatter-chart' and scatter_selected:
            try:
                cities = [point['customdata'] for point in scatter_selected['points']
                          if point.get('customdata')]
                return cities
            except (KeyError, TypeError):
                pass

        # Scatter click - select single city
        if triggered_id == 'scatter-chart' and scatter_click:
            try:
                city = scatter_click['points'][0].get('customdata') or \
                       scatter_click['points'][0].get('text')
                if city:
                    current = current_selection or []
                    if city in current:
                        current.remove(city)
                    else:
                        current.append(city)
                    return current
            except (KeyError, IndexError, TypeError):
                pass

        # Box plot click - could select cluster's cities
        if triggered_id == 'boxplot-chart' and box_click:
            try:
                # Get cluster from the clicked box
                cluster_name = box_click['points'][0].get('x')
                if cluster_name:
                    # Find cluster ID from name
                    for cid, cname in CLUSTER_NAMES.items():
                        if cname == cluster_name:
                            cluster_cities = df_summary[
                                df_summary['cluster'] == cid
                            ]['city'].tolist()
                            return cluster_cities
            except (KeyError, IndexError, TypeError):
                pass

        # Comparison bar click - select single city
        if triggered_id == 'comparison-chart' and bar_click:
            try:
                city = bar_click['points'][0].get('customdata') or \
                       bar_click['points'][0].get('y')
                if city:
                    current = current_selection or []
                    if city in current:
                        current.remove(city)
                    else:
                        current.append(city)
                    return current
            except (KeyError, IndexError, TypeError):
                pass

        # No valid selection - keep current
        return current_selection or []

    # =========================================================================
    # ADDITIONAL UI CALLBACKS
    # =========================================================================

    @app.callback(
        Output('cluster-filter', 'value'),
        Input('btn-vienna-cluster', 'n_clicks'),
        Input('btn-reset', 'n_clicks'),
        State('cluster-filter', 'value'),
        prevent_initial_call=True,
    )
    def update_cluster_filter(btn_vienna, btn_reset, current):
        """Update cluster filter when quick buttons are pressed."""
        triggered_id = ctx.triggered_id

        if triggered_id == 'btn-reset':
            return [0, 1, 2, 3]

        if triggered_id == 'btn-vienna-cluster':
            vienna_cluster = df_summary[df_summary['city'] == 'Vienna']['cluster'].values[0]
            return [vienna_cluster]

        return current


def load_data():
    """Load the pre-processed data files."""
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    # Load clustered summary data
    summary_path = os.path.join(data_dir, 'cities_clustered.csv')
    df_summary = pd.read_csv(summary_path)

    # Load time series data
    ts_path = os.path.join(data_dir, 'cities_timeseries.csv')
    df_timeseries = pd.read_csv(ts_path)

    # Add cluster info to timeseries (for filtering)
    cluster_map = df_summary.set_index('city')['cluster'].to_dict()
    df_timeseries['cluster'] = df_timeseries['city'].map(cluster_map)

    return df_summary, df_timeseries
