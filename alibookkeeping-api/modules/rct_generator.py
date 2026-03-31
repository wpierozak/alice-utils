import csv

def generate_rct_csv(runs: list[dict], out_csv: str) -> None:
    # Use ';' as a delimiter as expected by run_calibration.py
    with open(out_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        
        headers = ["runNumber", "lhcPeriod", "runQuality", "tags"]
        writer.writerow(headers)
        
        for r in runs:
            run_num = r.get("runNumber", "")
            period = r.get("lhcPeriod", "")
            quality = r.get("runQuality", "")
            
            # Join tag texts with a comma
            tags_list = r.get("tags", [])
            tags_str = ",".join(t.get("text", "") for t in tags_list)
            
            writer.writerow([run_num, period, quality, tags_str])
