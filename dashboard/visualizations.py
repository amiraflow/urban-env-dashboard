"""
Visualization Components for Urban Environmental Quality Dashboard

This module contains functions to create each of the 7 visualizations:
1. Geographic Map (Scattermapbox)
2. Time Series Chart (Line)
3. Cluster Box Plots (Box)
4. Scatter Plot (Density vs Air Quality)
5. Correlation Heatmap
6. City Comparison Bars
7. Parallel Coordinates

All visualizations support brushing & linking through consistent data structures
and callback integration.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from dashboard.styles import (
    COLORS, CLUSTER_COLORS, FONTS, SPACING,
    get_chart_layout, CLUSTER_NAMES, CLUSTER_DESCRIPTIONS
)


# =============================================================================
# 1. GEOGRAPHIC MAP
# =============================================================================
def create_map(df, selected_cities=None, highlight_vienna=True):
    """
    Create geographic scatter map with cities colored by PM2.5 levels.

    Args:
        df: DataFrame with city data including lat, lon, pm25
        selected_cities: List of city names to highlight (for brushing)
        highlight_vienna: Whether to give Vienna special styling

    Returns:
        plotly.graph_objects.Figure
    """
    df = df.copy()

    # Determine opacity based on selection
    if selected_cities and len(selected_cities) > 0:
        df['opacity'] = df['city'].apply(
            lambda x: 1.0 if x in selected_cities or x == 'Vienna' else 0.2
        )
    else:
        df['opacity'] = 0.8

    # Create size column based on population (area-proportional scaling)
    # Using sqrt to make marker AREA proportional to population, not diameter
    df['marker_size'] = 6 + np.sqrt(df['population'] / df['population'].max()) * 12

    # Separate Vienna for special styling
    vienna = df[df['city'] == 'Vienna']
    other_cities = df[df['city'] != 'Vienna']

    fig = go.Figure()

    # Add other cities
    fig.add_trace(go.Scattergeo(
        lon=other_cities['lon'],
        lat=other_cities['lat'],
        mode='markers',
        marker=dict(
            size=other_cities['marker_size'],
            color=other_cities['pm25'],
            # Using Viridis - perceptually uniform and colorblind-friendly
            colorscale='Viridis',
            reversescale=True,  # Yellow = clean (low PM2.5), Purple = polluted (high)
            cmin=5,
            cmax=80,
            opacity=other_cities['opacity'].tolist(),
            line=dict(width=1, color='white'),
            colorbar=dict(
                title=dict(text='PM2.5<br>(μg/m³)', font=dict(size=11)),
                thickness=15,
                len=0.5,
                y=0.5,
            )
        ),
        text=other_cities.apply(
            lambda r: f"<b>{r['city']}</b>, {r['country']}<br>" +
                      f"PM2.5: {r['pm25']:.1f} μg/m³<br>" +
                      f"Cluster: {CLUSTER_NAMES.get(r['cluster'], r['cluster'])}",
            axis=1
        ),
        hoverinfo='text',
        customdata=other_cities['city'],
        name='Cities'
    ))

    # Add Vienna with special styling
    if highlight_vienna and len(vienna) > 0:
        fig.add_trace(go.Scattergeo(
            lon=vienna['lon'],
            lat=vienna['lat'],
            mode='markers+text',
            marker=dict(
                size=18,
                color=COLORS['accent'],
                symbol='star',
                line=dict(width=2, color='black'),
            ),
            text=['Vienna'],
            textposition='top center',
            textfont=dict(size=12, color=COLORS['accent'], family='Arial'),
            hovertext=vienna.apply(
                lambda r: f"<b>{r['city']}</b>, {r['country']}<br>" +
                          f"PM2.5: {r['pm25']:.1f} μg/m³<br>" +
                          f"Cluster: {CLUSTER_NAMES.get(r['cluster'], r['cluster'])}",
                axis=1
            ),
            hoverinfo='text',
            customdata=vienna['city'],
            name='Vienna'
        ))

    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor='#F5F5F5',
            countrycolor='#CCCCCC',
            coastlinecolor='#AAAAAA',
            showocean=True,
            oceancolor='#E8F4FD',
            showlakes=True,
            lakecolor='#E8F4FD',
            projection_type='natural earth',
            center=dict(lat=30, lon=10),
            projection_scale=1.2,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor=COLORS['background'],
        font=dict(family=FONTS['family'], size=FONTS['body_size']),
        showlegend=False,
        height=280,
    )

    return fig


# =============================================================================
# 2. TIME SERIES CHART
# =============================================================================
def create_time_series(df_timeseries, df_summary, selected_cities=None):
    """
    Create time series line chart showing PM2.5 trends over time.

    Shows:
    - Vienna (bold orange line)
    - Vienna's cluster average (medium blue)
    - Global average (gray dashed)
    - Selected cities (if any)

    Args:
        df_timeseries: DataFrame with monthly time series data
        df_summary: DataFrame with city summary including cluster assignments
        selected_cities: List of additional cities to show

    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()

    # Get Vienna's cluster
    vienna_cluster = df_summary[df_summary['city'] == 'Vienna']['cluster'].values[0]

    # Calculate averages
    df_ts = df_timeseries.copy()
    df_ts['date'] = pd.to_datetime(df_ts['date'])

    # Global average
    global_avg = df_ts.groupby('date')['pm25'].mean().reset_index()

    # Cluster average (Vienna's cluster)
    cluster_cities = df_summary[df_summary['cluster'] == vienna_cluster]['city'].tolist()
    cluster_data = df_ts[df_ts['city'].isin(cluster_cities)]
    cluster_avg = cluster_data.groupby('date')['pm25'].mean().reset_index()

    # Vienna data
    vienna_data = df_ts[df_ts['city'] == 'Vienna']

    # Add global average (bottom layer)
    fig.add_trace(go.Scatter(
        x=global_avg['date'],
        y=global_avg['pm25'],
        mode='lines',
        name='Global Average',
        line=dict(color=COLORS['grid'], width=1.5, dash='dash'),
        hovertemplate='Global Avg: %{y:.1f} μg/m³<extra></extra>'
    ))

    # Add cluster average
    fig.add_trace(go.Scatter(
        x=cluster_avg['date'],
        y=cluster_avg['pm25'],
        mode='lines',
        name=f'Cluster Avg ({CLUSTER_NAMES.get(vienna_cluster, "Vienna\'s")})',
        line=dict(color=COLORS['primary'], width=2),
        hovertemplate='Cluster Avg: %{y:.1f} μg/m³<extra></extra>'
    ))

    # Add selected cities (if any)
    if selected_cities:
        for city in selected_cities:
            if city != 'Vienna':
                city_data = df_ts[df_ts['city'] == city]
                if len(city_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=city_data['date'],
                        y=city_data['pm25'],
                        mode='lines',
                        name=city,
                        line=dict(width=1.5),
                        opacity=0.7,
                        hovertemplate=f'{city}: %{{y:.1f}} μg/m³<extra></extra>'
                    ))

    # Add Vienna (top layer, prominent)
    fig.add_trace(go.Scatter(
        x=vienna_data['date'],
        y=vienna_data['pm25'],
        mode='lines',
        name='Vienna',
        line=dict(color=COLORS['accent'], width=3),
        hovertemplate='Vienna: %{y:.1f} μg/m³<extra></extra>'
    ))

    layout = get_chart_layout(height=280)
    layout.update(
        xaxis_title='',
        yaxis_title='PM2.5 (μg/m³)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10),
        ),
        margin=dict(l=50, r=10, t=30, b=30),
        hovermode='x unified',
    )

    fig.update_layout(layout)

    return fig


