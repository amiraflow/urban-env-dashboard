"""
Master Data Fetching Script

Runs all data fetching and processing scripts in order:
1. Fetch air quality data from OpenAQ
2. Fetch supplementary data (population, green space, traffic)
3. Process and merge all data
4. Run clustering

Usage:
    python fetch_all_data.py

Prerequisites:
    - Set OPENAQ_API_KEY environment variable
    - Or create .env file with OPENAQ_API_KEY=your_key
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name: str) -> bool:
    """Run a Python script and return success status."""
    script_path = Path(__file__).parent / script_name

    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return False

def main():
    print("="*60)
    print("Urban Environmental Quality Dashboard - Data Pipeline")
    print("="*60)

    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAQ_API_KEY")
    if not api_key:
        print("\nERROR: OPENAQ_API_KEY not found!")
        print("\nTo set up:")
        print("  1. Get a free API key from https://explore.openaq.org/")
        print("  2. Create a .env file in this directory with:")
        print("     OPENAQ_API_KEY=your_key_here")
        print("  3. Or set environment variable:")
        print("     export OPENAQ_API_KEY=your_key_here")
        sys.exit(1)

    print(f"\nAPI key found: {api_key[:8]}...")

    # Step 1: Fetch supplementary data (doesn't need API)
    print("\n[Step 1/3] Fetching supplementary data...")
    if not run_script("fetch_supplementary.py"):
        print("Warning: Supplementary data fetch had issues")

    # Step 2: Fetch OpenAQ air quality data
    print("\n[Step 2/3] Fetching OpenAQ air quality data...")
    print("This may take 10-30 minutes depending on API rate limits...")
    if not run_script("fetch_openaq.py"):
        print("Error: OpenAQ fetch failed")
        sys.exit(1)

    # Step 3: Process and merge all data
    print("\n[Step 3/3] Processing and merging data...")
    if not run_script("process_data.py"):
        print("Error: Data processing failed")
        sys.exit(1)

    print("\n" + "="*60)
    print("DATA PIPELINE COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - data/cities_timeseries.csv")
    print("  - data/cities_summary.csv")
    print("  - data/cities_clustered.csv")
    print("\nYou can now run the dashboard:")
    print("  python run.py")

if __name__ == "__main__":
    main()
