#!/usr/bin/env python3
import argparse
import random
import time
import pathlib
import sys
from pathlib import Path

# Add the parent directory to sys.path to resolve 'modules'
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pyslurm

from modules.calibration_utils import (
    GracefulKiller, RCTFields, get_list_of_runs, copy_scripts_to_workdir,
    load_status, save_status, update_active_jobs_list
)
from modules.ctf_utils import fetch_ctf_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scans queue directory for raw data and triggers CTF production")
    parser.add_argument("--year", help="Year", required=True)
    parser.add_argument("--period", help="LHC period", required=True)
    parser.add_argument("--rct", help="Path to RCT table in CSV format", required=True)
    parser.add_argument("--ctf-num", help="Number of CTF files to process", required=True)
    parser.add_argument("--scripts-path", help="Path to job scripts", required=True)
    parser.add_argument("--limit", type=int, default=0, help="Limit number of jobs to submit (0 for no limit)")
    parser.add_argument("--work-dir", default=".", help="Directory to create workdirs")
    parser.add_argument("--status-file", help="Path to the status tracking file", default="job_status.csv")
    parser.add_argument("--sleep", default=1)
    args = parser.parse_args()

    year: str = args.year
    period: str = args.period
    rct: str = args.rct
    ctf_num: int = int(args.ctf_num)
    script_source = pathlib.Path(args.scripts_path)
    limit: int = args.limit
    work_dir: str = args.work_dir
    status_file_path = pathlib.Path(args.status_file)
    sleep_time: float = float(args.sleep)

    # Load existing progress
    run_status: dict[str, dict] = load_status(status_file_path)
    runs = get_list_of_runs(rct)
    ctf_list_files = {}
    submitted_count = 0
    active_jobs_id = []
    
    for status in run_status.values():
        if status["job_id"] != "":
            active_jobs_id.append(status["job_id"])

    killer = GracefulKiller()

    for run in runs:
        if killer.kill_now:
            print(f"Program was terminated")
            break

        active_jobs_id = update_active_jobs_list(active_jobs_id)
        while limit > 0 and len(active_jobs_id) >= limit:
            if killer.kill_now:
                break
            print(f"Reached limit of {limit} active jobs. Waiting {sleep_time}s...")
            time.sleep(sleep_time)
            active_jobs_id = update_active_jobs_list(active_jobs_id)

        current_data = run_status.get(run, {})
        current_state = current_data.get("status", "")
        if current_state == "submitted":
            print(f"Run {run} already submitted (Job ID: {current_data.get('job_id', 'unknown')}). Skipping.")
            continue

        print(f"Processing run {run} (Status: {current_state or 'new'})...")
        
        # New split tuple from modules/ctf_utils.py:
        ctf_list_raw, skimmed_ctf_list = fetch_ctf_list(year, period, run)
        
        print(f"Get {len(skimmed_ctf_list)} skimmed")
        if len(skimmed_ctf_list) != 0:
            ctf_list = skimmed_ctf_list
        else:
            ctf_list = ctf_list_raw
        
        if not ctf_list:
            print(f"No CTF files found for run {run}. Skipping.")
            continue
        
        actual_ctf_num = min(ctf_num, len(ctf_list))
        sampled_ctfs = random.sample(ctf_list, actual_ctf_num)
        
        workdir = pathlib.Path(work_dir) / f"{year}_{period}_{run}"
        workdir.mkdir(parents=True, exist_ok=True) 
        
        ctf_list_file = workdir / "ctfs.lst"
        ctf_list_files[run] = ctf_list_file

        with open(ctf_list_file, "w") as file:
            file.write("\n".join(sampled_ctfs) + "\n")

        copy_scripts_to_workdir(script_source, workdir)
        slurm_script_path = workdir / "generate-objects.slurm"
        
        try:
            with open(slurm_script_path, "r") as slurm_file:
                script_content = slurm_file.read()
            
            job_desc = pyslurm.JobSubmitDescription(
                name=f"events-per-bc-{year}-{period}-{run}",
                script=str(slurm_script_path.absolute()),
                working_directory=str(workdir.absolute())
            )
            
            job_id = job_desc.submit()
            print(f"Successfully submitted run {run}. Job ID: {job_id}")
            
            # Update status with job ID and increment counter
            run_status[run] = {
                "status": "submitted", 
                "job_id": str(job_id)
            }

            active_jobs_id.append(job_id)
            submitted_count += 1
            save_status(status_file_path, run_status)

        except Exception as e:
            print(f"Failed to submit run {run} via pyslurm: {e}")
        
    print(f"Done. Total jobs submitted this session: {submitted_count}")
