#!/usr/bin/env python3
import sys
import argparse
import random
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.ctf_utils import fetch_ctf_list

def main():
    parser = argparse.ArgumentParser(description="Sample a list of CTFs from Grid and save to a .lst file.")
    parser.add_argument("year", help="Year (e.g., 2022)")
    parser.add_argument("period", help="LHC period (e.g., LHC22o)")
    parser.add_argument("run", help="Run number (e.g., 526463)")
    
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of CTFs to sample (default: 10). Pass 0 to get all available.")
    parser.add_argument("-o", "--output", help="Output .lst file path (default: <run>.lst)")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prefer-skimmed", action="store_true", help="Prefer to sample skimmed CTFs before raw")
    group.add_argument("--prefer-raw", action="store_true", help="Prefer to sample raw CTFs before skimmed")

    args = parser.parse_args()

    ctf_list, skimmed_ctf_list = fetch_ctf_list(args.year, args.period, args.run)
    
    if args.prefer_raw:
        primary_list = ctf_list
        secondary_list = skimmed_ctf_list
    else:
        primary_list = skimmed_ctf_list
        secondary_list = ctf_list

    random.shuffle(primary_list)
    random.shuffle(secondary_list)

    needed = args.num

    # Support getting all by parsing num=0 or simply if needed > total
    if needed <= 0:
        sampled = primary_list + secondary_list
    else:
        if len(primary_list) >= needed:
            sampled = primary_list[:needed]
        else:
            sampled = list(primary_list)
            remaining = needed - len(primary_list)
            
            if len(secondary_list) >= remaining:
                sampled += secondary_list[:remaining]
            else:
                sampled += secondary_list

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
