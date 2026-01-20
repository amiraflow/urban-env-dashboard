"""
City Definitions for Real Data Collection

Contains target cities with their coordinates, country, region, and metadata
for fetching real environmental data from various sources.
"""

# Target cities for the dashboard (37 cities across 5 regions)
# Coordinates are city center approximate values for OpenAQ location search

CITIES = [
    # =========================================================================
    # EUROPE (17 cities) - Best data coverage via EEA + Eurostat + Copernicus
    # =========================================================================
    {
        "city": "Vienna",
        "country": "Austria",
        "country_code": "AT",
        "region": "Europe",
        "lat": 48.2082,
        "lon": 16.3738,
        "search_radius_km": 25,  # Radius for finding OpenAQ stations
        "priority": 1,  # Primary focus city
    },
    {
        "city": "Berlin",
        "country": "Germany",
        "country_code": "DE",
        "region": "Europe",
        "lat": 52.5200,
        "lon": 13.4050,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Paris",
        "country": "France",
        "country_code": "FR",
        "region": "Europe",
        "lat": 48.8566,
        "lon": 2.3522,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "London",
        "country": "United Kingdom",
        "country_code": "GB",
        "region": "Europe",
        "lat": 51.5074,
        "lon": -0.1278,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Madrid",
        "country": "Spain",
        "country_code": "ES",
        "region": "Europe",
        "lat": 40.4168,
        "lon": -3.7038,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Rome",
        "country": "Italy",
        "country_code": "IT",
        "region": "Europe",
        "lat": 41.9028,
        "lon": 12.4964,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Amsterdam",
        "country": "Netherlands",
        "country_code": "NL",
        "region": "Europe",
        "lat": 52.3676,
        "lon": 4.9041,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Stockholm",
        "country": "Sweden",
        "country_code": "SE",
        "region": "Europe",
        "lat": 59.3293,
        "lon": 18.0686,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Copenhagen",
        "country": "Denmark",
        "country_code": "DK",
        "region": "Europe",
        "lat": 55.6761,
        "lon": 12.5683,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Prague",
        "country": "Czech Republic",
        "country_code": "CZ",
        "region": "Europe",
        "lat": 50.0755,
        "lon": 14.4378,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Warsaw",
        "country": "Poland",
        "country_code": "PL",
        "region": "Europe",
        "lat": 52.2297,
        "lon": 21.0122,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Budapest",
        "country": "Hungary",
        "country_code": "HU",
        "region": "Europe",
        "lat": 47.4979,
        "lon": 19.0402,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Brussels",
        "country": "Belgium",
        "country_code": "BE",
        "region": "Europe",
        "lat": 50.8503,
        "lon": 4.3517,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Zurich",
        "country": "Switzerland",
        "country_code": "CH",
        "region": "Europe",
        "lat": 47.3769,
        "lon": 8.5417,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Helsinki",
        "country": "Finland",
        "country_code": "FI",
        "region": "Europe",
        "lat": 60.1699,
        "lon": 24.9384,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Belgrade",
        "country": "Serbia",
        "country_code": "RS",
        "region": "Europe",
        "lat": 44.7866,
        "lon": 20.4489,
        "search_radius_km": 20,
        "priority": 2,  # Important comparison for Vienna (regional, high winter pollution)
    },
    {
        "city": "Sarajevo",
        "country": "Bosnia and Herzegovina",
        "country_code": "BA",
        "region": "Europe",
        "lat": 43.8563,
        "lon": 18.4131,
        "search_radius_km": 20,
        "priority": 2,  # Known for severe winter pollution (valley geography)
    },

    # =========================================================================
    # ASIA (8 cities) - OpenAQ + UN population + OECD/TomTom
    # =========================================================================
    {
        "city": "Tokyo",
        "country": "Japan",
        "country_code": "JP",
        "region": "Asia",
        "lat": 35.6762,
        "lon": 139.6503,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Seoul",
        "country": "South Korea",
        "country_code": "KR",
        "region": "Asia",
        "lat": 37.5665,
        "lon": 126.9780,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Singapore",
        "country": "Singapore",
        "country_code": "SG",
        "region": "Asia",
        "lat": 1.3521,
        "lon": 103.8198,
        "search_radius_km": 20,
        "priority": 2,
    },
    {
        "city": "Bangkok",
        "country": "Thailand",
        "country_code": "TH",
        "region": "Asia",
        "lat": 13.7563,
        "lon": 100.5018,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Delhi",
        "country": "India",
        "country_code": "IN",
        "region": "Asia",
        "lat": 28.7041,
        "lon": 77.1025,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Mumbai",
        "country": "India",
        "country_code": "IN",
        "region": "Asia",
        "lat": 19.0760,
        "lon": 72.8777,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Beijing",
        "country": "China",
        "country_code": "CN",
        "region": "Asia",
        "lat": 39.9042,
        "lon": 116.4074,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Shanghai",
        "country": "China",
        "country_code": "CN",
        "region": "Asia",
        "lat": 31.2304,
        "lon": 121.4737,
        "search_radius_km": 25,
        "priority": 2,
    },

    # =========================================================================
    # AMERICAS (6 cities) - OpenAQ + UN population + OECD/TomTom
    # =========================================================================
    {
        "city": "New York",
        "country": "United States",
        "country_code": "US",
        "region": "Americas",
        "lat": 40.7128,
        "lon": -74.0060,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Los Angeles",
        "country": "United States",
        "country_code": "US",
        "region": "Americas",
        "lat": 34.0522,
        "lon": -118.2437,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Toronto",
        "country": "Canada",
        "country_code": "CA",
        "region": "Americas",
        "lat": 43.6532,
        "lon": -79.3832,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Mexico City",
        "country": "Mexico",
        "country_code": "MX",
        "region": "Americas",
        "lat": 19.4326,
        "lon": -99.1332,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Sao Paulo",
        "country": "Brazil",
        "country_code": "BR",
        "region": "Americas",
        "lat": -23.5505,
        "lon": -46.6333,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Buenos Aires",
        "country": "Argentina",
        "country_code": "AR",
        "region": "Americas",
        "lat": -34.6037,
        "lon": -58.3816,
        "search_radius_km": 25,
        "priority": 2,
    },

    # =========================================================================
    # AFRICA (3 cities) - OpenAQ + UN population, limited other data
    # =========================================================================
    {
        "city": "Cairo",
        "country": "Egypt",
        "country_code": "EG",
        "region": "Africa",
        "lat": 30.0444,
        "lon": 31.2357,
        "search_radius_km": 25,
        "priority": 3,
    },
    {
        "city": "Johannesburg",
        "country": "South Africa",
        "country_code": "ZA",
        "region": "Africa",
        "lat": -26.2041,
        "lon": 28.0473,
        "search_radius_km": 25,
        "priority": 3,
    },
    {
        "city": "Cape Town",
        "country": "South Africa",
        "country_code": "ZA",
        "region": "Africa",
        "lat": -33.9249,
        "lon": 18.4241,
        "search_radius_km": 25,
        "priority": 3,
    },

    # =========================================================================
    # OCEANIA (3 cities) - OpenAQ + UN population + OECD
    # =========================================================================
    {
        "city": "Sydney",
        "country": "Australia",
        "country_code": "AU",
        "region": "Oceania",
        "lat": -33.8688,
        "lon": 151.2093,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Melbourne",
        "country": "Australia",
        "country_code": "AU",
        "region": "Oceania",
        "lat": -37.8136,
        "lon": 144.9631,
        "search_radius_km": 25,
        "priority": 2,
    },
    {
        "city": "Auckland",
        "country": "New Zealand",
        "country_code": "NZ",
        "region": "Oceania",
        "lat": -36.8485,
        "lon": 174.7633,
        "search_radius_km": 25,
        "priority": 2,
    },
]

