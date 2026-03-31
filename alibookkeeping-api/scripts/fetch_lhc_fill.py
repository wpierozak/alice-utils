#!/usr/bin/env python3
import argparse
import sys
import logging
import requests
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.lhc_fill_api import LHCFillAPI

# Configure basic logging for the script execution
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Fetch LHC Fill data from AliBookkeeping API and save to JSON.")
    parser.add_argument("fill_number", type=int, help="The LHC fill number to fetch (e.g., 11560)")
    parser.add_argument("-o", "--output", help="Output JSON file name (default: lhc_fill_<fill_number>.json)")
    parser.add_argument("-t", "--token", help="API token (if not provided, uses ALIBK_API_TOKEN env var)")
    
    args = parser.parse_args()
    
    output_file = args.output or f"lhc_fill_{args.fill_number}.json"
    
    try:
        api = LHCFillAPI(token=args.token)
        api.save_fill_data(args.fill_number, output_file)
        print(f"Successfully saved LHC fill {args.fill_number} to {output_file}")
    except requests.exceptions.HTTPError as he:
        print(f"HTTP Error occurred: {he}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
