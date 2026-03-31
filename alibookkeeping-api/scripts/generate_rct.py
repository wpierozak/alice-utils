#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.alibk_framework import AliBookkeepingAPI
from modules.rct_generator import generate_rct_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch run information from Ali-Bookkeeping API and generate RCT CSV.")
    parser.add_argument("--period", required=True, help="Full period name, e.g., 'LHC25aj'")
    parser.add_argument("--out-csv", required=True, help="Output CSV path, e.g., 'rct.csv'")
    parser.add_argument("--include-tag", help="Only include runs with this tag, e.g., 'ITS'", default=None)
    parser.add_argument("--exclude-tag", help="Exclude runs with this tag, e.g., 'ITS'", default=None)
    parser.add_argument("--token", help="Override API token (or use ALIBK_API_TOKEN env var)", default=None)
    args = parser.parse_args()

    try:
        api = AliBookkeepingAPI(token=args.token)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    print(f"Fetching runs for period '{args.period}'...")
    try:
        runs = api.fetch_runs(period_name=args.period, include_tag=args.include_tag, exclude_tag=args.exclude_tag)
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return
        
    print(f"Retrieved {len(runs)} runs.")

    if not runs:
        print("No runs found. CSV will not be created.")
        return

    generate_rct_csv(runs, args.out_csv)
    print(f"Successfully generated RCT at {args.out_csv}")

if __name__ == "__main__":
    main()
