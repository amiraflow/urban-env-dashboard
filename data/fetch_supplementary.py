"""
Supplementary Data Fetcher for Urban Environmental Quality Dashboard

Fetches and compiles supplementary data from various sources:
- Population data (UN World Urbanization Prospects / Eurostat)
- Green space data (OECD / research papers)
- Traffic data (TomTom Traffic Index)
- Country-level PM2.5 (Our World in Data)

Some data is downloaded as CSV, some is compiled from known statistics.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

import requests
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from city_definitions import CITIES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "raw" / "supplementary"


# =============================================================================
# CITY SUPPLEMENTARY DATA
# Compiled from official sources: UN, Eurostat, OECD, TomTom, city reports
# =============================================================================

# Population and density data (UN World Urbanization Prospects 2018 + Eurostat 2020)
# Sources:
# - UN: https://population.un.org/wup/
# - Eurostat: https://ec.europa.eu/eurostat/web/cities/data/database
POPULATION_DATA = {
    # Europe
    "Vienna": {"population": 1911191, "area_km2": 414.6, "year": 2020},
    "Berlin": {"population": 3644826, "area_km2": 891.7, "year": 2020},
    "Paris": {"population": 2161000, "area_km2": 105.4, "year": 2020},
    "London": {"population": 8982000, "area_km2": 1572, "year": 2020},
    "Madrid": {"population": 3223334, "area_km2": 604.3, "year": 2020},
    "Rome": {"population": 2873000, "area_km2": 1285, "year": 2020},
    "Amsterdam": {"population": 872680, "area_km2": 219.3, "year": 2020},
    "Stockholm": {"population": 975904, "area_km2": 188, "year": 2020},
    "Copenhagen": {"population": 794128, "area_km2": 86.2, "year": 2020},
    "Prague": {"population": 1335084, "area_km2": 496, "year": 2020},
    "Warsaw": {"population": 1790658, "area_km2": 517.2, "year": 2020},
    "Budapest": {"population": 1752286, "area_km2": 525.2, "year": 2020},
    "Brussels": {"population": 1218255, "area_km2": 162.4, "year": 2020},
    "Zurich": {"population": 421878, "area_km2": 87.9, "year": 2020},
    "Helsinki": {"population": 656920, "area_km2": 214.3, "year": 2020},
    "Belgrade": {"population": 1397939, "area_km2": 359.9, "year": 2020},
    "Sarajevo": {"population": 275524, "area_km2": 141.5, "year": 2020},
    # Asia
    "Tokyo": {"population": 13960000, "area_km2": 2194, "year": 2020},
    "Seoul": {"population": 9776000, "area_km2": 605.2, "year": 2020},
    "Singapore": {"population": 5686000, "area_km2": 728.6, "year": 2020},
    "Bangkok": {"population": 10539000, "area_km2": 1568.7, "year": 2020},
    "Delhi": {"population": 32941000, "area_km2": 1484, "year": 2020},
    "Mumbai": {"population": 20668000, "area_km2": 603, "year": 2020},
    "Beijing": {"population": 21540000, "area_km2": 16411, "year": 2020},
    "Shanghai": {"population": 28516000, "area_km2": 6341, "year": 2020},
    # Americas
    "New York": {"population": 8336817, "area_km2": 783.8, "year": 2020},
    "Los Angeles": {"population": 3979576, "area_km2": 1213.9, "year": 2020},
    "Toronto": {"population": 2930000, "area_km2": 630.2, "year": 2020},
    "Mexico City": {"population": 21672000, "area_km2": 1485, "year": 2020},
    "Sao Paulo": {"population": 12325232, "area_km2": 1521.1, "year": 2020},
    "Buenos Aires": {"population": 2891082, "area_km2": 203, "year": 2020},
    # Africa
    "Cairo": {"population": 21323000, "area_km2": 1100, "year": 2020},
    "Johannesburg": {"population": 5635127, "area_km2": 1645, "year": 2020},
    "Cape Town": {"population": 4618000, "area_km2": 2461, "year": 2020},
    # Oceania
    "Sydney": {"population": 5312163, "area_km2": 12368, "year": 2020},
    "Melbourne": {"population": 5078193, "area_km2": 9993, "year": 2020},
    "Auckland": {"population": 1571718, "area_km2": 559.2, "year": 2020},
}

# Green space percentage data
# Sources:
# - European Urban Atlas (Copernicus Land Monitoring Service)
# - OECD Metropolitan Areas Database
# - Academic papers and city sustainability reports
# - WHO Urban Health Observatory
GREEN_SPACE_DATA = {
    # Europe - from Copernicus Urban Atlas / EEA reports
    "Vienna": {"green_space_pct": 49.7, "source": "Vienna City Administration 2020"},
    "Berlin": {"green_space_pct": 44.0, "source": "Berlin Environmental Atlas 2020"},
    "Paris": {"green_space_pct": 21.0, "source": "European Urban Atlas 2018"},
    "London": {"green_space_pct": 33.0, "source": "London Environment Strategy 2018"},
    "Madrid": {"green_space_pct": 35.0, "source": "European Urban Atlas 2018"},
    "Rome": {"green_space_pct": 30.0, "source": "European Urban Atlas 2018"},
    "Amsterdam": {"green_space_pct": 30.0, "source": "European Urban Atlas 2018"},
    "Stockholm": {"green_space_pct": 40.0, "source": "Stockholm Environment 2019"},
    "Copenhagen": {"green_space_pct": 35.0, "source": "Copenhagen Green Accounts 2019"},
    "Prague": {"green_space_pct": 40.0, "source": "European Urban Atlas 2018"},
    "Warsaw": {"green_space_pct": 38.0, "source": "European Urban Atlas 2018"},
    "Budapest": {"green_space_pct": 36.0, "source": "European Urban Atlas 2018"},
    "Brussels": {"green_space_pct": 32.0, "source": "European Urban Atlas 2018"},
    "Zurich": {"green_space_pct": 45.0, "source": "Zurich Statistics 2020"},
    "Helsinki": {"green_space_pct": 40.0, "source": "Helsinki City Plan 2019"},
    "Belgrade": {"green_space_pct": 25.0, "source": "Belgrade Urban Planning 2019"},
    "Sarajevo": {"green_space_pct": 22.0, "source": "Sarajevo Canton Environment 2018"},
    # Asia - from OECD / city reports / academic studies
    "Tokyo": {"green_space_pct": 7.5, "source": "Tokyo Metropolitan Gov 2019"},
    "Seoul": {"green_space_pct": 27.0, "source": "Seoul Statistics 2020"},
    "Singapore": {"green_space_pct": 47.0, "source": "Singapore Green Plan 2019"},
    "Bangkok": {"green_space_pct": 11.0, "source": "WHO Urban Health 2016"},
    "Delhi": {"green_space_pct": 12.0, "source": "Delhi Master Plan 2020"},
    "Mumbai": {"green_space_pct": 15.0, "source": "Mumbai Environmental Status 2019"},
    "Beijing": {"green_space_pct": 44.4, "source": "Beijing Statistics 2020"},
    "Shanghai": {"green_space_pct": 38.0, "source": "Shanghai Statistics 2020"},
    # Americas - from OECD / city reports
    "New York": {"green_space_pct": 27.0, "source": "NYC Parks 2020"},
    "Los Angeles": {"green_space_pct": 15.0, "source": "LA City Planning 2019"},
    "Toronto": {"green_space_pct": 28.0, "source": "Toronto Green Standard 2020"},
    "Mexico City": {"green_space_pct": 18.0, "source": "CDMX Environment 2019"},
    "Sao Paulo": {"green_space_pct": 20.0, "source": "Sao Paulo SVMA 2019"},
    "Buenos Aires": {"green_space_pct": 22.0, "source": "Buenos Aires Statistics 2019"},
    # Africa - limited data, from reports and studies
    "Cairo": {"green_space_pct": 5.0, "source": "GOPP Egypt 2016"},
    "Johannesburg": {"green_space_pct": 24.0, "source": "Joburg City Parks 2019"},
    "Cape Town": {"green_space_pct": 32.0, "source": "Cape Town Environment 2019"},
    # Oceania - from OECD
    "Sydney": {"green_space_pct": 46.0, "source": "NSW Planning 2019"},
    "Melbourne": {"green_space_pct": 48.0, "source": "Melbourne Green Space 2019"},
    "Auckland": {"green_space_pct": 55.0, "source": "Auckland Council 2019"},
}

# Traffic congestion data
# Source: TomTom Traffic Index 2020-2023
# https://www.tomtom.com/traffic-index/ranking/
# Values represent congestion level (% extra travel time vs free-flow)
TRAFFIC_DATA = {
    # Europe
    "Vienna": {"congestion_pct": 27, "rank_global": 82, "year": 2022},
    "Berlin": {"congestion_pct": 30, "rank_global": 54, "year": 2022},
    "Paris": {"congestion_pct": 36, "rank_global": 23, "year": 2022},
    "London": {"congestion_pct": 37, "rank_global": 18, "year": 2022},
    "Madrid": {"congestion_pct": 25, "rank_global": 102, "year": 2022},
    "Rome": {"congestion_pct": 39, "rank_global": 12, "year": 2022},
    "Amsterdam": {"congestion_pct": 26, "rank_global": 92, "year": 2022},
    "Stockholm": {"congestion_pct": 24, "rank_global": 115, "year": 2022},
    "Copenhagen": {"congestion_pct": 23, "rank_global": 125, "year": 2022},
    "Prague": {"congestion_pct": 32, "rank_global": 41, "year": 2022},
    "Warsaw": {"congestion_pct": 32, "rank_global": 42, "year": 2022},
    "Budapest": {"congestion_pct": 35, "rank_global": 27, "year": 2022},
    "Brussels": {"congestion_pct": 35, "rank_global": 28, "year": 2022},
    "Zurich": {"congestion_pct": 27, "rank_global": 83, "year": 2022},
    "Helsinki": {"congestion_pct": 22, "rank_global": 135, "year": 2022},
    "Belgrade": {"congestion_pct": 34, "rank_global": 32, "year": 2022},
    "Sarajevo": {"congestion_pct": 30, "rank_global": 55, "year": 2022},
    # Asia
    "Tokyo": {"congestion_pct": 32, "rank_global": 43, "year": 2022},
    "Seoul": {"congestion_pct": 37, "rank_global": 19, "year": 2022},
    "Singapore": {"congestion_pct": 31, "rank_global": 48, "year": 2022},
    "Bangkok": {"congestion_pct": 53, "rank_global": 2, "year": 2022},
    "Delhi": {"congestion_pct": 39, "rank_global": 11, "year": 2022},
    "Mumbai": {"congestion_pct": 53, "rank_global": 1, "year": 2022},
    "Beijing": {"congestion_pct": 40, "rank_global": 10, "year": 2022},
    "Shanghai": {"congestion_pct": 35, "rank_global": 26, "year": 2022},
    # Americas
    "New York": {"congestion_pct": 32, "rank_global": 44, "year": 2022},
    "Los Angeles": {"congestion_pct": 34, "rank_global": 31, "year": 2022},
    "Toronto": {"congestion_pct": 36, "rank_global": 22, "year": 2022},
    "Mexico City": {"congestion_pct": 46, "rank_global": 4, "year": 2022},
    "Sao Paulo": {"congestion_pct": 38, "rank_global": 14, "year": 2022},
    "Buenos Aires": {"congestion_pct": 38, "rank_global": 15, "year": 2022},
    # Africa
    "Cairo": {"congestion_pct": 42, "rank_global": 7, "year": 2022},
    "Johannesburg": {"congestion_pct": 33, "rank_global": 36, "year": 2022},
    "Cape Town": {"congestion_pct": 32, "rank_global": 45, "year": 2022},
    # Oceania
    "Sydney": {"congestion_pct": 31, "rank_global": 47, "year": 2022},
    "Melbourne": {"congestion_pct": 32, "rank_global": 40, "year": 2022},
    "Auckland": {"congestion_pct": 29, "rank_global": 63, "year": 2022},
}


def download_owid_country_pm25():
    """
    Download country-level PM2.5 data from Our World in Data.
    This is used for the world choropleth map.
    """
    logger.info("Downloading Our World in Data PM2.5 dataset...")

    # Direct GitHub URL for the dataset
    url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/PM2.5%20air%20pollution%20-%20IHME/PM2.5%20air%20pollution%20-%20IHME.csv"

    try:
        df = pd.read_csv(url)
        logger.info(f"Downloaded {len(df)} records")

        # Save to raw directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "owid_pm25_country.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Saved to {output_path}")

        return df
    except Exception as e:
        logger.error(f"Failed to download OWID data: {e}")
        return None


def compile_city_supplementary_data() -> pd.DataFrame:
    """Compile all supplementary data into a single DataFrame."""
    logger.info("Compiling supplementary city data...")

    records = []
    for city_info in CITIES:
        city = city_info["city"]
        record = {
            "city": city,
            "country": city_info["country"],
            "country_code": city_info["country_code"],
            "region": city_info["region"],
            "lat": city_info["lat"],
            "lon": city_info["lon"],
        }

        # Add population data
        if city in POPULATION_DATA:
            pop = POPULATION_DATA[city]
            record["population"] = pop["population"]
            record["area_km2"] = pop["area_km2"]
            record["population_density"] = round(
                pop["population"] / pop["area_km2"], 1
            )
            record["pop_data_year"] = pop["year"]
        else:
            logger.warning(f"No population data for {city}")

        # Add green space data
        if city in GREEN_SPACE_DATA:
            gs = GREEN_SPACE_DATA[city]
            record["green_space_pct"] = gs["green_space_pct"]
            record["green_space_source"] = gs["source"]
        else:
            logger.warning(f"No green space data for {city}")

        # Add traffic data
        if city in TRAFFIC_DATA:
            tf = TRAFFIC_DATA[city]
            record["traffic_congestion_pct"] = tf["congestion_pct"]
            record["traffic_rank_global"] = tf["rank_global"]
            record["traffic_data_year"] = tf["year"]
        else:
            logger.warning(f"No traffic data for {city}")

        records.append(record)

    df = pd.DataFrame(records)
    return df


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Supplementary Data Fetcher")
    logger.info("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Download Our World in Data country PM2.5
    owid_df = download_owid_country_pm25()
    if owid_df is not None:
        logger.info(
            f"OWID data: {owid_df['Entity'].nunique()} countries, "
            f"years {owid_df['Year'].min()}-{owid_df['Year'].max()}"
        )

    # Compile city supplementary data
    city_df = compile_city_supplementary_data()

    # Save to CSV
    output_path = OUTPUT_DIR / "city_supplementary.csv"
    city_df.to_csv(output_path, index=False)
    logger.info(f"\nSaved city supplementary data to {output_path}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total cities: {len(city_df)}")

    # Check completeness
    for col in ["population", "green_space_pct", "traffic_congestion_pct"]:
        missing = city_df[col].isna().sum()
        logger.info(f"  {col}: {len(city_df) - missing}/{len(city_df)} cities")

    # Show sample
    logger.info("\nSample data (first 5 cities):")
    print(
        city_df[
            [
                "city",
                "region",
                "population",
                "population_density",
                "green_space_pct",
                "traffic_congestion_pct",
            ]
        ]
        .head()
        .to_string()
    )


if __name__ == "__main__":
    main()
