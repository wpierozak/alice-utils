#!/usr/bin/env python3
"""
Fetch LHC Period Statistics from AliBookkeeping API.

Usage examples:
    # Fetch all period statistics and save to JSON
    python fetch_lhc_period_statistics.py --all -o all_periods.json

    # Fetch statistics for a specific period
    python fetch_lhc_period_statistics.py --period LHC25aj -o period_stats.json

    # List all available period names
    python fetch_lhc_period_statistics.py --list
"""
import argparse
import sys
import logging
import requests
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.lhc_period_statistics import LHCPeriodStatisticsAPI

# Configure basic logging for the script execution
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    parser = argparse.ArgumentParser(
        description="Fetch LHC Period Statistics from AliBookkeeping API."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true", help="Fetch all period statistics")
    mode.add_argument("--period", type=str, help="Fetch statistics for a specific period name (e.g., 'LHC25aj')")
    mode.add_argument("--list", action="store_true", help="List all available period names")

    parser.add_argument("-o", "--output", help="Output JSON file name (required for --all and --period)")
    parser.add_argument("-t", "--token", help="API token (if not provided, uses ALIBK_API_TOKEN env var)")

    args = parser.parse_args()

    try:
        api = LHCPeriodStatisticsAPI(token=args.token)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.list:
            names = api.get_period_names()
            print(f"Found {len(names)} LHC periods:")
            for name in names:
                print(f"  {name}")

        elif args.all:
            if not args.output:
                parser.error("--output is required when using --all")
            data = api.fetch_all()
            api.save_to_json(data, args.output)
            print(f"Successfully saved {len(data)} period statistics entries to {args.output}")

        elif args.period:
            if not args.output:
                parser.error("--output is required when using --period")
            data = api.get_statistics_for_period(args.period)
            if data is None:
                print(f"Period '{args.period}' not found.", file=sys.stderr)
                sys.exit(1)
            api.save_to_json(data, args.output)
            print(f"Successfully saved statistics for '{args.period}' to {args.output}")

    except requests.exceptions.HTTPError as he:
        print(f"HTTP Error occurred: {he}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
