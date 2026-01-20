"""
Styling Configuration for Urban Environmental Quality Dashboard
All colors, fonts, and chart styling in one place for easy customization.
"""

# =============================================================================
# COLOR PALETTE
# =============================================================================
# Professional blue/gray color scheme with orange accent for Vienna
# Using ColorBrewer-inspired colorblind-friendly palette
COLORS = {
    # Primary colors
    'primary': '#2E5C8A',           # Deep blue - main elements
    'secondary': '#5B8DB8',         # Medium blue - secondary elements
    'accent': '#D95F02',            # Orange - Vienna highlighting (colorblind-safe)

    # Cluster colors - ColorBrewer "Dark2" qualitative palette (colorblind-friendly)
    # Only 4 colors needed, all distinguishable for most color vision deficiencies
    'cluster_1': '#1B9E77',         # Teal - Clean cities
    'cluster_2': '#7570B3',         # Purple - Moderate cities
    'cluster_3': '#E7298A',         # Magenta - High density
    'cluster_4': '#66A61E',         # Green - Industrial (distinct from teal)

    # UI colors
    'background': '#FFFFFF',        # White background
    'card_bg': '#F8F9FA',           # Light gray for cards
    'text': '#333333',              # Dark gray text
    'text_light': '#666666',        # Medium gray text
    'grid': '#EEEEEE',              # Light grid lines
    'border': '#DDDDDD',            # Border color

    # Selection states
    'selected': '#D95F02',          # Orange for selection (colorblind-safe)
    'unselected': '#CCCCCC',        # Light gray for unselected
    'hover': '#E8F4FD',             # Light blue for hover

    # Correlation heatmap - colorblind-friendly diverging (blue-white-orange)
    'corr_negative': '#2166AC',     # Blue for negative correlation
    'corr_neutral': '#F7F7F7',      # Off-white for zero
    'corr_positive': '#B2182B',     # Dark red for positive (distinguishable from blue)
}

# Cluster color list for easy iteration
CLUSTER_COLORS = [
    COLORS['cluster_1'],
    COLORS['cluster_2'],
    COLORS['cluster_3'],
    COLORS['cluster_4'],
]

# =============================================================================
# TYPOGRAPHY
# =============================================================================
FONTS = {
    'family': 'Arial, Helvetica, sans-serif',
    'title_size': 26,
    'subtitle_size': 18,
    'body_size': 14,
    'small_size': 12,
    'axis_size': 11,
}

# =============================================================================
# SPACING
# =============================================================================
SPACING = {
    'padding': 20,
    'margin': 15,
    'card_padding': 15,
    'chart_margin': {'l': 50, 'r': 20, 't': 40, 'b': 40},
}

# =============================================================================
# CHART LAYOUT TEMPLATE
# =============================================================================
def get_chart_layout(title='', height=None, show_legend=True):
    """
    Returns a consistent Plotly layout configuration for all charts.

    Args:
        title: Chart title string
        height: Optional height in pixels
        show_legend: Whether to show the legend

    Returns:
        dict: Plotly layout configuration
    """
    layout = {
        'title': {
            'text': title,
            'font': {
                'family': FONTS['family'],
                'size': FONTS['subtitle_size'],
                'color': COLORS['text'],
            },
            'x': 0.5,
            'xanchor': 'center',
        },
        'font': {
            'family': FONTS['family'],
            'size': FONTS['body_size'],
            'color': COLORS['text'],
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'margin': SPACING['chart_margin'],
        'xaxis': {
            'showgrid': True,
            'gridcolor': COLORS['grid'],
            'gridwidth': 1,
            'showline': True,
            'linecolor': COLORS['border'],
            'linewidth': 1,
            'tickfont': {'size': FONTS['axis_size']},
            'title_font': {'size': FONTS['body_size']},
        },
        'yaxis': {
            'showgrid': True,
            'gridcolor': COLORS['grid'],
            'gridwidth': 1,
            'showline': True,
            'linecolor': COLORS['border'],
            'linewidth': 1,
            'tickfont': {'size': FONTS['axis_size']},
            'title_font': {'size': FONTS['body_size']},
        },
        'hoverlabel': {
            'bgcolor': 'white',
            'font_size': FONTS['body_size'],
            'font_family': FONTS['family'],
            'bordercolor': COLORS['border'],
        },
        'showlegend': show_legend,
        'legend': {
            'bgcolor': 'rgba(255,255,255,0.9)',
            'bordercolor': COLORS['border'],
            'borderwidth': 1,
            'font': {'size': FONTS['small_size']},
        },
    }

    if height:
        layout['height'] = height

    return layout


# =============================================================================
# CSS STYLES FOR DASH COMPONENTS
# =============================================================================
CARD_STYLE = {
    'backgroundColor': COLORS['background'],
    'borderRadius': '8px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'padding': f'{SPACING["card_padding"]}px',
    'height': '100%',
}

METRIC_CARD_STYLE = {
    'backgroundColor': COLORS['card_bg'],
    'borderRadius': '8px',
    'padding': '15px 20px',
    'textAlign': 'center',
    'border': f'1px solid {COLORS["border"]}',
}

HEADER_STYLE = {
    'backgroundColor': COLORS['primary'],
    'color': 'white',
    'padding': '15px 30px',
    'marginBottom': '20px',
}

TITLE_STYLE = {
    'fontFamily': FONTS['family'],
    'fontSize': f'{FONTS["title_size"]}px',
    'fontWeight': 'bold',
    'color': 'white',
    'margin': '0',
}

SUBTITLE_STYLE = {
    'fontFamily': FONTS['family'],
    'fontSize': f'{FONTS["body_size"]}px',
    'fontWeight': 'normal',
    'color': 'rgba(255,255,255,0.8)',
    'margin': '5px 0 0 0',
}

FILTER_LABEL_STYLE = {
    'fontFamily': FONTS['family'],
    'fontSize': f'{FONTS["small_size"]}px',
    'fontWeight': '600',
    'color': COLORS['text'],
    'marginBottom': '5px',
}

CHART_TITLE_STYLE = {
    'fontFamily': FONTS['family'],
    'fontSize': f'{FONTS["subtitle_size"]}px',
    'fontWeight': '600',
    'color': COLORS['text'],
    'marginBottom': '10px',
    'textAlign': 'center',
}

# =============================================================================
# CLUSTER NAMES AND DESCRIPTIONS
# =============================================================================
CLUSTER_NAMES = {
    0: 'Clean & Green',
    1: 'Moderate Urban',
    2: 'High Density',
    3: 'Industrial/Polluted',
}

CLUSTER_DESCRIPTIONS = {
    0: 'Low pollution, high green space',
    1: 'Balanced environmental profile',
    2: 'Dense urban areas, moderate pollution',
    3: 'High pollution, industrial activity',
}