# =============================================================================
# 3. CLUSTER BOX PLOTS
# =============================================================================
def create_cluster_boxplot(df, indicator='pm25', selected_cluster=None):
    """
    Create box plots showing distribution of an indicator across clusters.

    Args:
        df: DataFrame with city data including cluster assignments
        indicator: Which indicator to show ('pm25', 'no2', 'green_space_pct', etc.)
        selected_cluster: Cluster to highlight (for brushing)

    Returns:
        plotly.graph_objects.Figure
    """
    indicator_labels = {
        'pm25': 'PM2.5 (μg/m³)',
        'pm10': 'PM10 (μg/m³)',
        'no2': 'NO₂ (μg/m³)',
        'o3': 'O₃ (μg/m³)',
        'green_space_pct': 'Green Space (%)',
        'air_quality_index': 'Air Quality Index',
    }

    fig = go.Figure()

    # Add box for each cluster
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[df['cluster'] == cluster_id][indicator]
        cluster_name = CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}')

        opacity = 1.0 if selected_cluster is None or selected_cluster == cluster_id else 0.3

        fig.add_trace(go.Box(
            y=cluster_data,
            name=cluster_name,
            marker_color=CLUSTER_COLORS[cluster_id],
            opacity=opacity,
            boxpoints='outliers',
            hovertemplate=f'{cluster_name}<br>{indicator_labels.get(indicator, indicator)}: %{{y:.1f}}<extra></extra>'
        ))

    # Mark Vienna's position
    vienna = df[df['city'] == 'Vienna'].iloc[0]
    vienna_cluster = int(vienna['cluster'])
    vienna_value = vienna[indicator]

    fig.add_trace(go.Scatter(
        x=[CLUSTER_NAMES.get(vienna_cluster, f'Cluster {vienna_cluster}')],
        y=[vienna_value],
        mode='markers',
        marker=dict(
            symbol='star',
            size=15,
            color=COLORS['accent'],
            line=dict(width=1, color='black')
        ),
        name='Vienna',
        hovertemplate=f'Vienna: {vienna_value:.1f}<extra></extra>'
    ))

    layout = get_chart_layout(height=280)
    layout.update(
        xaxis_title='',
        yaxis_title=indicator_labels.get(indicator, indicator),
        showlegend=False,
        margin=dict(l=50, r=10, t=30, b=50),
    )

    fig.update_layout(layout)

    return fig


