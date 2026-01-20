# Real Data Integration Plan
## Urban Environmental Quality Dashboard

**Student**: Amira Midzic, 12532872
**Date**: January 2026
**Phase**: Model & Report (with real data)

---

## 1. Data Requirements Summary

The dashboard requires the following variables:

| Variable | Type | Required For | Priority |
|----------|------|--------------|----------|
| `pm25` | float | All charts, clustering | Critical |
| `pm10` | float | Correlation, parallel coords | Critical |
| `no2` | float | Correlation, parallel coords | High |
| `o3` | float | Correlation, parallel coords | High |
| `city` | string | All charts | Critical |
| `country` | string | Grouping, filtering | Critical |
| `region` | string | Filtering (Europe, Asia, etc.) | Critical |
| `lat`, `lon` | float | Map visualization | Critical |
| `population` | int | Scatter plot, context | Medium |
| `population_density` | float | Scatter, clustering | High |
| `green_space_pct` | float | Clustering, correlation | High |
| `traffic_intensity` | float | Clustering, correlation | Medium |
| `air_quality_index` | float | Comparison chart | Medium |
| `date`/`year`/`month` | datetime | Time series | Critical |

---

## 2. Real Data Sources

### 2.1 Air Quality Data

#### Source A: OpenAQ API v3 (Primary)
- **URL**: https://api.openaq.org/v3
- **Coverage**: Global, 60,000+ monitoring stations
- **Variables**: PM2.5, PM10, NO2, O3, SO2, CO
- **Granularity**: Hourly/Daily measurements
- **Time Range**: 2020-2023 (target)
- **API Key**: Required (you have one)

**Data Fetching Strategy**:
1. Query locations by country/city coordinates
2. Select representative stations per city (government/reference grade preferred)
3. Fetch daily aggregates using `/sensors/{id}/days` endpoint
4. Aggregate to monthly city-level averages

**Target Cities for OpenAQ**:
- Europe (15 cities): Vienna, Berlin, Paris, London, Madrid, Rome, Amsterdam, Stockholm, Copenhagen, Prague, Warsaw, Budapest, Brussels, Zurich, Helsinki
- Asia (8 cities): Tokyo, Seoul, Singapore, Bangkok, Delhi, Mumbai, Beijing, Shanghai
- Americas (6 cities): New York, Los Angeles, Toronto, Mexico City, Sao Paulo, Buenos Aires
- Africa (3 cities): Cairo, Johannesburg, Cape Town
- Oceania (3 cities): Sydney, Melbourne, Auckland

**Total**: ~35 cities with real air quality data

#### Source B: European Environment Agency (EEA)
- **URL**: https://www.eea.europa.eu/en/datahub/datahubitem-view/3b8eb428-f9e5-4a7c-b0f0-7d463c2b231c
- **Dataset**: Air Quality e-Reporting (AQ e-Reporting)
- **Variables**: PM2.5, PM10, NO2, O3 (validated annual/seasonal)
- **Coverage**: All EU countries
- **Time Range**: 2020-2023
- **Format**: CSV download

**Use Case**: Supplement/validate OpenAQ data for European cities

---

### 2.2 Population & Urban Density

#### Source C: UN World Urbanization Prospects
- **URL**: https://population.un.org/wup/Download/
- **Variables**: City population, urban agglomeration data
- **Coverage**: 300+ major cities worldwide
- **Time Range**: Estimates for 2020, projections

#### Source D: Eurostat Urban Audit
- **URL**: https://ec.europa.eu/eurostat/web/cities/data/database
- **Variables**: Population, population density (per km²), land area
- **Coverage**: All EU cities
- **Format**: CSV/TSV download

---

### 2.3 Green Space Data

#### Source E: European Urban Atlas (Copernicus)
- **URL**: https://land.copernicus.eu/en/products/urban-atlas
- **Variables**: Green urban areas (%), forests, parks
- **Coverage**: 800+ European urban areas
- **Resolution**: Land use classification
- **Format**: GIS/derived statistics

#### Source F: OECD Metropolitan Areas Green Space
- **URL**: https://stats.oecd.org/ (Metropolitan areas database)
- **Variables**: Green space per capita, urban green indicators
- **Coverage**: OECD countries (35+ countries)
- **Format**: CSV download

#### Source G: WHO Global Urban Health Observatory
- **URL**: https://www.who.int/data/gho/data/indicators
- **Variables**: Green space availability indicators
- **Coverage**: Global (selected cities)

---

### 2.4 Traffic & Transport Data

#### Source H: TomTom Traffic Index
- **URL**: https://www.tomtom.com/traffic-index/ranking/
- **Variables**: Congestion level (%), average commute time
- **Coverage**: 400+ cities worldwide
- **Note**: Publicly available rankings (may need manual extraction)

#### Source I: Eurostat Transport Statistics
- **URL**: https://ec.europa.eu/eurostat/web/transport/data/database
- **Variables**: Vehicle registrations, road traffic intensity
- **Coverage**: EU cities/countries
- **Format**: CSV download

