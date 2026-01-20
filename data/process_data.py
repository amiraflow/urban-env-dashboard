"""
Data Processing Pipeline for Urban Environmental Quality Dashboard

Combines data from all sources:
- OpenAQ air quality data (PM2.5, PM10, NO2, O3)
- Supplementary data (population, green space, traffic)

Produces final CSV files for the dashboard:
- cities_timeseries.csv (monthly data)
- cities_summary.csv (city averages)

Then runs clustering to produce:
- cities_clustered.csv (with cluster assignments)
"""

import os
import sys
import logging
from pathlib import Path

import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR


def compute_aqi(pm25: float, pm10: float = None, no2: float = None, o3: float = None) -> float:
    """
    Compute a simplified Air Quality Index based on US EPA AQI formula.
    Uses PM2.5 as the primary indicator.

    AQI Breakpoints for PM2.5 (24-hour, µg/m³):
    Good: 0-12 -> AQI 0-50
    Moderate: 12.1-35.4 -> AQI 51-100
    Unhealthy for Sensitive: 35.5-55.4 -> AQI 101-150
    Unhealthy: 55.5-150.4 -> AQI 151-200
    Very Unhealthy: 150.5-250.4 -> AQI 201-300
    Hazardous: 250.5+ -> AQI 301-500
    """
    if pd.isna(pm25):
        return np.nan

    # PM2.5 AQI calculation
    breakpoints = [
        (0, 12, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]

    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return round(aqi, 0)

    # Above highest breakpoint
    if pm25 > 500.4:
        return 500

    return np.nan


def load_openaq_data() -> pd.DataFrame:
    """Load OpenAQ monthly air quality data."""
    filepath = RAW_DIR / "openaq" / "all_cities_monthly.csv"

    if not filepath.exists():
        logger.warning(f"OpenAQ data not found at {filepath}")
        logger.info("Run fetch_openaq.py first to download air quality data")
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    logger.info(f"Loaded OpenAQ data: {len(df)} monthly records for {df['city'].nunique()} cities")

    return df


def load_supplementary_data() -> pd.DataFrame:
    """Load supplementary city data (population, green space, traffic)."""
    filepath = RAW_DIR / "supplementary" / "city_supplementary.csv"

    if not filepath.exists():
        logger.warning(f"Supplementary data not found at {filepath}")
        logger.info("Run fetch_supplementary.py first to compile supplementary data")
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    logger.info(f"Loaded supplementary data for {len(df)} cities")

    return df


def merge_data(aq_df: pd.DataFrame, supp_df: pd.DataFrame) -> pd.DataFrame:
    """Merge air quality and supplementary data."""
    if aq_df.empty:
        logger.error("No air quality data to merge")
        return pd.DataFrame()

    if supp_df.empty:
        logger.warning("No supplementary data - using air quality data only")
        return aq_df

    # Columns to take from supplementary data
    supp_cols = [
        "city",
        "population",
        "population_density",
        "green_space_pct",
        "traffic_congestion_pct",
    ]

    # Ensure columns exist
    supp_cols = [c for c in supp_cols if c in supp_df.columns]

    # Merge on city
    merged = pd.merge(
        aq_df,
        supp_df[supp_cols],
        on="city",
        how="left",
    )

    logger.info(f"Merged data: {len(merged)} records")

    return merged


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values in the dataset."""
    # For air quality, interpolate within each city's time series
    for city in df["city"].unique():
        mask = df["city"] == city
        for col in ["pm25", "pm10", "no2", "o3"]:
            if col in df.columns:
                df.loc[mask, col] = df.loc[mask, col].interpolate(method="linear", limit=2)

    # Log missing data summary
    logger.info("Missing values after interpolation:")
    for col in ["pm25", "pm10", "no2", "o3", "population_density", "green_space_pct"]:
        if col in df.columns:
            missing = df[col].isna().sum()
            pct = (missing / len(df)) * 100
            logger.info(f"  {col}: {missing} ({pct:.1f}%)")

    return df


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived metrics like AQI."""
    # Air Quality Index
    df["air_quality_index"] = df.apply(
        lambda row: compute_aqi(
            row.get("pm25"),
            row.get("pm10"),
            row.get("no2"),
            row.get("o3"),
        ),
        axis=1,
    )

    # Rename traffic_congestion_pct to traffic_intensity for dashboard compatibility
    if "traffic_congestion_pct" in df.columns:
        # Scale congestion (0-100%) to a traffic intensity proxy (0-15000 range)
        # Using linear scaling where 50% congestion ~ 10000 traffic
        df["traffic_intensity"] = df["traffic_congestion_pct"] * 200
        df["traffic_intensity"] = df["traffic_intensity"].fillna(df["traffic_intensity"].median())

    return df


def generate_timeseries_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Generate the cities_timeseries.csv file."""
    # Required columns for dashboard
    required_cols = [
        "city",
        "country",
        "region",
        "lat",
        "lon",
        "population",
        "population_density",
        "green_space_pct",
        "traffic_intensity",
        "pm25",
        "pm10",
        "no2",
        "o3",
        "air_quality_index",
        "year",
        "month",
        "date",
    ]

    # Ensure all required columns exist
    for col in required_cols:
        if col not in df.columns:
            logger.warning(f"Missing column: {col}")
            df[col] = np.nan

    # Select and order columns
    output_df = df[required_cols].copy()

    # Round numeric columns
    numeric_cols = ["pm25", "pm10", "no2", "o3", "air_quality_index", "green_space_pct"]
    for col in numeric_cols:
        if col in output_df.columns:
            output_df[col] = output_df[col].round(1)

    output_df["population_density"] = output_df["population_density"].round(0)
    output_df["traffic_intensity"] = output_df["traffic_intensity"].round(0).astype("Int64")

    # Sort by city and date
    output_df = output_df.sort_values(["city", "date"]).reset_index(drop=True)

    # Save
    output_path = OUTPUT_DIR / "cities_timeseries.csv"
    output_df.to_csv(output_path, index=False)
    logger.info(f"Saved timeseries data to {output_path}")
    logger.info(f"  {len(output_df)} records for {output_df['city'].nunique()} cities")

    return output_df


def generate_summary_csv(ts_df: pd.DataFrame) -> pd.DataFrame:
    """Generate the cities_summary.csv file (city-level averages)."""
    # Aggregate time series to city level
    agg_cols = {
        "pm25": "mean",
        "pm10": "mean",
        "no2": "mean",
        "o3": "mean",
        "air_quality_index": "mean",
    }

    # Group by city metadata
    groupby_cols = [
        "city",
        "country",
        "region",
        "lat",
        "lon",
        "population",
        "population_density",
        "green_space_pct",
        "traffic_intensity",
    ]

    # Ensure columns exist
    groupby_cols = [c for c in groupby_cols if c in ts_df.columns]
    agg_cols = {k: v for k, v in agg_cols.items() if k in ts_df.columns}

    summary = ts_df.groupby(groupby_cols, dropna=False).agg(agg_cols).reset_index()

    # Round values
    for col in ["pm25", "pm10", "no2", "o3"]:
        if col in summary.columns:
            summary[col] = summary[col].round(1)
    if "air_quality_index" in summary.columns:
        summary["air_quality_index"] = summary["air_quality_index"].round(0).astype("Int64")

    # Fill remaining NaN values with column medians (required for clustering)
    numeric_cols = ["pm25", "pm10", "no2", "o3", "air_quality_index",
                    "population_density", "green_space_pct", "traffic_intensity"]
    for col in numeric_cols:
        if col in summary.columns:
            median_val = summary[col].median()
            if pd.notna(median_val):
                na_count = summary[col].isna().sum()
                if na_count > 0:
                    # Convert Int64 columns to float before filling to avoid type errors
                    if summary[col].dtype == "Int64":
                        summary[col] = summary[col].astype(float)
                        median_val = int(round(median_val))
                    logger.info(f"  Filling {na_count} NaN values in {col} with median ({median_val})")
                    summary[col] = summary[col].fillna(median_val)

    # Log final data quality
    logger.info("Final data quality check:")
    for col in numeric_cols:
        if col in summary.columns:
            na_count = summary[col].isna().sum()
            if na_count > 0:
                logger.warning(f"  {col}: still has {na_count} NaN values")
            else:
                logger.info(f"  {col}: OK (no NaN)")

    # Save
    output_path = OUTPUT_DIR / "cities_summary.csv"
    summary.to_csv(output_path, index=False)
    logger.info(f"Saved summary data to {output_path}")
    logger.info(f"  {len(summary)} cities")

    return summary


def run_clustering(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Run K-means clustering on city summary data."""
    # Import here to avoid circular imports
    sys.path.insert(0, str(DATA_DIR.parent / "models"))

    try:
        from clustering import perform_clustering, save_clustered_data

        # perform_clustering returns a tuple: (df_clustered, kmeans, pca, cluster_info, feature_cols)
        result = perform_clustering(summary_df)
        clustered_df = result[0]  # First element is the clustered DataFrame

        # Save the clustered data to cities_clustered.csv
        save_clustered_data(clustered_df)

        logger.info("Clustering completed successfully")
        return clustered_df
    except ImportError as e:
        logger.warning(f"Could not import clustering module: {e}")
        logger.info("Skipping clustering - run models/clustering.py separately")
        return summary_df
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return summary_df


def main():
    """Main data processing pipeline."""
    logger.info("=" * 60)
    logger.info("Data Processing Pipeline")
    logger.info("=" * 60)

    # Step 1: Load data
    logger.info("\n[1/6] Loading data sources...")
    aq_df = load_openaq_data()
    supp_df = load_supplementary_data()

    if aq_df.empty:
        logger.error("Cannot proceed without air quality data")
        logger.info("\nTo get started:")
        logger.info("  1. Set OPENAQ_API_KEY environment variable")
        logger.info("  2. Run: python fetch_openaq.py")
        logger.info("  3. Run: python fetch_supplementary.py")
        logger.info("  4. Run: python process_data.py")
        return

    # Step 2: Merge data
    logger.info("\n[2/6] Merging data sources...")
    merged_df = merge_data(aq_df, supp_df)

    # Step 3: Fill missing values
    logger.info("\n[3/6] Handling missing values...")
    filled_df = fill_missing_values(merged_df)

    # Step 4: Compute derived metrics
    logger.info("\n[4/6] Computing derived metrics...")
    processed_df = compute_derived_metrics(filled_df)

    # Step 5: Generate output files
    logger.info("\n[5/6] Generating output files...")
    ts_df = generate_timeseries_csv(processed_df)
    summary_df = generate_summary_csv(ts_df)

    # Step 6: Run clustering
    logger.info("\n[6/6] Running clustering...")
    clustered_df = run_clustering(summary_df)

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Cities: {ts_df['city'].nunique()}")
    logger.info(f"Time range: {ts_df['date'].min()} to {ts_df['date'].max()}")
    logger.info(f"Regions: {ts_df['region'].unique().tolist()}")

    logger.info("\nOutput files:")
    logger.info(f"  - {OUTPUT_DIR / 'cities_timeseries.csv'}")
    logger.info(f"  - {OUTPUT_DIR / 'cities_summary.csv'}")
    logger.info(f"  - {OUTPUT_DIR / 'cities_clustered.csv'}")

    # Data quality summary
    logger.info("\nPollutant coverage (cities with >50% data):")
    for col in ["pm25", "pm10", "no2", "o3"]:
        if col in ts_df.columns:
            cities_with_data = (
                ts_df.groupby("city")[col]
                .apply(lambda x: x.notna().mean() > 0.5)
                .sum()
            )
            logger.info(f"  {col}: {cities_with_data} cities")


if __name__ == "__main__":
    main()