# =============================================================================
# 4. SCATTER PLOT (Density vs Air Quality)
# =============================================================================
def create_scatter_plot(df, selected_cities=None, x_var='population_density', y_var='pm25'):
    """
    Create scatter plot showing relationship between two variables.

    Args:
        df: DataFrame with city data
        selected_cities: List of cities to highlight
        x_var: Variable for x-axis
        y_var: Variable for y-axis

    Returns:
        plotly.graph_objects.Figure
    """
    var_labels = {
        'population_density': 'Population Density (per km²)',
        'pm25': 'PM2.5 (μg/m³)',
        'green_space_pct': 'Green Space (%)',
        'traffic_intensity': 'Traffic Intensity',
        'air_quality_index': 'Air Quality Index',
    }

    df = df.copy()

    # Determine opacity based on selection (size is constant - not encoding data)
    if selected_cities and len(selected_cities) > 0:
        df['opacity'] = df['city'].apply(
            lambda x: 1.0 if x in selected_cities or x == 'Vienna' else 0.15
        )
    else:
        df['opacity'] = 0.8

    # Constant marker size (not encoding any variable)
    df['size'] = 9

    fig = go.Figure()

    # Add points for each cluster (excluding Vienna)
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[(df['cluster'] == cluster_id) & (df['city'] != 'Vienna')]

        fig.add_trace(go.Scatter(
            x=cluster_data[x_var],
            y=cluster_data[y_var],
            mode='markers',
            name=CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}'),
            marker=dict(
                size=cluster_data['size'],
                color=CLUSTER_COLORS[cluster_id],
                opacity=cluster_data['opacity'].tolist(),
                line=dict(width=0.5, color='white')
            ),
            text=cluster_data['city'],
            customdata=cluster_data['city'],
            hovertemplate='<b>%{text}</b><br>' +
                          f'{var_labels.get(x_var, x_var)}: %{{x:,.0f}}<br>' +
                          f'{var_labels.get(y_var, y_var)}: %{{y:.1f}}<extra></extra>'
        ))

    # Add Vienna with special marker
    vienna = df[df['city'] == 'Vienna'].iloc[0]
    fig.add_trace(go.Scatter(
        x=[vienna[x_var]],
        y=[vienna[y_var]],
        mode='markers',
        name='Vienna',
        marker=dict(
            size=15,
            color=COLORS['accent'],
            symbol='star',
            line=dict(width=1.5, color='black')
        ),
        hovertemplate='<b>Vienna</b><br>' +
                      f'{var_labels.get(x_var, x_var)}: %{{x:,.0f}}<br>' +
                      f'{var_labels.get(y_var, y_var)}: %{{y:.1f}}<extra></extra>'
    ))

    # Add trend line
    z = np.polyfit(df[x_var], df[y_var], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[x_var].min(), df[x_var].max(), 100)

    fig.add_trace(go.Scatter(
        x=x_line,
        y=p(x_line),
        mode='lines',
        name='Trend',
        line=dict(color=COLORS['text_light'], width=1, dash='dash'),
        hoverinfo='skip'
    ))

    layout = get_chart_layout(height=280)
    layout.update(
        xaxis_title=var_labels.get(x_var, x_var),
        yaxis_title=var_labels.get(y_var, y_var),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=9),
        ),
        margin=dict(l=60, r=10, t=30, b=50),
    )

    # Use log scale for density if values span large range
    if x_var == 'population_density':
        layout['xaxis']['type'] = 'log'

    fig.update_layout(layout)

    return fig


