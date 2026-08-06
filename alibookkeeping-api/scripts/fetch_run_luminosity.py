#!/usr/bin/env python3
"""Fetch integrated luminosity values for a list of runs and save them as CSV."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.run_luminosity import RunLuminosityAPI


def parse_run_numbers(values: list[str], input_file: str | None) -> list[int]:
    """Parse positional/comma-separated run numbers and an optional text file."""
    tokens = list(values)
    if input_file:
        content = Path(input_file).read_text(encoding="utf-8")
        tokens.extend(line.partition("#")[0] for line in content.splitlines())
    runs = []
    for token in tokens:
        for value in re.split(r"[,;\s]+", token.strip()):
            if value:
                runs.append(int(value))
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch AliBookkeeping run luminosity values and write a semicolon-delimited CSV."
    )
    parser.add_argument("runs", nargs="*", help="Run numbers (space- or comma-separated)")
    parser.add_argument("-i", "--input", help="Text file containing run numbers")
    parser.add_argument("-o", "--output", required=True, help="Output CSV path")
    parser.add_argument("-t", "--token", help="API token (otherwise ALIBK_API_TOKEN is used)")
    args = parser.parse_args()

    try:
        run_numbers = parse_run_numbers(args.runs, args.input)
    except (OSError, ValueError) as error:
        parser.error(f"could not read run list: {error}")
    if not run_numbers:
        parser.error("provide at least one run number or use --input")

    try:
        api = RunLuminosityAPI(token=args.token)
        api.export_csv(run_numbers, args.output)
    except (requests.RequestException, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Successfully wrote luminosity for {len(run_numbers)} runs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
