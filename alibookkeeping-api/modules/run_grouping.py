def group_runs(runs: list[dict], full_runs: bool) -> dict:
    grouped_runs = {}
    for run in runs:
        fill_num = None
        lhc_fill = run.get('lhcFill')
        
        if lhc_fill and isinstance(lhc_fill, dict):
            fill_num = lhc_fill.get('fillNumber')
            
        if fill_num is None:
            # Fallback if lhcFill.fillNumber is missing
            fill_num = run.get('fillNumber', 'UNKNOWN')
            
        fill_str = str(fill_num)
        
        if fill_str not in grouped_runs:
            grouped_runs[fill_str] = []
            
        if full_runs:
            grouped_runs[fill_str].append(run)
        else:
            grouped_runs[fill_str].append(run.get('runNumber'))
            
    return grouped_runs
