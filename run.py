#!/usr/bin/env python
"""
Run script for Urban Environmental Quality Dashboard

Usage:
    python run.py

Then open http://127.0.0.1:8050 in your browser.
"""

import os
import sys

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from dashboard.app import app

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Urban Environmental Quality Dashboard")
    print("=" * 60)
    print("\nStarting development server...")
    print("Open http://127.0.0.1:8050 in your browser")
    print("Press Ctrl+C to stop\n")

    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050,
    )