---

### 2.5 Vienna-Specific Data (Deep Dive)

#### Source J: Vienna Open Data Portal
- **URL**: https://www.data.gv.at/ and https://digitales.wien.gv.at/
- **Datasets**:
  1. **Air Quality**: `luftguete-messdaten` - hourly/daily PM, NO2, O3
  2. **Green Spaces**: `gruenflaechen-wien` - parks, urban forests area
  3. **Traffic Counts**: `dauerzaehlstellen` - permanent traffic counters
  4. **Bike Counters**: `radverkehrszaehlstellen` - cycling volumes

---

### 2.6 Country-Level Context (Choropleth Map)

#### Source K: Our World in Data
- **URL**: https://github.com/owid/owid-datasets
- **Direct CSV**: https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/PM2.5%20air%20pollution%20-%20IHME/PM2.5%20air%20pollution%20-%20IHME.csv
- **Variables**: Mean annual PM2.5 exposure by country
- **Coverage**: All countries
- **Use Case**: The world choropleth map you showed in the screenshots

---

## 3. Data Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   OpenAQ     │  │    EEA       │  │  Vienna      │          │
│  │   API v3     │  │   (Europe)   │  │  Open Data   │          │
│  │  (PM, NO2)   │  │  (Validated) │  │  (Detail)    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────┴─────────────────┴─────────────────┴───────┐          │
│  │              RAW DATA (JSON/CSV)                 │          │
│  │  data/raw/openaq_*.json                          │          │
│  │  data/raw/eea_*.csv                              │          │
│  │  data/raw/vienna_*.csv                           │          │
│  └──────────────────────┬───────────────────────────┘          │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                    DATA PROCESSING LAYER                        │
├─────────────────────────┼───────────────────────────────────────┤
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  1. CLEAN & VALIDATE                                │       │
│  │     - Remove invalid measurements                   │       │
│  │     - Handle missing values                         │       │
│  │     - Standardize units (µg/m³)                     │       │
│  └───────────────────────┬─────────────────────────────┘       │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  2. AGGREGATE                                       │       │
│  │     - Station → City level (median/mean)            │       │
│  │     - Daily → Monthly averages                      │       │
│  │     - Add seasonal/yearly indicators                │       │
│  └───────────────────────┬─────────────────────────────┘       │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  3. ENRICH                                          │       │
│  │     - Add population data (UN/Eurostat)             │       │
│  │     - Add green space % (Copernicus/OECD)           │       │
│  │     - Add traffic proxy (TomTom/Eurostat)           │       │
│  │     - Assign region labels                          │       │
│  └───────────────────────┬─────────────────────────────┘       │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  4. COMPUTE DERIVED METRICS                         │       │
│  │     - Air Quality Index (EPA formula)               │       │
│  │     - Population density (pop/area)                 │       │
│  └───────────────────────┬─────────────────────────────┘       │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                    OUTPUT LAYER                                 │
├──────────────────────────┼──────────────────────────────────────┤
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  data/cities_timeseries.csv                         │       │
│  │  - Monthly data for 35+ cities                      │       │
│  │  - Columns: city, country, region, lat, lon,        │       │
│  │    population, population_density, green_space_pct, │       │
│  │    traffic_intensity, pm25, pm10, no2, o3,          │       │
│  │    air_quality_index, year, month, date             │       │
│  │  - Rows: ~35 cities × 48 months = ~1,680 rows       │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  data/cities_summary.csv                            │       │
│  │  - One row per city (temporal average)              │       │
│  │  - Used for clustering and static comparisons       │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  data/cities_clustered.csv                          │       │
│  │  - After K-means clustering                         │       │
│  │  - Adds: cluster, pca_1, pca_2                      │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Steps

### Phase 1: Data Collection Scripts (Week 1)

| Step | Script | Description |
|------|--------|-------------|
| 1.1 | `data/fetch_openaq.py` | Fetch air quality from OpenAQ API |
| 1.2 | `data/fetch_eea.py` | Download EEA validated data |
| 1.3 | `data/fetch_vienna.py` | Vienna Open Data air quality |
| 1.4 | `data/fetch_population.py` | UN/Eurostat population data |
| 1.5 | `data/fetch_greenspace.py` | Copernicus/OECD green space |
| 1.6 | `data/fetch_traffic.py` | TomTom/Eurostat traffic proxies |

### Phase 2: Data Processing (Week 1-2)

| Step | Script | Description |
|------|--------|-------------|
| 2.1 | `data/clean_airquality.py` | Clean and validate air quality data |
| 2.2 | `data/aggregate_cities.py` | Station → City aggregation |
| 2.3 | `data/merge_datasets.py` | Combine all sources |
| 2.4 | `data/compute_derived.py` | Calculate AQI, density, etc. |

### Phase 3: Quality Assurance

| Step | Action | Description |
|------|--------|-------------|
| 3.1 | Coverage check | Verify all 35 cities have data |
| 3.2 | Temporal check | Confirm 2020-2023 coverage |
| 3.3 | Vienna validation | Compare with official reports |
| 3.4 | Outlier review | Check for unrealistic values |