# Pollutants of interest and their OpenAQ parameter names
POLLUTANTS = {
    "pm25": {"openaq_name": "pm25", "unit": "µg/m³", "display": "PM2.5"},
    "pm10": {"openaq_name": "pm10", "unit": "µg/m³", "display": "PM10"},
    "no2": {"openaq_name": "no2", "unit": "µg/m³", "display": "NO₂"},
    "o3": {"openaq_name": "o3", "unit": "µg/m³", "display": "O₃"},
}

# Time range for data collection
DATE_RANGE = {
    "start": "2020-01-01",
    "end": "2023-12-31",
}


def get_cities_by_region(region: str = None) -> list:
    """Get cities, optionally filtered by region."""
    if region:
        return [c for c in CITIES if c["region"] == region]
    return CITIES


def get_city_by_name(name: str) -> dict:
    """Get a single city by name."""
    for city in CITIES:
        if city["city"].lower() == name.lower():
            return city
    return None


def get_european_cities() -> list:
    """Get all European cities (best data coverage)."""
    return get_cities_by_region("Europe")


def get_all_country_codes() -> list:
    """Get unique country codes for API queries."""
    return list(set(c["country_code"] for c in CITIES))


if __name__ == "__main__":
    print(f"Total cities: {len(CITIES)}")
    for region in ["Europe", "Asia", "Americas", "Africa", "Oceania"]:
        cities = get_cities_by_region(region)
        print(f"  {region}: {len(cities)} cities")
    print(f"\nCountry codes: {get_all_country_codes()}")
