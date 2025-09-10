#!/usr/bin/env python3
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from main import create_parser, run

if __name__ == "__main__":
    # Case study setup
    processes = None
    if len(sys.argv) > 1:
        processes = int(sys.argv[1])
    samples = 10
    case_study_dir = "data/case_studies"
    case_studies = {"AFC": ["AFC29", "AFC33"], "AT": ["AT1", "AT2"], "CC": ["CC1", "CCX"], "EU": ["EU3"],
                    "NNP": ["NNP3a", "NNP3b", "NNP4"], "TUI": ["TU1", "TU2"]}
    w_sem = 1.0
    w_syn = 1.0
    w_sat = 1.0
    run_configurations = [
        ("no_aggregation", [w_sem, w_syn, w_sat]),
        ("no_aggregation", [0.0, w_syn, w_sat]),
        ("no_aggregation", [w_sem, 0.0, w_sat]),
        ("no_aggregation", [w_sem, w_syn, 0.0]),
        ("weighted_sum",   [w_sem, w_syn, w_sat])
    ]

    # Run all configs
    parser = create_parser()
    futures = {}
    stats = []
    with ProcessPoolExecutor(max_workers=processes) as executor:
        for case_study, requirements in case_studies.items():
            for requirement in requirements:
                for aggregation, weights in run_configurations:
                    for i in range(samples):
                        cmd = [f"{case_study_dir}/{case_study}", requirement, "-a", aggregation, "-w",
                               ",".join(str(w) for w in weights), "-s", f"{i}"]
                        args = parser.parse_args(cmd)
                        futures[executor.submit(run, args)] = args
        for future in as_completed(futures.keys()):
            print(f"Completed: {vars(futures[future])}")
            stats.extend(future.result())
    csv_path = f"output/results.csv"
    pd.DataFrame(stats).to_csv(csv_path, mode="w", index=False)

