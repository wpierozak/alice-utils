#!/usr/bin/env python3
"""
Fetch Period Summary from AliBookkeeping API.

Usage examples:
    # Fetch period summary by name
    python fetch_period_summary.py --period LHC25aj -o summary.json

    # Fetch period summary by numeric period ID
    python fetch_period_summary.py --period-id 178 -o summary.json
"""
import argparse
import sys
import logging
import requests
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.period_summary import PeriodSummaryAPI

# Configure basic logging for the script execution
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Period Summary from AliBookkeeping API."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--period", type=str, help="LHC period name (e.g., 'LHC25aj') — resolves ID automatically")
    mode.add_argument("--period-id", type=int, help="Numeric LHC period ID (if already known)")

    parser.add_argument("-o", "--output", required=True, help="Output JSON file name")
    parser.add_argument("-t", "--token", help="API token (if not provided, uses ALIBK_API_TOKEN env var)")

    args = parser.parse_args()

    try:
        api = PeriodSummaryAPI(token=args.token)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.period:
            print(f"Fetching period summary for '{args.period}'...")
            data = api.fetch_summary_by_name(args.period)
        else:
            print(f"Fetching period summary for period ID {args.period_id}...")
            data = api.fetch_summary(args.period_id)

        api.save_to_json(data, args.output)
        print(f"Successfully saved period summary to {args.output}")

    except requests.exceptions.HTTPError as he:
        print(f"HTTP Error occurred: {he}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
