"""
OpenAQ Data Fetcher for Urban Environmental Quality Dashboard

Fetches air quality data (PM2.5, PM10, NO2, O3) from OpenAQ API v3
for the target cities defined in city_definitions.py.

Usage:
    python fetch_openaq.py

Requires:
    - OPENAQ_API_KEY environment variable set
    - Or create a .env file with OPENAQ_API_KEY=your_key
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import pandas as pd
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from city_definitions import CITIES, POLLUTANTS, DATE_RANGE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("fetch_openaq.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "https://api.openaq.org/v3"
API_KEY = os.getenv("OPENAQ_API_KEY")
RATE_LIMIT_DELAY = 0.5  # seconds between requests to avoid rate limiting
MAX_RETRIES = 3
OUTPUT_DIR = Path(__file__).parent / "raw" / "openaq"


class OpenAQFetcher:
    """Handles all OpenAQ API interactions."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError(
                "OpenAQ API key is required. Set OPENAQ_API_KEY environment variable."
            )
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def _request(
        self, endpoint: str, params: dict = None, retries: int = MAX_RETRIES
    ) -> dict:
        """Make a request to the OpenAQ API with retry logic."""
        url = f"{BASE_URL}/{endpoint}"

        for attempt in range(retries):
            try:
                time.sleep(RATE_LIMIT_DELAY)
                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 60 * (attempt + 1)
                    logger.warning(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif response.status_code == 404:
                    logger.debug(f"Not found: {url}")
                    return {"results": []}
                else:
                    logger.error(
                        f"API error {response.status_code}: {response.text[:200]}"
                    )

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

        return {"results": []}

    def find_locations_near_city(
        self, lat: float, lon: float, radius_km: int = 25, limit: int = 100
    ) -> list:
        """Find OpenAQ monitoring locations near a city center."""
        # Convert km to meters for API (max 25000m = 25km)
        radius_m = min(radius_km * 1000, 25000)

        params = {
            "coordinates": f"{lat},{lon}",
            "radius": radius_m,
            "limit": limit,
        }

        data = self._request("locations", params)
        return data.get("results", [])

    def get_location_sensors(self, location_id: int) -> list:
        """Get sensors for a specific location."""
        data = self._request(f"locations/{location_id}/sensors", {"limit": 100})
        return data.get("results", [])

    def get_sensor_daily_data(
        self,
        sensor_id: int,
        date_from: str,
        date_to: str,
        limit: int = 1000,
    ) -> list:
        """Get daily aggregated data for a sensor with pagination."""
        all_results = []
        page = 1

        while True:
            params = {
                "date_from": date_from,
                "date_to": date_to,
                "limit": min(limit, 1000),  # API max is 1000
                "page": page,
            }
            data = self._request(f"sensors/{sensor_id}/days", params)
            results = data.get("results", [])

            if not results:
                break

            all_results.extend(results)

            # Check if we got less than limit (no more pages)
            if len(results) < min(limit, 1000):
                break

            page += 1

            # Safety limit to avoid infinite loops
            if page > 10:
                break

        return all_results

    def find_best_stations_for_city(
        self, city_info: dict, target_pollutants: list = None
    ) -> dict:
        """
        Find the best monitoring stations for a city.
        Prefers reference-grade government stations with multiple pollutants.
        """
        if target_pollutants is None:
            target_pollutants = ["pm25", "pm10", "no2", "o3"]

        locations = self.find_locations_near_city(
            city_info["lat"],
            city_info["lon"],
            city_info.get("search_radius_km", 25),
        )

        if not locations:
            logger.warning(f"No locations found for {city_info['city']}")
            return {}

        # Score and rank locations
        scored_locations = []
        for loc in locations:
            score = 0
            available_params = set()

            # Check what parameters this location has
            for sensor in loc.get("sensors", []):
                param = sensor.get("parameter", {})
                param_name = param.get("name", "").lower()
                if param_name in target_pollutants:
                    available_params.add(param_name)
                    score += 10

            # Prefer reference-grade monitors
            if loc.get("isMonitor"):
                score += 20

            # Prefer government/research entities
            entity = loc.get("entity", {}).get("type", "").lower()
            if entity in ["government", "research"]:
                score += 15

            # Prefer locations with more data
            measurements = loc.get("measurements", 0)
            if measurements > 10000:
                score += 10
            elif measurements > 1000:
                score += 5

            if available_params:
                scored_locations.append(
                    {
                        "location": loc,
                        "score": score,
                        "params": available_params,
                    }
                )

        if not scored_locations:
            logger.warning(f"No suitable stations found for {city_info['city']}")
            return {}

        # Sort by score
        scored_locations.sort(key=lambda x: x["score"], reverse=True)

        # Select best stations - try to cover all pollutants
        selected = {}
        covered_params = set()

        for item in scored_locations:
            loc = item["location"]
            params = item["params"]

            # Add if it covers new pollutants or is high quality
            new_params = params - covered_params
            if new_params or (item["score"] > 30 and len(selected) < 3):
                loc_id = loc["id"]
                selected[loc_id] = {
                    "location_id": loc_id,
                    "name": loc.get("name", "Unknown"),
                    "lat": loc.get("coordinates", {}).get("latitude"),
                    "lon": loc.get("coordinates", {}).get("longitude"),
                    "params": list(params),
                    "score": item["score"],
                    "entity": loc.get("entity", {}).get("type"),
                    "is_monitor": loc.get("isMonitor"),
                }
                covered_params.update(params)

            # Stop if we have all pollutants covered
            if covered_params >= set(target_pollutants):
                break

        logger.info(
            f"{city_info['city']}: Found {len(selected)} stations covering {covered_params}"
        )
        return selected


def fetch_city_data(fetcher: OpenAQFetcher, city_info: dict) -> pd.DataFrame:
    """Fetch all air quality data for a single city."""
    city_name = city_info["city"]
    logger.info(f"Fetching data for {city_name}...")

    # Find best stations
    stations = fetcher.find_best_stations_for_city(city_info)
    if not stations:
        return pd.DataFrame()

    all_data = []
    date_from = DATE_RANGE["start"]
    date_to = DATE_RANGE["end"]

    for loc_id, station_info in stations.items():
        logger.info(f"  Station: {station_info['name']} (ID: {loc_id})")

        # Get sensors for this location
        sensors = fetcher.get_location_sensors(loc_id)

        for sensor in sensors:
            sensor_id = sensor.get("id")
            param = sensor.get("parameter", {})
            param_name = param.get("name", "").lower()

            if param_name not in ["pm25", "pm10", "no2", "o3"]:
                continue

            logger.info(f"    Fetching {param_name} from sensor {sensor_id}...")

            # Fetch daily data
            daily_data = fetcher.get_sensor_daily_data(
                sensor_id, date_from, date_to, limit=1500
            )

            for record in daily_data:
                # Extract date from various possible formats
                date_info = record.get("period", {})
                if isinstance(date_info, dict):
                    date_str = date_info.get("datetimeFrom", {})
                    if isinstance(date_str, dict):
                        date_str = date_str.get("utc", "")
                    elif isinstance(date_str, str):
                        pass
                    else:
                        date_str = ""
                else:
                    date_str = str(date_info) if date_info else ""

                # Parse the date
                try:
                    if date_str:
                        dt = pd.to_datetime(date_str).date()
                    else:
                        continue
                except Exception:
                    continue

                # Get the value (prefer average)
                value = record.get("value", {})
                if isinstance(value, dict):
                    avg_value = value.get("avg") or value.get("mean")
                else:
                    avg_value = value

                if avg_value is None:
                    continue

                all_data.append(
                    {
                        "city": city_name,
                        "country": city_info["country"],
                        "country_code": city_info["country_code"],
                        "region": city_info["region"],
                        "station_id": loc_id,
                        "station_name": station_info["name"],
                        "sensor_id": sensor_id,
                        "parameter": param_name,
                        "value": float(avg_value),
                        "date": dt,
                        "lat": station_info["lat"],
                        "lon": station_info["lon"],
                    }
                )

    if not all_data:
        logger.warning(f"No data retrieved for {city_name}")
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    logger.info(f"  Retrieved {len(df)} daily records for {city_name}")
    return df


def aggregate_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily station data to monthly city-level averages."""
    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # First aggregate across stations (median to reduce outlier impact)
    # Group by city + parameter + time, take median of values and mean of coordinates
    station_monthly = (
        df.groupby(["city", "country", "country_code", "region", "parameter", "year", "month"])
        .agg({"value": "median", "lat": "mean", "lon": "mean"})
        .reset_index()
    )

    # Pivot to get one row per city-month with all pollutants as columns
    # Don't include lat/lon in pivot index to avoid duplicates
    pivoted = station_monthly.pivot_table(
        index=["city", "country", "country_code", "region", "year", "month"],
        columns="parameter",
        values="value",
        aggfunc="mean",
    ).reset_index()

    # Flatten column names
    pivoted.columns = [
        col if not isinstance(col, tuple) else col[0] for col in pivoted.columns
    ]

    # Add lat/lon back (use mean coordinates per city)
    city_coords = df.groupby("city").agg({"lat": "mean", "lon": "mean"}).reset_index()
    pivoted = pivoted.merge(city_coords, on="city", how="left")

    # Add date column
    pivoted["date"] = pd.to_datetime(
        pivoted["year"].astype(str) + "-" + pivoted["month"].astype(str).str.zfill(2) + "-01"
    )

    return pivoted


def save_progress(df: pd.DataFrame, city_name: str):
    """Save intermediate results for a city."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = city_name.lower().replace(" ", "_")
    filepath = OUTPUT_DIR / f"{safe_name}_daily.csv"
    df.to_csv(filepath, index=False)
    logger.info(f"Saved {len(df)} records to {filepath}")


def main():
    """Main entry point for data fetching."""
    if not API_KEY:
        logger.error("OPENAQ_API_KEY not found in environment variables!")
        logger.info("Please set it: export OPENAQ_API_KEY=your_api_key")
        logger.info("Or create a .env file with OPENAQ_API_KEY=your_key")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("OpenAQ Data Fetcher - Urban Environmental Quality Dashboard")
    logger.info("=" * 60)
    logger.info(f"Target cities: {len(CITIES)}")
    logger.info(f"Date range: {DATE_RANGE['start']} to {DATE_RANGE['end']}")

    fetcher = OpenAQFetcher(API_KEY)
    all_city_data = []

    for i, city_info in enumerate(CITIES, 1):
        logger.info(f"\n[{i}/{len(CITIES)}] Processing {city_info['city']}...")

        try:
            df = fetch_city_data(fetcher, city_info)
            if not df.empty:
                save_progress(df, city_info["city"])
                all_city_data.append(df)
        except Exception as e:
            logger.error(f"Error processing {city_info['city']}: {e}")
            continue

    if not all_city_data:
        logger.error("No data collected!")
        sys.exit(1)

    # Combine all data
    combined = pd.concat(all_city_data, ignore_index=True)
    logger.info(f"\nTotal daily records: {len(combined)}")

    # Save combined daily data
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_DIR / "all_cities_daily.csv", index=False)

    # Aggregate to monthly
    monthly = aggregate_to_monthly(combined)
    monthly.to_csv(OUTPUT_DIR / "all_cities_monthly.csv", index=False)
    logger.info(f"Monthly records: {len(monthly)}")

    # Summary statistics
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Cities with data: {combined['city'].nunique()}")
    logger.info(f"Date range: {combined['date'].min()} to {combined['date'].max()}")
    logger.info("\nPollutant coverage:")
    for param in ["pm25", "pm10", "no2", "o3"]:
        count = combined[combined["parameter"] == param]["city"].nunique()
        logger.info(f"  {param}: {count} cities")

    # List cities without data
    cities_with_data = set(combined["city"].unique())
    all_cities = set(c["city"] for c in CITIES)
    missing = all_cities - cities_with_data
    if missing:
        logger.warning(f"\nCities without data: {missing}")

    logger.info("\nData fetching complete!")
    logger.info(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
