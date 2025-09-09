# !/usr/bin/env python3
import subprocess
import sys

if __name__ == "__main__":

    # Case Study Specs and runs setup
    case_study_dir = "data/case_studies"
    case_study = "CC"
    requirement = "CC1"
    samples = 10
    processes = 32
    if len(sys.argv) > 1:
        processes = sys.argv[1]
    # NOTE: the desirability dimension implementations are fixed for now
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
    n = 0
    for aggregation, weights in run_configurations:
        for i in range(samples):
            print(f"(Sample {i}) Running configuration: aggregation_strategy={aggregation}, weights={weights}")
            cmd = ["python3", "bin/main.py", f"{case_study_dir}/{case_study}", requirement, "-a", aggregation, "-w",
                   ",".join(str(w) for w in weights), "-s", f"{i}"]
            subprocess.Popen(cmd)
            n += 1
            if n >= processes:
                break #TODO wait for results instead
