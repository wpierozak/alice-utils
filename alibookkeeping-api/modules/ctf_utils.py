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
