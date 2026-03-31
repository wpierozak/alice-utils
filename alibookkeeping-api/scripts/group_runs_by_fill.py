#!/usr/bin/env python3
import json
import argparse
import sys
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.run_grouping import group_runs

def main():
    parser = argparse.ArgumentParser(description="Group runs by LHC fill (lhcFill.fillNumber).")
    parser.add_argument("-i", "--input", default="alice_runs.json", help="Input JSON file (default: alice_runs.json)")
    parser.add_argument("-o", "--output", default="runs_by_fill.json", help="Output JSON file (default: runs_by_fill.json)")
    parser.add_argument("--full-runs", action="store_true", help="Store full run objects instead of just run numbers")
    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input}'", file=sys.stderr)
        sys.exit(1)

    # Handle wrapper "data" field if it exists
    runs = data.get('data', data) if isinstance(data, dict) else data

    if not isinstance(runs, list):
        print("Error: Expected input data to be a list of runs, or a dict containing a 'data' list.", file=sys.stderr)
        sys.exit(1)

    grouped_runs = group_runs(runs, args.full_runs)

    with open(args.output, 'w') as f:
        json.dump(grouped_runs, f, indent=4)
        
    print(f"Successfully processed {len(runs)} runs.")
    print(f"Grouped into {len(grouped_runs)} fills.")
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
