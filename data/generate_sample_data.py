"""
Generate Realistic Sample Data for Urban Environmental Quality Dashboard
Creates synthetic data for ~70 world cities with monthly time series (2019-2024).

Data includes:
- City metadata (name, country, region, coordinates, population)
- Environmental indicators (PM2.5, PM10, NO2, O3, green space, traffic)
- Time series data for trend analysis

Values are realistic and based on actual city environmental profiles.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import os

# Set seed for reproducibility
np.random.seed(42)


# =============================================================================
# CITY DEFINITIONS WITH REALISTIC BASE VALUES
# =============================================================================
# Each city has base values that reflect its actual environmental profile
CITIES_DATA = [
    # Europe - Generally cleaner, more green space
    {'city': 'Vienna', 'country': 'Austria', 'region': 'Europe', 'lat': 48.2082, 'lon': 16.3738,
     'population': 1900000, 'density': 4326, 'pm25_base': 15, 'green': 48, 'traffic': 6500},
    {'city': 'Zurich', 'country': 'Switzerland', 'region': 'Europe', 'lat': 47.3769, 'lon': 8.5417,
     'population': 434000, 'density': 4700, 'pm25_base': 12, 'green': 45, 'traffic': 5800},
    {'city': 'Copenhagen', 'country': 'Denmark', 'region': 'Europe', 'lat': 55.6761, 'lon': 12.5683,
     'population': 794000, 'density': 7140, 'pm25_base': 11, 'green': 42, 'traffic': 4200},
    {'city': 'Stockholm', 'country': 'Sweden', 'region': 'Europe', 'lat': 59.3293, 'lon': 18.0686,
     'population': 975000, 'density': 5200, 'pm25_base': 10, 'green': 50, 'traffic': 4500},
    {'city': 'Helsinki', 'country': 'Finland', 'region': 'Europe', 'lat': 60.1699, 'lon': 24.9384,
     'population': 656000, 'density': 3050, 'pm25_base': 9, 'green': 52, 'traffic': 4100},
    {'city': 'Amsterdam', 'country': 'Netherlands', 'region': 'Europe', 'lat': 52.3676, 'lon': 4.9041,
     'population': 872000, 'density': 5200, 'pm25_base': 14, 'green': 35, 'traffic': 5200},
    {'city': 'Berlin', 'country': 'Germany', 'region': 'Europe', 'lat': 52.5200, 'lon': 13.4050,
     'population': 3645000, 'density': 4100, 'pm25_base': 16, 'green': 44, 'traffic': 6200},
    {'city': 'Munich', 'country': 'Germany', 'region': 'Europe', 'lat': 48.1351, 'lon': 11.5820,
     'population': 1472000, 'density': 4800, 'pm25_base': 14, 'green': 47, 'traffic': 6800},
    {'city': 'Paris', 'country': 'France', 'region': 'Europe', 'lat': 48.8566, 'lon': 2.3522,
     'population': 2161000, 'density': 20500, 'pm25_base': 18, 'green': 21, 'traffic': 8500},
    {'city': 'London', 'country': 'UK', 'region': 'Europe', 'lat': 51.5074, 'lon': -0.1278,
     'population': 8982000, 'density': 5700, 'pm25_base': 17, 'green': 33, 'traffic': 7800},
    {'city': 'Madrid', 'country': 'Spain', 'region': 'Europe', 'lat': 40.4168, 'lon': -3.7038,
     'population': 3223000, 'density': 5400, 'pm25_base': 15, 'green': 35, 'traffic': 7200},
    {'city': 'Barcelona', 'country': 'Spain', 'region': 'Europe', 'lat': 41.3851, 'lon': 2.1734,
     'population': 1620000, 'density': 16000, 'pm25_base': 16, 'green': 28, 'traffic': 7500},
    {'city': 'Rome', 'country': 'Italy', 'region': 'Europe', 'lat': 41.9028, 'lon': 12.4964,
     'population': 2873000, 'density': 2230, 'pm25_base': 19, 'green': 30, 'traffic': 8200},
    {'city': 'Milan', 'country': 'Italy', 'region': 'Europe', 'lat': 45.4642, 'lon': 9.1900,
     'population': 1396000, 'density': 7700, 'pm25_base': 25, 'green': 18, 'traffic': 9000},
    {'city': 'Prague', 'country': 'Czech Republic', 'region': 'Europe', 'lat': 50.0755, 'lon': 14.4378,
     'population': 1309000, 'density': 2600, 'pm25_base': 18, 'green': 40, 'traffic': 6100},
    {'city': 'Warsaw', 'country': 'Poland', 'region': 'Europe', 'lat': 52.2297, 'lon': 21.0122,
     'population': 1790000, 'density': 3500, 'pm25_base': 22, 'green': 38, 'traffic': 7000},
    {'city': 'Budapest', 'country': 'Hungary', 'region': 'Europe', 'lat': 47.4979, 'lon': 19.0402,
     'population': 1752000, 'density': 3300, 'pm25_base': 20, 'green': 36, 'traffic': 6800},
    {'city': 'Lisbon', 'country': 'Portugal', 'region': 'Europe', 'lat': 38.7223, 'lon': -9.1393,
     'population': 545000, 'density': 6500, 'pm25_base': 12, 'green': 28, 'traffic': 5500},
    {'city': 'Athens', 'country': 'Greece', 'region': 'Europe', 'lat': 37.9838, 'lon': 23.7275,
     'population': 664000, 'density': 17000, 'pm25_base': 21, 'green': 15, 'traffic': 7800},
    {'city': 'Brussels', 'country': 'Belgium', 'region': 'Europe', 'lat': 50.8503, 'lon': 4.3517,
     'population': 185000, 'density': 7400, 'pm25_base': 15, 'green': 32, 'traffic': 6400},

    # Asia - Wide range from very clean to very polluted
    {'city': 'Tokyo', 'country': 'Japan', 'region': 'Asia', 'lat': 35.6762, 'lon': 139.6503,
     'population': 13960000, 'density': 6400, 'pm25_base': 15, 'green': 36, 'traffic': 7200},
    {'city': 'Singapore', 'country': 'Singapore', 'region': 'Asia', 'lat': 1.3521, 'lon': 103.8198,
     'population': 5686000, 'density': 8400, 'pm25_base': 18, 'green': 47, 'traffic': 5000},
    {'city': 'Seoul', 'country': 'South Korea', 'region': 'Asia', 'lat': 37.5665, 'lon': 126.9780,
     'population': 9776000, 'density': 16000, 'pm25_base': 25, 'green': 28, 'traffic': 8500},
    {'city': 'Hong Kong', 'country': 'China', 'region': 'Asia', 'lat': 22.3193, 'lon': 114.1694,
     'population': 7500000, 'density': 6800, 'pm25_base': 22, 'green': 42, 'traffic': 6200},
    {'city': 'Beijing', 'country': 'China', 'region': 'Asia', 'lat': 39.9042, 'lon': 116.4074,
     'population': 21540000, 'density': 1300, 'pm25_base': 55, 'green': 45, 'traffic': 11000},
    {'city': 'Shanghai', 'country': 'China', 'region': 'Asia', 'lat': 31.2304, 'lon': 121.4737,
     'population': 24280000, 'density': 3800, 'pm25_base': 45, 'green': 38, 'traffic': 10500},
    {'city': 'Shenzhen', 'country': 'China', 'region': 'Asia', 'lat': 22.5431, 'lon': 114.0579,
     'population': 12530000, 'density': 6300, 'pm25_base': 32, 'green': 45, 'traffic': 9000},
    {'city': 'Delhi', 'country': 'India', 'region': 'Asia', 'lat': 28.7041, 'lon': 77.1025,
     'population': 32940000, 'density': 11300, 'pm25_base': 98, 'green': 12, 'traffic': 14000},
    {'city': 'Mumbai', 'country': 'India', 'region': 'Asia', 'lat': 19.0760, 'lon': 72.8777,
     'population': 20670000, 'density': 20700, 'pm25_base': 65, 'green': 15, 'traffic': 12500},
    {'city': 'Bangalore', 'country': 'India', 'region': 'Asia', 'lat': 12.9716, 'lon': 77.5946,
     'population': 12340000, 'density': 4400, 'pm25_base': 42, 'green': 22, 'traffic': 9500},
    {'city': 'Bangkok', 'country': 'Thailand', 'region': 'Asia', 'lat': 13.7563, 'lon': 100.5018,
     'population': 10540000, 'density': 5300, 'pm25_base': 35, 'green': 20, 'traffic': 10000},
    {'city': 'Jakarta', 'country': 'Indonesia', 'region': 'Asia', 'lat': -6.2088, 'lon': 106.8456,
     'population': 10560000, 'density': 15900, 'pm25_base': 45, 'green': 10, 'traffic': 11500},
    {'city': 'Hanoi', 'country': 'Vietnam', 'region': 'Asia', 'lat': 21.0285, 'lon': 105.8542,
     'population': 8054000, 'density': 2400, 'pm25_base': 40, 'green': 18, 'traffic': 9800},
    {'city': 'Taipei', 'country': 'Taiwan', 'region': 'Asia', 'lat': 25.0330, 'lon': 121.5654,
     'population': 2646000, 'density': 9700, 'pm25_base': 18, 'green': 35, 'traffic': 7000},
    {'city': 'Osaka', 'country': 'Japan', 'region': 'Asia', 'lat': 34.6937, 'lon': 135.5023,
     'population': 2750000, 'density': 12000, 'pm25_base': 14, 'green': 32, 'traffic': 6800},
    {'city': 'Dubai', 'country': 'UAE', 'region': 'Asia', 'lat': 25.2048, 'lon': 55.2708,
     'population': 3490000, 'density': 860, 'pm25_base': 42, 'green': 8, 'traffic': 8500},
    {'city': 'Tel Aviv', 'country': 'Israel', 'region': 'Asia', 'lat': 32.0853, 'lon': 34.7818,
     'population': 460000, 'density': 8500, 'pm25_base': 22, 'green': 18, 'traffic': 7200},
    {'city': 'Kuala Lumpur', 'country': 'Malaysia', 'region': 'Asia', 'lat': 3.1390, 'lon': 101.6869,
     'population': 1808000, 'density': 7400, 'pm25_base': 28, 'green': 25, 'traffic': 8200},

    # Americas
    {'city': 'New York', 'country': 'USA', 'region': 'Americas', 'lat': 40.7128, 'lon': -74.0060,
     'population': 8336000, 'density': 11000, 'pm25_base': 12, 'green': 27, 'traffic': 7800},
    {'city': 'Los Angeles', 'country': 'USA', 'region': 'Americas', 'lat': 34.0522, 'lon': -118.2437,
     'population': 3980000, 'density': 3300, 'pm25_base': 18, 'green': 15, 'traffic': 9500},
    {'city': 'San Francisco', 'country': 'USA', 'region': 'Americas', 'lat': 37.7749, 'lon': -122.4194,
     'population': 874000, 'density': 7200, 'pm25_base': 10, 'green': 21, 'traffic': 6200},
    {'city': 'Chicago', 'country': 'USA', 'region': 'Americas', 'lat': 41.8781, 'lon': -87.6298,
     'population': 2746000, 'density': 4600, 'pm25_base': 13, 'green': 23, 'traffic': 7200},
    {'city': 'Toronto', 'country': 'Canada', 'region': 'Americas', 'lat': 43.6532, 'lon': -79.3832,
     'population': 2930000, 'density': 4300, 'pm25_base': 11, 'green': 28, 'traffic': 6500},
    {'city': 'Vancouver', 'country': 'Canada', 'region': 'Americas', 'lat': 49.2827, 'lon': -123.1207,
     'population': 675000, 'density': 5500, 'pm25_base': 8, 'green': 35, 'traffic': 5200},
    {'city': 'Montreal', 'country': 'Canada', 'region': 'Americas', 'lat': 45.5017, 'lon': -73.5673,
     'population': 1780000, 'density': 4600, 'pm25_base': 10, 'green': 30, 'traffic': 5800},
    {'city': 'Mexico City', 'country': 'Mexico', 'region': 'Americas', 'lat': 19.4326, 'lon': -99.1332,
     'population': 21670000, 'density': 6000, 'pm25_base': 28, 'green': 18, 'traffic': 9800},
    {'city': 'Sao Paulo', 'country': 'Brazil', 'region': 'Americas', 'lat': -23.5505, 'lon': -46.6333,
     'population': 12330000, 'density': 7400, 'pm25_base': 22, 'green': 20, 'traffic': 9200},
    {'city': 'Buenos Aires', 'country': 'Argentina', 'region': 'Americas', 'lat': -34.6037, 'lon': -58.3816,
     'population': 2891000, 'density': 14500, 'pm25_base': 18, 'green': 22, 'traffic': 7500},
    {'city': 'Santiago', 'country': 'Chile', 'region': 'Americas', 'lat': -33.4489, 'lon': -70.6693,
     'population': 6310000, 'density': 8600, 'pm25_base': 30, 'green': 15, 'traffic': 8000},
    {'city': 'Lima', 'country': 'Peru', 'region': 'Americas', 'lat': -12.0464, 'lon': -77.0428,
     'population': 10880000, 'density': 3600, 'pm25_base': 32, 'green': 12, 'traffic': 8500},
    {'city': 'Bogota', 'country': 'Colombia', 'region': 'Americas', 'lat': 4.7110, 'lon': -74.0721,
     'population': 7410000, 'density': 4500, 'pm25_base': 20, 'green': 25, 'traffic': 7800},

    # Africa
    {'city': 'Cairo', 'country': 'Egypt', 'region': 'Africa', 'lat': 30.0444, 'lon': 31.2357,
     'population': 21320000, 'density': 19400, 'pm25_base': 78, 'green': 5, 'traffic': 12000},
    {'city': 'Lagos', 'country': 'Nigeria', 'region': 'Africa', 'lat': 6.5244, 'lon': 3.3792,
     'population': 15390000, 'density': 6900, 'pm25_base': 68, 'green': 8, 'traffic': 11000},
    {'city': 'Johannesburg', 'country': 'South Africa', 'region': 'Africa', 'lat': -26.2041, 'lon': 28.0473,
     'population': 5635000, 'density': 2700, 'pm25_base': 25, 'green': 24, 'traffic': 7500},
    {'city': 'Cape Town', 'country': 'South Africa', 'region': 'Africa', 'lat': -33.9249, 'lon': 18.4241,
     'population': 4618000, 'density': 1500, 'pm25_base': 15, 'green': 32, 'traffic': 5800},
    {'city': 'Nairobi', 'country': 'Kenya', 'region': 'Africa', 'lat': -1.2921, 'lon': 36.8219,
     'population': 4735000, 'density': 6200, 'pm25_base': 32, 'green': 18, 'traffic': 8000},
    {'city': 'Casablanca', 'country': 'Morocco', 'region': 'Africa', 'lat': 33.5731, 'lon': -7.5898,
     'population': 3360000, 'density': 14200, 'pm25_base': 28, 'green': 12, 'traffic': 7200},
    {'city': 'Accra', 'country': 'Ghana', 'region': 'Africa', 'lat': 5.6037, 'lon': -0.1870,
     'population': 2514000, 'density': 13600, 'pm25_base': 55, 'green': 10, 'traffic': 9500},

    # Oceania
    {'city': 'Sydney', 'country': 'Australia', 'region': 'Oceania', 'lat': -33.8688, 'lon': 151.2093,
     'population': 5312000, 'density': 430, 'pm25_base': 10, 'green': 46, 'traffic': 5500},
    {'city': 'Melbourne', 'country': 'Australia', 'region': 'Oceania', 'lat': -37.8136, 'lon': 144.9631,
     'population': 5078000, 'density': 510, 'pm25_base': 9, 'green': 48, 'traffic': 5200},
    {'city': 'Brisbane', 'country': 'Australia', 'region': 'Oceania', 'lat': -27.4698, 'lon': 153.0251,
     'population': 2514000, 'density': 370, 'pm25_base': 8, 'green': 52, 'traffic': 4800},
    {'city': 'Auckland', 'country': 'New Zealand', 'region': 'Oceania', 'lat': -36.8485, 'lon': 174.7633,
     'population': 1571000, 'density': 2400, 'pm25_base': 7, 'green': 55, 'traffic': 4500},
    {'city': 'Perth', 'country': 'Australia', 'region': 'Oceania', 'lat': -31.9505, 'lon': 115.8605,
     'population': 2140000, 'density': 320, 'pm25_base': 8, 'green': 45, 'traffic': 4600},
]


def generate_environmental_indicators(base_pm25, green_space, traffic, density):
    """
    Generate correlated environmental indicators based on base PM2.5 value.
    Creates realistic correlations between variables.
    """
    # PM10 is typically 1.5-2x PM2.5
    pm10 = base_pm25 * np.random.uniform(1.4, 1.8)

    # NO2 correlates with traffic and density
    no2 = 10 + (traffic / 1000) * 2 + (density / 1000) * 0.5 + np.random.uniform(-5, 5)

    # O3 inversely correlates with NO2 (complex chemistry)
    o3 = 60 - no2 * 0.3 + np.random.uniform(10, 30)

    # Air Quality Index (weighted combination)
    aqi = base_pm25 * 1.5 + pm10 * 0.3 + no2 * 0.5 + max(0, o3 - 50) * 0.2

    return {
        'pm10': max(10, min(250, pm10)),
        'no2': max(5, min(80, no2)),
        'o3': max(20, min(120, o3)),
        'air_quality_index': max(0, min(500, aqi))
    }


def add_seasonal_variation(base_value, month, city_lat):
    """
    Add seasonal variation to environmental values.
    Northern hemisphere: worse in winter
    Southern hemisphere: opposite pattern
    """
    # Seasonal factor (-1 to 1)
    if city_lat > 0:  # Northern hemisphere
        seasonal = np.cos((month - 1) * np.pi / 6)  # Peak in winter
    else:  # Southern hemisphere
        seasonal = np.cos((month - 7) * np.pi / 6)  # Peak in their winter

    # Seasonal amplitude (larger for more polluted cities)
    amplitude = base_value * 0.15

    return base_value + seasonal * amplitude


def add_trend(base_value, year, city_region):
    """
    Add year-over-year trend.
    Most cities improving slightly, some (developing) improving faster.
    """
    year_offset = year - 2019

    # Different improvement rates by region
    trend_rates = {
        'Europe': -0.02,      # 2% improvement per year
        'Americas': -0.015,   # 1.5% improvement per year
        'Asia': -0.025,       # 2.5% improvement per year (faster in China)
        'Oceania': -0.01,     # Already clean, slow improvement
        'Africa': 0.01,       # Still increasing due to development
    }

    trend_rate = trend_rates.get(city_region, -0.01)
    return base_value * (1 + trend_rate * year_offset)


def generate_time_series_data():
    """
    Generate complete time series data for all cities (2019-2024, monthly).
    Returns a pandas DataFrame.
    """
    all_data = []

    for city_info in CITIES_DATA:
        # Generate monthly data for 2019-2024
        for year in range(2019, 2025):
            for month in range(1, 13):
                # Skip future months in 2024
                if year == 2024 and month > 10:
                    continue

                # Base PM2.5 with trend
                base_pm25 = add_trend(city_info['pm25_base'], year, city_info['region'])

                # Add seasonal variation
                pm25 = add_seasonal_variation(base_pm25, month, city_info['lat'])

                # Add random noise
                pm25 = pm25 * np.random.uniform(0.9, 1.1)
                pm25 = max(3, min(200, pm25))

                # Generate other indicators
                env_indicators = generate_environmental_indicators(
                    pm25, city_info['green'], city_info['traffic'], city_info['density']
                )

                # Create record
                record = {
                    'city': city_info['city'],
                    'country': city_info['country'],
                    'region': city_info['region'],
                    'lat': city_info['lat'],
                    'lon': city_info['lon'],
                    'population': city_info['population'],
                    'population_density': city_info['density'],
                    'green_space_pct': city_info['green'] + np.random.uniform(-2, 2),
                    'traffic_intensity': city_info['traffic'] + np.random.uniform(-500, 500),
                    'pm25': round(pm25, 1),
                    'pm10': round(env_indicators['pm10'], 1),
                    'no2': round(env_indicators['no2'], 1),
                    'o3': round(env_indicators['o3'], 1),
                    'air_quality_index': round(env_indicators['air_quality_index'], 0),
                    'year': year,
                    'month': month,
                    'date': f"{year}-{month:02d}-01"
                }

                all_data.append(record)

    df = pd.DataFrame(all_data)

    # Ensure consistent green space and traffic within each city
    for city in df['city'].unique():
        mask = df['city'] == city
        df.loc[mask, 'green_space_pct'] = df.loc[mask, 'green_space_pct'].mean()
        df.loc[mask, 'traffic_intensity'] = df.loc[mask, 'traffic_intensity'].mean()

    # Round values
    df['green_space_pct'] = df['green_space_pct'].round(1)
    df['traffic_intensity'] = df['traffic_intensity'].round(0).astype(int)

    return df


def generate_city_summary():
    """
    Generate city-level summary data (averaged across all time).
    """
    df = generate_time_series_data()

    # Aggregate to city level
    summary = df.groupby(['city', 'country', 'region', 'lat', 'lon',
                          'population', 'population_density']).agg({
        'pm25': 'mean',
        'pm10': 'mean',
        'no2': 'mean',
        'o3': 'mean',
        'air_quality_index': 'mean',
        'green_space_pct': 'first',
        'traffic_intensity': 'first',
    }).reset_index()

    # Round values
    summary['pm25'] = summary['pm25'].round(1)
    summary['pm10'] = summary['pm10'].round(1)
    summary['no2'] = summary['no2'].round(1)
    summary['o3'] = summary['o3'].round(1)
    summary['air_quality_index'] = summary['air_quality_index'].round(0).astype(int)

    return summary


if __name__ == '__main__':
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating urban environmental quality data...")

    # Generate and save time series data
    df_timeseries = generate_time_series_data()
    timeseries_path = os.path.join(script_dir, 'cities_timeseries.csv')
    df_timeseries.to_csv(timeseries_path, index=False)
    print(f"Time series data saved: {len(df_timeseries)} records for {df_timeseries['city'].nunique()} cities")

    # Generate and save city summary data
    df_summary = generate_city_summary()
    summary_path = os.path.join(script_dir, 'cities_summary.csv')
    df_summary.to_csv(summary_path, index=False)
    print(f"City summary data saved: {len(df_summary)} cities")

    # Display sample data
    print("\nSample of generated data:")
    print(df_summary[df_summary['city'].isin(['Vienna', 'Tokyo', 'Delhi', 'Sydney', 'New York'])].to_string())

    print("\nData columns:", list(df_timeseries.columns))
    print(f"\nDate range: {df_timeseries['date'].min()} to {df_timeseries['date'].max()}")
    print(f"Regions: {df_timeseries['region'].unique().tolist()}")
