#!/usr/bin/env python3

from concurrent.futures import ProcessPoolExecutor, as_completed
from argparse import ArgumentParser

import pandas as pd

from main import create_parser, run

def create_parser_eval():
    parser = ArgumentParser(description="Runs experimental evaluation of ReqRep")
    parser.add_argument("config_list", nargs="*", help="List of configurations to execute (e.g., V1)")
    parser.add_argument("-p", "--processes", default=None,
                        help="Number of processes for parallel computation, "
                             "defaults to the number of processors on the running computer")
    parser.add_argument("-st", "--smoke-test", action="store_true",
                        help="Run a smoke test with minimal configurations")

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
        # original configs
        "V1": ("no_aggregation", [w_sem, w_syn, w_sat], "smt", "default"),
        "V2": ("no_aggregation", [w_sem, w_syn, w_sat], "sampling", "default"),

        # VARIANT: weighted sum
        "V3": ("weighted_sum",   [w_sem, w_syn, w_sat], "smt", "default"),
        "V4": ("weighted_sum",   [w_sem, w_syn, w_sat], "sampling", "default"),

        # [NEWLY ADDED]
        # VARIANT: weighted sum
        "V5": ("no_aggregation", [1.0, 3.0, 5.0], "smt", "default"),

        # VARIANT: hyperparameters
        "V6": ("no_aggregation", [w_sem, w_syn, w_sat], "smt", "hp_increase_tree_depth"),
        "V7": ("no_aggregation", [w_sem, w_syn, w_sat], "smt", "hp_increase_num_offsprings"),

        # Ablation study
        "Abl1": ("no_aggregation", [0.0, w_syn, w_sat], "smt", "default"),
        "Abl2": ("no_aggregation", [w_sem, 0.0, w_sat], "smt", "default"),
        "Abl3": ("no_aggregation", [w_sem, w_syn, 0.0], "smt", "default"),
    }

    # Get list of configuration to run from parser
    parser_eval = create_parser_eval()
    args_eval = parser_eval.parse_args()
    
    if args_eval.smoke_test:
        samples = 2
        case_studies = {"TUI": ["TU1", "TU2"]}

    if not args_eval.config_list:
        # Run complete evaluation on all the possible configurations.
        run_configurations = list(all_configurations.values())
    else:
        # Run only the specified configurations
        run_configurations = [all_configurations[k] for k in args_eval.config_list]
        
    # Get number of processes from parser
    processes = None
    if args_eval.processes:
        processes = int(args_eval.processes)
    
    # Run all configs
    parser_main = create_parser()
    futures = {}
    output_dir = "output"
    csv_filename = "results.csv"
    csv_path = f"{output_dir}/{csv_filename}"
    csv_header = True
    with ProcessPoolExecutor(max_workers=processes) as executor:
        for case_study, requirements in case_studies.items():
            for requirement in requirements:
                for aggregation, weights, tautology_check, approach_config in run_configurations:
                    print(f"Approach Configuration: {weights}")
                    for i in range(samples):
                        cmd = [f"{case_study_dir}/{case_study}",
                               requirement,
                               "-o", output_dir,
                               "-a", aggregation,
                               "-w", ",".join(str(w) for w in weights),
                               "-tc", tautology_check,
                               "-ac", approach_config,
                               "-s", f"{i}"]
                        args_main = parser_main.parse_args(cmd)
                        futures[executor.submit(run, args_main)] = args_main
        for future in as_completed(futures.keys()):
            print(f"Completed: {vars(futures[future])}")
            try:
                res = future.result()
                pd.DataFrame(res).to_csv(csv_path, mode="a", index=False, header=csv_header)
                if csv_header:
                    csv_header = False
            except Exception as e:
                print(f"Error: {e}")

