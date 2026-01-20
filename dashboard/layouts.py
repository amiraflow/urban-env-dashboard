"""
Dashboard Layout for Urban Environmental Quality Dashboard

Defines the HTML/CSS structure of the dashboard using Dash components.
Layout is designed to fit on one screen (no scrolling) with professional styling.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from dashboard.styles import (
    COLORS, CLUSTER_COLORS, FONTS, SPACING,
    CARD_STYLE, METRIC_CARD_STYLE, HEADER_STYLE, TITLE_STYLE, SUBTITLE_STYLE,
    FILTER_LABEL_STYLE, CLUSTER_NAMES
)


def create_header():
    """Create the dashboard header with title and subtitle."""
    return html.Div([
        html.H1("Urban Environmental Quality Dashboard",
                style=TITLE_STYLE),
        html.P("Analyzing Air Quality and Livability Across World Cities - Vienna Focus",
               style=SUBTITLE_STYLE),
    ], style=HEADER_STYLE)


def create_metric_card(id_prefix, title, value="--", subtitle=""):
    """Create a metric display card."""
    return html.Div([
        html.Div(title, style={
            'fontSize': '12px',
            'color': COLORS['text_light'],
            'marginBottom': '5px',
            'textTransform': 'uppercase',
            'letterSpacing': '0.5px',
        }),
        html.Div(id=f'{id_prefix}-value', children=value, style={
            'fontSize': '24px',
            'fontWeight': 'bold',
            'color': COLORS['primary'],
        }),
        html.Div(id=f'{id_prefix}-subtitle', children=subtitle, style={
            'fontSize': '11px',
            'color': COLORS['text_light'],
        }),
    ], style=METRIC_CARD_STYLE)


def create_metrics_row():
    """Create the row of key metric cards."""
    return dbc.Row([
        dbc.Col(create_metric_card('cities', 'Cities Analyzed', '31'), width=2),
        dbc.Col(create_metric_card('avg-pm25', 'Avg PM2.5', '--'), width=2),
        dbc.Col(create_metric_card('vienna-rank', 'Vienna Rank', '--'), width=2),
        dbc.Col(create_metric_card('vienna-cluster', 'Vienna Cluster', 'Clean & Green'), width=2),
        dbc.Col(create_metric_card('time-range', 'Time Range', '2020-2023'), width=2),
        dbc.Col(create_metric_card('selected', 'Selected', 'All Cities'), width=2),
    ], className='mb-3', style={'marginLeft': '10px', 'marginRight': '10px'})


def create_filter_panel():
    """Create the filter controls panel."""
    return html.Div([
        dbc.Row([
            # Region Filter
            dbc.Col([
                html.Label('Region', style=FILTER_LABEL_STYLE),
                dcc.Dropdown(
                    id='region-filter',
                    options=[
                        {'label': 'All Regions', 'value': 'all'},
                        {'label': 'Europe', 'value': 'Europe'},
                        {'label': 'Asia', 'value': 'Asia'},
                        {'label': 'Americas', 'value': 'Americas'},
                        {'label': 'Africa', 'value': 'Africa'},
                        {'label': 'Oceania', 'value': 'Oceania'},
                    ],
                    value='all',
                    clearable=False,
                    style={'fontSize': '12px'},
                ),
            ], width=2),

            # Year Range
            dbc.Col([
                html.Label('Year Range', style=FILTER_LABEL_STYLE),
                dcc.RangeSlider(
                    id='year-slider',
                    min=2020,
                    max=2023,
                    step=1,
                    value=[2020, 2023],
                    marks={y: str(y) for y in range(2020, 2024)},
                    tooltip={'placement': 'bottom', 'always_visible': False},
                ),
            ], width=3),

            # Cluster Filter
            dbc.Col([
                html.Label('Clusters', style=FILTER_LABEL_STYLE),
                dcc.Checklist(
                    id='cluster-filter',
                    options=[
                        {'label': f' {CLUSTER_NAMES[i]}', 'value': i}
                        for i in range(4)
                    ],
                    value=[0, 1, 2, 3],
                    inline=True,
                    style={'fontSize': '11px'},
                    inputStyle={'marginRight': '5px'},
                    labelStyle={'marginRight': '15px'},
                ),
            ], width=4),

            # Quick Filters & Reset
            dbc.Col([
                html.Label('Quick Filters', style=FILTER_LABEL_STYLE),
                html.Div([
                    dbc.Button("Vienna's Cluster", id='btn-vienna-cluster',
                               size='sm', outline=True, color='primary',
                               className='me-1', style={'fontSize': '10px'}),
                    dbc.Button("Top 10 Cleanest", id='btn-top-clean',
                               size='sm', outline=True, color='success',
                               className='me-1', style={'fontSize': '10px'}),
                    dbc.Button("Reset All", id='btn-reset',
                               size='sm', color='secondary',
                               className='me-1', style={'fontSize': '10px'}),
                    # Help button with popover
                    html.Span([
                        dbc.Button("?", id='btn-help', size='sm', color='info',
                                   style={'fontSize': '10px', 'borderRadius': '50%',
                                          'width': '22px', 'height': '22px', 'padding': '0'}),
                        dbc.Popover([
                            dbc.PopoverHeader("Interaction Tips", style={'fontWeight': 'bold'}),
                            dbc.PopoverBody([
                                html.P([html.Strong("Click"), " a city on the map to highlight it across all charts"],
                                       style={'marginBottom': '5px', 'fontSize': '11px'}),
                                html.P([html.Strong("Click"), " a bar in the comparison chart to select that city"],
                                       style={'marginBottom': '5px', 'fontSize': '11px'}),
                                html.P([html.Strong("Click"), " a box plot to select all cities in that cluster"],
                                       style={'marginBottom': '5px', 'fontSize': '11px'}),
                                html.P([html.Strong("Lasso select"), " on the scatter plot to highlight multiple cities"],
                                       style={'marginBottom': '5px', 'fontSize': '11px'}),
                                html.P([html.Strong("Click again"), " to deselect a city"],
                                       style={'marginBottom': '0', 'fontSize': '11px'}),
                            ]),
                        ], target='btn-help', trigger='hover', placement='bottom'),
                    ]),
                ]),
            ], width=3),
        ]),
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'padding': '15px 20px',
        'borderRadius': '8px',
        'marginBottom': '15px',
        'marginLeft': '15px',
        'marginRight': '15px',
    })


def create_main_layout():
    """Create the complete dashboard layout."""

    chart_card_style = {
        **CARD_STYLE,
        'padding': '12px',
    }

    header_style = {
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'marginBottom': '10px',
    }

    title_style = {
        'fontWeight': '600',
        'fontSize': '14px',
        'color': COLORS['text'],
    }

    return html.Div([
        # Store components for state management (brushing & linking)
        dcc.Store(id='selected-cities-store', data=[]),
        dcc.Store(id='selected-cluster-store', data=None),
        dcc.Store(id='filtered-data-store', data=None),

        # Header
        create_header(),

        # Metrics Row
        create_metrics_row(),

        # Filter Panel
        create_filter_panel(),

        # Main Chart Grid
        html.Div([
            # Top Row: Map, Time Series, Box Plots
            dbc.Row([
                # Map Chart
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('Geographic Distribution by PM2.5', style=title_style),
                        ], style=header_style),
                        dcc.Graph(id='map-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                    ], style=chart_card_style),
                ], width=4),

                # Time Series Chart
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('PM2.5 Trends Over Time', style=title_style),
                        ], style=header_style),
                        dcc.Graph(id='timeseries-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                    ], style=chart_card_style),
                ], width=4),

                # Box Plot with dropdown
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('Distribution by Cluster', style=title_style),
                            dcc.Dropdown(
                                id='boxplot-indicator',
                                options=[
                                    {'label': 'PM2.5', 'value': 'pm25'},
                                    {'label': 'PM10', 'value': 'pm10'},
                                    {'label': 'NO2', 'value': 'no2'},
                                    {'label': 'Green Space %', 'value': 'green_space_pct'},
                                ],
                                value='pm25',
                                clearable=False,
                                style={'width': '120px', 'fontSize': '11px'},
                            ),
                        ], style=header_style),
                        dcc.Graph(id='boxplot-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                    ], style=chart_card_style),
                ], width=4),
            ], className='mb-2 g-2'),

            # Middle Row: Scatter, Correlation, Comparison
            dbc.Row([
                # Scatter Plot with dropdown
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('Density vs Air Quality', style=title_style),
                            dcc.Dropdown(
                                id='scatter-x-var',
                                options=[
                                    {'label': 'Pop. Density', 'value': 'population_density'},
                                    {'label': 'Traffic', 'value': 'traffic_intensity'},
                                    {'label': 'Green Space', 'value': 'green_space_pct'},
                                ],
                                value='population_density',
                                clearable=False,
                                style={'width': '110px', 'fontSize': '10px'},
                            ),
                        ], style=header_style),
                        dcc.Graph(id='scatter-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                    ], style=chart_card_style),
                ], width=4),

                # Correlation Chart
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('Variable Correlations', style=title_style),
                        ], style=header_style),
                        dcc.Graph(id='correlation-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                    ], style=chart_card_style),
                ], width=4),

                # Comparison Chart with dropdown
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('Vienna vs Peer Cities', style=title_style),
                            dcc.Dropdown(
                                id='comparison-indicator',
                                options=[
                                    {'label': 'PM2.5', 'value': 'pm25'},
                                    {'label': 'Green Space', 'value': 'green_space_pct'},
                                    {'label': 'AQI', 'value': 'air_quality_index'},
                                ],
                                value='pm25',
                                clearable=False,
                                style={'width': '110px', 'fontSize': '11px'},
                            ),
                        ], style=header_style),
                        dcc.Graph(id='comparison-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                    ], style=chart_card_style),
                ], width=4),
            ], className='mb-2 g-2'),

            # Bottom Row: Parallel Coordinates (full width)
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Span('Multi-Dimensional City Comparison - Vienna Highlighted in Orange', style=title_style),
                        ], style=header_style),
                        dcc.Graph(id='parallel-chart', config={'displayModeBar': False}, style={'height': '180px'}),
                    ], style=chart_card_style),
                ], width=12),
            ], className='g-2'),

        ], style={
            'padding': '0 15px',
        }),

        # Footer
        html.Div([
            html.Span("Data: Real air quality data from OpenAQ for 31 world cities (2020-2023) | ",
                      style={'color': COLORS['text_light'], 'fontSize': '11px'}),
            html.Span("Click on any chart to highlight cities across all visualizations",
                      style={'color': COLORS['primary'], 'fontSize': '11px', 'fontWeight': '500'}),
        ], style={
            'textAlign': 'center',
            'padding': '10px',
            'marginTop': '10px',
        }),

    ], style={
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'fontFamily': FONTS['family'],
    })
