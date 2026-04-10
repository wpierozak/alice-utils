import os
import subprocess

def fetch_ctf_list(year: str, period: str, run: str) -> tuple[list[str], list[str]]:
    remote_data_path = f"/alice/data/{year}/{period}/{run}/raw"
    skimmed_data_path = f"/alice/data/{year}/{period}/{run}/skimmed"
    cmd: str = f"alien_find {remote_data_path}/*o2_ctf*.root"
    skimmed_cmd: str = f"alien_find {skimmed_data_path}/*o2_ctf*.root"
    
    print(f"Querying raw CTFs: {cmd}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        shell=True,
        text=True,
        env=os.environ
    )
    
    ctf_list = [
        "alien://" + p.strip() 
        for p in result.stdout.splitlines() 
        if p.strip().endswith(".root")
    ]

    print(f"Querying skimmed CTFs: {skimmed_cmd}")
    skimmed_result = subprocess.run(
        skimmed_cmd,
        capture_output=True,
        shell=True,
        text=True,
        env=os.environ
    )
    
    skimmed_ctf_list = [
        "alien://" + p.strip() 
        for p in skimmed_result.stdout.splitlines() 
        if p.strip().endswith(".root")
    ]

    print(f"Found {len(skimmed_ctf_list)} skimmed CTFs and {len(ctf_list)} raw CTFs")

    return ctf_list, skimmed_ctf_list

import random

def fetch_ctfs_with_preference(year: str, period: str, run: str, prefer: str = "skimmed", limit: int = 0) -> list[str]:
    """
    Fetches a list of CTFs, preferring either 'skimmed' or 'raw' based on preference.
    Falls back to the other type if the preferred type is not available.
    Optionally limits and randomly samples the resulting list if limit > 0.
    """
    raw_ctfs, skimmed_ctfs = fetch_ctf_list(year, period, run)
    
    ctf_list = []
    
    if prefer == "skimmed":
        if skimmed_ctfs:
            ctf_list = skimmed_ctfs
            print(f"Using skimmed CTFs: found {len(ctf_list)}.")
        elif raw_ctfs:
            ctf_list = raw_ctfs
            print(f"Skimmed CTFs not found. Falling back to {len(ctf_list)} raw CTFs.")
    elif prefer == "raw":
        if raw_ctfs:
            ctf_list = raw_ctfs
            print(f"Using raw CTFs: found {len(ctf_list)}.")
        elif skimmed_ctfs:
            ctf_list = skimmed_ctfs
            print(f"Raw CTFs not found. Falling back to {len(ctf_list)} skimmed CTFs.")
    else:
        raise ValueError("preference must be 'skimmed' or 'raw'")
        
    if not ctf_list:
        print(f"No CTF files found for run {run}.")
        return []
        
    if limit > 0:
        actual_ctf_num = min(limit, len(ctf_list))
        return random.sample(ctf_list, actual_ctf_num)
        
    return ctf_list
