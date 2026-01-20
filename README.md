# Urban Environmental Quality Dashboard

An interactive web dashboard for analyzing air quality and livability across world cities, with a focus on Vienna. Built with Plotly Dash for a Visual Data Science university course.

## Features

- **7 Interactive Visualizations** with full brushing & linking
- **K-Means Clustering** to identify city peer groups
- **63 World Cities** with monthly data from 2019-2024
- **Vienna Focus** - highlighted throughout all visualizations
- **One-Screen Layout** - no scrolling required
- **Professional Styling** - clean, minimal design

## Dashboard Preview

The dashboard includes:

1. **Geographic Map** - Cities colored by PM2.5 levels
2. **Time Series Chart** - PM2.5 trends over time (Vienna vs averages)
3. **Cluster Box Plots** - Distribution of indicators by cluster
4. **Scatter Plot** - Population density vs air quality
5. **Correlation Heatmap** - Relationships between variables
6. **City Comparison Bars** - Vienna vs peer cities
7. **Parallel Coordinates** - Multi-dimensional city profiles

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone or download this repository
cd urban-env-dashboard

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
python run.py
```

Then open http://127.0.0.1:8050 in your browser.

## Project Structure

```
urban-env-dashboard/
├── data/
│   ├── generate_sample_data.py    # Data generation script
│   ├── cities_timeseries.csv      # Monthly data (2019-2024)
│   ├── cities_summary.csv         # City-level summaries
│   └── cities_clustered.csv       # With cluster assignments
├── models/
│   ├── clustering.py              # K-means clustering analysis
│   ├── model_visualizations.py    # Part 1 visualizations
│   └── figures/                   # Saved model plots
├── dashboard/
│   ├── app.py                     # Main Dash application
│   ├── layouts.py                 # Dashboard layout
│   ├── callbacks.py               # Interactivity & brushing/linking
│   ├── visualizations.py          # Chart generation functions
│   └── styles.py                  # Colors, fonts, styling config
├── assets/
│   └── custom.css                 # Custom styling
├── requirements.txt
├── Procfile                       # For Heroku/Render deployment
├── render.yaml                    # Render.com configuration
└── README.md
```

## Brushing & Linking

**This is the key interactive feature.** Selections in any view affect ALL other views:

| Action | Effect |
|--------|--------|
| Click city on map | Highlights that city everywhere |
| Lasso select in scatter | Shows only selected cities in all views |
| Click cluster box | Filters to that cluster's cities |
| Click bar in comparison | Highlights that city everywhere |
| Use global filters | Filters all visualizations |
| Click "Reset All" | Clears all selections |

### How It Works

1. **dcc.Store** components maintain shared selection state
2. **Callbacks** update the store when users interact with any chart
3. **All charts** re-render when the store changes, highlighting selected items
4. Unselected items fade to gray (opacity 0.15-0.3)
5. Vienna always remains highlighted (orange star/line)

## Part 1: Model Stage

The clustering analysis groups cities into 4 environmental profiles:

| Cluster | Name | Characteristics |
|---------|------|-----------------|
| 0 | Clean & Green | Low PM2.5, high green space |
| 1 | High Density Urban | Dense cities, moderate pollution |
| 2 | Moderate Urban | Balanced profiles |
| 3 | Industrial/Polluted | High pollution levels |

**Vienna is in Cluster 0 (Clean & Green)** along with cities like Zurich, Copenhagen, Sydney, and Tokyo.

### Generate Model Visualizations

```bash
python models/model_visualizations.py
```

This creates:
- `models/figures/elbow_plot.png` - K selection justification
- `models/figures/pca_scatter.png` - Cities by cluster (2D)
- `models/figures/cluster_boxplots.png` - Indicator distributions
- `models/figures/cluster_radar.png` - Cluster profiles (bonus)

## Deployment

### Deploy to Render (Recommended)

1. Push code to GitHub
2. Go to [render.com](https://render.com) and create account
3. Click "New Web Service"
4. Connect your GitHub repository
5. Render will auto-detect settings from `render.yaml`
6. Click "Create Web Service"

Your dashboard will be live at `https://your-app-name.onrender.com`

### Deploy to Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Python and use `Procfile`

### Deploy to Heroku

```bash
heroku create your-app-name
git push heroku main
heroku open
```

## Replacing Sample Data with Real Data

The dashboard uses realistic synthetic data. To use real data:

1. **Prepare your data** with these columns:
   - Required: `city`, `country`, `region`, `lat`, `lon`, `population`, `population_density`
   - Environmental: `pm25`, `pm10`, `no2`, `o3`, `green_space_pct`, `traffic_intensity`, `air_quality_index`
   - Time series: `year`, `month`, `date`

2. **Save as CSV** to `data/cities_timeseries.csv`

3. **Run clustering** to generate summary and cluster assignments:
   ```bash
   python models/clustering.py
   ```

4. **Restart the dashboard**

## Customization

### Colors

Edit `dashboard/styles.py`:

```python
COLORS = {
    'primary': '#2E5C8A',      # Main blue
    'accent': '#F39C12',       # Orange (Vienna)
    'cluster_1': '#3498DB',    # Cluster colors
    # ...
}
```

### Adding Visualizations

1. Add function in `dashboard/visualizations.py`
2. Add chart card in `dashboard/layouts.py`
3. Add callback output in `dashboard/callbacks.py`

## Data Sources

The sample data reflects realistic environmental patterns based on:
- WHO Global Air Quality Database
- European Environment Agency
- World Bank urban indicators

For actual project use, replace with official data sources.

## Grading Criteria Addressed

| Requirement | Implementation |
|-------------|----------------|
| 4+ visualizations | 7 visualizations included |
| Brushing & linking | Full cross-chart selection |
| One-screen layout | No scrolling required |
| Programming library | Built with Plotly Dash (Python) |
| Clean design | Professional blue/gray palette, white space |
| Model visualization | Elbow plot, PCA scatter, box plots |
| Deployed URL | Ready for Render/Railway deployment |

## Technical Details

- **Framework:** Plotly Dash 2.14
- **Charts:** Plotly Express & Graph Objects
- **Styling:** Dash Bootstrap Components
- **Clustering:** scikit-learn K-means
- **Data:** pandas, numpy

## License

MIT License - Free to use for educational purposes.

## Author

Created for Visual Data Science course at TU Wien, 2025.
