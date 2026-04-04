#!/usr/bin/env python3

from concurrent.futures import ProcessPoolExecutor, as_completed
from argparse import ArgumentParser

import pandas as pd

from main import create_parser, run

def create_parser_eval():
    parser = ArgumentParser(description="List of configurations to execute")
    parser.add_argument("configList", nargs="*", help="List of configurations to execute (e.g., V1)")
    parser.add_argument("-p", "--process", default=None, help="Number of processes for parallel computation")

    return parser

if __name__ == "__main__":
    # Case study setup
    samples = 10
    case_study_dir = "data/case_studies"
    case_studies = {"AFC": ["AFC29", "AFC33"], "AT": ["AT1", "AT2"], "CC": ["CC1", "CCX"], "EU": ["EU3"],
                    "NNP": ["NNP3a", "NNP3b", "NNP4"], "TUI": ["TU1", "TU2"]}
    w_sem = 1.0
    w_syn = 1.0
    w_sat = 1.0
    all_configurations = {
        # ToDo: Missing configurations V2 and V4.
        # original configs
        "V1": ("no_aggregation", [w_sem, w_syn, w_sat], "default"),

        # VARIANT: weighted sum
        "V3": ("weighted_sum",   [w_sem, w_syn, w_sat], "default"),

        # [NEWLY ADDED]
        # VARIANT: weighted sum
        "V5": ("no_aggregation", [1.0, 3.0, 5.0], "default"),

        # VARIANT: hyperparameters
        "V6": ("no_aggregation", [w_sem, w_syn, w_sat], "hp_increase_tree_depth"),
        "V7": ("no_aggregation", [w_sem, w_syn, w_sat], "hp_increase_num_offsprings"),

        # Ablation study
        "Abl1": ("no_aggregation", [0.0, w_syn, w_sat], "default"),
        "Abl2": ("no_aggregation", [w_sem, 0.0, w_sat], "default"),
        "Abl3": ("no_aggregation", [w_sem, w_syn, 0.0], "default"),
    }

    # Get list of configuration to run from parser
    parserConfig = create_parser_eval()
    argsConfig = parserConfig.parse_args()
    if not argsConfig.configList:
        # Run complete evaluation on all the possible configurations.
        run_configurations = list(all_configurations.values())
    else:
        # Run only the specified configurations
        run_configurations = [all_configurations[k] for k in argsConfig.configList]
        
    # Get number of processes from parser
    processes = None
    if argsConfig.process:
        processes = int(argsConfig.process)
    
    # Run all configs
    parserRun = create_parser()
    futures = {}
    output_dir = "output"
    csv_filename = "results.csv"
    csv_path = f"{output_dir}/{csv_filename}"
    csv_header = True
    with ProcessPoolExecutor(max_workers=processes) as executor:
        for case_study, requirements in case_studies.items():
            for requirement in requirements:
                for aggregation, weights, approach_config in run_configurations:
                    print(f"Approach Configuration: {weights}")
                    for i in range(samples):
                        cmd = [f"{case_study_dir}/{case_study}",
                               requirement,
                               "-o", output_dir,
                               "-a", aggregation,
                               "-w", ",".join(str(w) for w in weights),
                               "-ac", approach_config,
                               "-s", f"{i}"]
                        argsRun = parserRun.parse_args(cmd)
                        futures[executor.submit(run, argsRun)] = argsRun
        for future in as_completed(futures.keys()):
            print(f"Completed: {vars(futures[future])}")
            try:
                res = future.result()
                pd.DataFrame(res).to_csv(csv_path, mode="a", index=False, header=csv_header)
                if csv_header:
                    csv_header = False
            except Exception as e:
                print(f"Error: {e}")

