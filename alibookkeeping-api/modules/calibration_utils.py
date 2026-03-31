import csv
import shutil
import pathlib
import pyslurm
import signal
from enum import Enum

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True

class RCTFields(Enum):
    runNumber = "runNumber"

def get_list_of_runs(rct: str) -> list[str]:
    runs: list[str] = []
    with open(rct, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            runs.append(row[RCTFields.runNumber.value])
    return runs

def copy_scripts_to_workdir(scripts_dir: pathlib.Path, dest: pathlib.Path):
    for item in scripts_dir.iterdir():
        if item.is_file():
            shutil.copy(item, dest)

def load_status(file_path: pathlib.Path) -> dict[str, dict]:
    """Loads run status from a CSV file (run_number, status, job_id)."""
    status_map = {}
    if file_path.exists():
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    run_id = row[0]
                    status = row[1]
                    job_id = row[2] if len(row) > 2 else ""
                    status_map[run_id] = {"status": status, "job_id": job_id}
    return status_map

def save_status(file_path: pathlib.Path, status_map: dict[str, dict]):
    """Saves the updated status map (including job_id) to the CSV file."""
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for run, data in status_map.items():
            writer.writerow([run, data["status"], data.get("job_id", "")])

def update_active_jobs_list(active_jobs: list) -> list:
    """
    Checks Slurm for active jobs and filters the tracking list.
    Only keeps job IDs that are still reported by Slurm.
    """
    jobs = pyslurm.Jobs.load()
    active_states = {'PENDING', 'RUNNING', 'SUSPENDED', 'COMPLETING', 'CONFIGURING'}
    return [job.job_id for job in active_jobs.values() if (int(job.job_id) in jobs and job.state in active_states)]