# =============================================================================
# 5. CORRELATION HEATMAP
# =============================================================================
def create_correlation_heatmap(df):
    """
    Create correlation heatmap of environmental variables.

    Args:
        df: DataFrame with city data

    Returns:
        plotly.graph_objects.Figure
    """
    # Select numeric columns for correlation
    corr_cols = ['pm25', 'pm10', 'no2', 'o3', 'green_space_pct',
                 'population_density', 'traffic_intensity', 'air_quality_index']

    col_labels = ['PM2.5', 'PM10', 'NO₂', 'O₃', 'Green Space',
                  'Pop. Density', 'Traffic', 'AQI']

    # Calculate correlation matrix
    corr_matrix = df[corr_cols].corr()

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=col_labels,
        y=col_labels,
        colorscale=[
            [0, COLORS['corr_negative']],
            [0.5, COLORS['corr_neutral']],
            [1, COLORS['corr_positive']]
        ],
        zmin=-1,
        zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont=dict(size=10),
        hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>',
        colorbar=dict(
            title='Correlation',
            thickness=12,
            len=0.8,
        )
    ))

    layout = get_chart_layout(height=280)
    layout.update(
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=9)),
        margin=dict(l=80, r=10, t=30, b=80),
    )

    fig.update_layout(layout)

    return fig