### Phase 4: Dashboard Integration

| Step | Action | Description |
|------|--------|-------------|
| 4.1 | Re-run clustering | Apply K-means to real data |
| 4.2 | Update dashboard | Verify all visualizations work |
| 4.3 | Validate insights | Document findings vs synthetic |

---

## 5. City Selection Matrix

| City | OpenAQ | EEA | Population | Green Space | Traffic |
|------|--------|-----|------------|-------------|---------|
| **Vienna** | ✓ | ✓ | Eurostat | Vienna OD | Vienna OD |
| Berlin | ✓ | ✓ | Eurostat | Copernicus | Eurostat |
| Paris | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| London | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Madrid | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Rome | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Amsterdam | ✓ | ✓ | Eurostat | Copernicus | Eurostat |
| Stockholm | ✓ | ✓ | Eurostat | Copernicus | Eurostat |
| Copenhagen | ✓ | ✓ | Eurostat | Copernicus | Eurostat |
| Prague | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Warsaw | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Budapest | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Brussels | ✓ | ✓ | Eurostat | Copernicus | TomTom |
| Zurich | ✓ | - | UN | OECD | TomTom |
| Helsinki | ✓ | ✓ | Eurostat | Copernicus | Eurostat |
| **Tokyo** | ✓ | - | UN | OECD | TomTom |
| **Seoul** | ✓ | - | UN | OECD | TomTom |
| **Singapore** | ✓ | - | UN | OECD | TomTom |
| **Bangkok** | ✓ | - | UN | OECD | TomTom |
| **Delhi** | ✓ | - | UN | - | TomTom |
| **Mumbai** | ✓ | - | UN | - | TomTom |
| **Beijing** | ✓ | - | UN | OECD | TomTom |
| **Shanghai** | ✓ | - | UN | OECD | TomTom |
| **New York** | ✓ | - | UN | OECD | TomTom |
| **Los Angeles** | ✓ | - | UN | OECD | TomTom |
| **Toronto** | ✓ | - | UN | OECD | TomTom |
| **Mexico City** | ✓ | - | UN | - | TomTom |
| **Sao Paulo** | ✓ | - | UN | - | TomTom |
| **Buenos Aires** | ✓ | - | UN | - | TomTom |
| **Cairo** | ✓ | - | UN | - | TomTom |
| **Johannesburg** | ✓ | - | UN | - | - |
| **Cape Town** | ✓ | - | UN | - | - |
| **Sydney** | ✓ | - | UN | OECD | TomTom |
| **Melbourne** | ✓ | - | UN | OECD | TomTom |
| **Auckland** | ✓ | - | UN | OECD | - |

**Legend**: ✓ = Available, - = Not directly available (will use proxy/estimate)

---

## 6. Fallback Strategy for Missing Data

For cities/variables where real data is unavailable:

1. **Green Space**:
   - Primary: Copernicus Urban Atlas (Europe), OECD stats (OECD countries)
   - Fallback: Research papers, city sustainability reports
   - Last resort: Satellite-derived NDVI (Normalized Difference Vegetation Index)

2. **Traffic Intensity**:
   - Primary: TomTom congestion index
   - Fallback: Vehicle registrations per capita (Eurostat/national stats)
   - Proxy: Population density × GDP per capita (research shows correlation)

3. **Missing Air Quality Months**:
   - Interpolation from adjacent months
   - Use EEA validated annual averages
   - Flag as estimated in metadata

---

## 7. Data Quality Documentation

For the report, document:
- Number of monitoring stations per city
- Temporal coverage (% of months with data)
- Data sources for each variable
- Any imputation/estimation methods used
- Validation against official city reports

---

## 8. Files to Create

```
urban-env-dashboard/
├── data/
│   ├── raw/                          # Raw downloaded data
│   │   ├── openaq/
│   │   ├── eea/
│   │   ├── vienna/
│   │   └── supplementary/
│   ├── processed/                    # Intermediate files
│   ├── fetch_openaq.py              # OpenAQ API fetcher
│   ├── fetch_supplementary.py       # Other sources
│   ├── process_data.py              # Main processing pipeline
│   ├── cities_timeseries.csv        # Final output
│   ├── cities_summary.csv           # Final output
│   └── data_sources.json            # Metadata about sources
```

---

## 9. Timeline Estimate

| Week | Tasks |
|------|-------|
| 1 | Data collection scripts, fetch all raw data |
| 2 | Processing pipeline, merge datasets |
| 3 | Quality checks, re-run clustering, update dashboard |
| 4 | Documentation, report writing |

---

## 10. Next Steps

1. **Immediate**: Create `fetch_openaq.py` with your API key
2. **Download**: EEA data (manual CSV download)
3. **Vienna**: Fetch Vienna Open Data datasets
4. **Supplementary**: Gather population and green space data
5. **Process**: Run the full pipeline
6. **Validate**: Compare Vienna data with official reports
