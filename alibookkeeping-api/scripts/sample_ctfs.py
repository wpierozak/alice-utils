#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.ctf_utils import fetch_ctfs_with_preference

def main():
    parser = argparse.ArgumentParser(description="Sample a list of CTFs from Grid, specifying a preference for skimmed or raw, and save to a .lst file.")
    parser.add_argument("year", help="Year (e.g., 2022)")
    parser.add_argument("period", help="LHC period (e.g., LHC22o)")
    parser.add_argument("run", help="Run number (e.g., 526463)")
    
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of CTFs to sample (default: 10). Pass 0 to get all available.")
    parser.add_argument("-o", "--output", help="Output .lst file path (default: <run>.lst)")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--prefer-skimmed", action="store_true", help="Prefer to sample skimmed CTFs, falling back to raw if not found.")
    group.add_argument("--prefer-raw", action="store_true", help="Prefer to sample raw CTFs, falling back to skimmed if not found.")

    args = parser.parse_args()

    preference = "skimmed"
    if args.prefer_raw:
        preference = "raw"

    sampled = fetch_ctfs_with_preference(args.year, args.period, args.run, prefer=preference, limit=args.num)

    output_path = args.output if args.output else f"{args.run}.lst"

    with open(output_path, "w") as f:
        for ctf in sampled:
            f.write(f"{ctf}\n")
            
    if sampled:
        print(f"Sampled {len(sampled)} CTFs and saved to {output_path}")
    else:
        print("Warning: No CTFs found to write.", file=sys.stderr)

if __name__ == "__main__":
    main()