# =============================================================================
# 6. CITY COMPARISON BARS
# =============================================================================
def create_city_comparison(df, comparison_cities=None, indicator='pm25'):
    """
    Create horizontal bar chart comparing Vienna with peer cities.

    Args:
        df: DataFrame with city data
        comparison_cities: List of cities to compare (default: Vienna's cluster peers)
        indicator: Which indicator to compare

    Returns:
        plotly.graph_objects.Figure
    """
    indicator_labels = {
        'pm25': 'PM2.5 (μg/m³)',
        'pm10': 'PM10 (μg/m³)',
        'no2': 'NO₂ (μg/m³)',
        'green_space_pct': 'Green Space (%)',
        'air_quality_index': 'Air Quality Index',
    }

    # Default: Vienna + top 5 peers from same cluster
    if comparison_cities is None or len(comparison_cities) == 0:
        vienna_cluster = df[df['city'] == 'Vienna']['cluster'].values[0]
        cluster_cities = df[df['cluster'] == vienna_cluster].sort_values(indicator)
        comparison_cities = cluster_cities['city'].head(6).tolist()
        if 'Vienna' not in comparison_cities:
            comparison_cities = ['Vienna'] + comparison_cities[:5]

    # Filter to comparison cities and sort
    compare_df = df[df['city'].isin(comparison_cities)].sort_values(indicator)

    # Create colors list (Vienna in accent, others by cluster)
    colors = [COLORS['accent'] if city == 'Vienna'
              else CLUSTER_COLORS[df[df['city'] == city]['cluster'].values[0]]
              for city in compare_df['city']]

    fig = go.Figure(go.Bar(
        x=compare_df[indicator],
        y=compare_df['city'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=1, color='white')
        ),
        text=compare_df[indicator].round(1),
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{y}</b><br>' +
                      f'{indicator_labels.get(indicator, indicator)}: %{{x:.1f}}<extra></extra>',
        customdata=compare_df['city'],
    ))

    layout = get_chart_layout(height=280)
    layout.update(
        xaxis_title=indicator_labels.get(indicator, indicator),
        yaxis_title='',
        margin=dict(l=100, r=40, t=30, b=40),
        yaxis=dict(tickfont=dict(size=11)),
    )

    fig.update_layout(layout)

    return fig


# =============================================================================
# 7. PARALLEL COORDINATES
# =============================================================================
def create_parallel_coordinates(df, selected_cities=None):
    """
    Create parallel coordinates plot for multi-dimensional comparison.

    Args:
        df: DataFrame with city data
        selected_cities: List of cities to highlight

    Returns:
        plotly.graph_objects.Figure
    """
    df = df.copy()

    # Columns to include
    dimensions = ['pm25', 'pm10', 'no2', 'o3', 'green_space_pct',
                  'population_density', 'traffic_intensity', 'air_quality_index']

    dim_labels = ['PM2.5', 'PM10', 'NO₂', 'O₃', 'Green<br>Space',
                  'Pop.<br>Density', 'Traffic', 'AQI']

    # Normalize data for better visualization
    df_norm = df.copy()
    for col in dimensions:
        min_val = df[col].min()
        max_val = df[col].max()
        df_norm[col + '_norm'] = (df[col] - min_val) / (max_val - min_val)

    # Create dimension specs
    dims = []
    for col, label in zip(dimensions, dim_labels):
        dims.append(dict(
            range=[df[col].min(), df[col].max()],
            label=label,
            values=df[col],
        ))

    # Determine line colors based on selection
    if selected_cities and len(selected_cities) > 0:
        # Highlight selected + Vienna
        color_values = []
        for _, row in df.iterrows():
            if row['city'] == 'Vienna':
                color_values.append(2)  # Vienna always visible
            elif row['city'] in selected_cities:
                color_values.append(1)  # Selected
            else:
                color_values.append(0)  # Not selected
        colorscale = [
            [0, 'rgba(200,200,200,0.1)'],  # Unselected - very faint
            [0.5, COLORS['primary']],      # Selected
            [1, COLORS['accent']]          # Vienna
        ]
    else:
        # Color by cluster, Vienna highlighted
        color_values = []
        for _, row in df.iterrows():
            if row['city'] == 'Vienna':
                color_values.append(5)  # Special value for Vienna
            else:
                color_values.append(row['cluster'])
        colorscale = [
            [0, CLUSTER_COLORS[0]],
            [0.25, CLUSTER_COLORS[1]],
            [0.5, CLUSTER_COLORS[2]],
            [0.75, CLUSTER_COLORS[3]],
            [1, COLORS['accent']]
        ]

    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=color_values,
            colorscale=colorscale,
        ),
        dimensions=dims,
        labelangle=-30,
        labelside='top',
    ))

    layout = get_chart_layout(height=200)
    layout.update(
        margin=dict(l=60, r=60, t=50, b=20),
    )

    fig.update_layout(layout)

    return fig
