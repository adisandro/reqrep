#!/usr/bin/env python3
from argparse import ArgumentParser
import os

from repair.fitness.desirability.satisfactionextent import VerticalAndHorizontalExtent
from utils import REQUIREMENTS, INPUT_VARIABLES
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticintegrity import SamplingAndVarTypeSanity
from repair.fitness.desirability.syntacticsimilarity import TreeEditDistance
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
import time
import pandas as pd
import repair.grammar.utils as grammar_utils

def perform_repair(approach):

    start_time = time.time()
    all_repaired_reqs = approach.repair()
    elapsed = time.time() - start_time

    # Save stats and print results
    print(approach.init_requirement.to_str(suite))
    if all_repaired_reqs is None:
        print("No repair necessary")
        exit()
    repaired_req = all_repaired_reqs[0]
    print(repaired_req.to_str(suite))
    print(f"Repair time: {elapsed:.2f} seconds")

    return all_repaired_reqs, elapsed

if __name__ == "__main__":
        
    # Case Study Specs
    case_study_dir = "data/case_studies"
    case_study_name = "CC"
    requirement_name="CC1"

    # Eval parameters
    # search = standard #TODO
    prev0=0.0
    num_loop_iterations=10
    numbers=1.2
    verbose=False
    num_repetitions = 10

    # Other parameters
    if verbose:
        utils.setup_logger("repair.log")

    # Fixed inputs
    trace_suite_path = f"{case_study_dir}/{case_study_name}"
    suite = TraceSuite(trace_suite_path, INPUT_VARIABLES[trace_suite_path], prev0)
    req_text = REQUIREMENTS[trace_suite_path][requirement_name]

    # output paths    
    output_folder = f"output/repair_{case_study_name}_{requirement_name}"
    os.makedirs(output_folder, exist_ok=True)

    # Runs setup
    # NOTE: the desirability dimension implementations are fixed for now
    w_sem = 1.0
    w_syn = 1.0
    w_sat = 1.0
    run_configurations = [
        ("no_aggregation", [w_sem, w_syn, w_sat]),
        ("no_aggregation", [0.0, w_syn, w_sat]),
        ("no_aggregation", [w_sem, 0.0, w_sat]),
        ("no_aggregation", [w_sem, w_syn, 0.0]),
        ("weighted_sum", [w_sem, w_syn, w_sat]) # would be nice, if we have time
    ]

    # Prepare CSV (create header once if file does not exist)
    # Overwrite the file
    csv_path = f"{output_folder}/results.csv"
    pd.DataFrame(columns=["config_id",
                          "run_id",
                          "time",
                          "aggregation_strategy",
                          "weights",
                          "precondition",
                          "postcondition",
                          "f_correctness",
                          "f_des_semantic",
                          "f_des_syntactic",
                          "f_des_satisfaction",
                          "f_des_weighted",
                          "f_sem_taut",
                          "f_sem_var_type",
                          "f_sat_vertical",
                          "f_sat_horizontal"]).to_csv(csv_path, index=False)

    # ---- Run all configurations ----
    for config_id, (aggregation_strategy, weights) in enumerate(run_configurations):
        for i in range(num_repetitions):
            print(f"(Run {i}) Running configuration: aggregation_strategy={aggregation_strategy}, weights={weights}")
            des = Desirability(
                trace_suite=suite,
                semantic=SamplingAndVarTypeSanity(n_samples=10),
                syntactic=TreeEditDistance(),
                satisfaction=VerticalAndHorizontalExtent(),
                weights=weights
            )
            approach = OptimizationApproach(suite, req_text, num_loop_iterations, numbers, des, aggregation_strategy)
            all_repaired_reqs, elapsed = perform_repair(approach)

            #Rank requirements by (1) correctness, (2) semantic desirability, (3) syntactic desirability, (4) satisfaction desirability
            all_repaired_reqs.sort(key=lambda r: (r.correctness, r.raw_desirability[0], r.raw_desirability[1], r.raw_desirability[2]))

            # ---- Save to file ----
            rounded_weights = [round(w) for w in weights]
            save_file_path = f"{output_folder}/{aggregation_strategy}_w{rounded_weights[0]}_{rounded_weights[1]}_{rounded_weights[2]}/run{i}.txt"
            os.makedirs(os.path.dirname(save_file_path), exist_ok=True)

            with open(save_file_path, "w", encoding="utf-8") as f:
                f.write(f"Repair time: {elapsed:.2f} seconds\n\n")
                f.write(approach.init_requirement.to_str(suite) + "\n\n")
                for req in all_repaired_reqs:
                    f.write(req.to_str(suite) + "\n\n")
            print(f"Results saved to {save_file_path}")


            # ---- Save to CSV ----
            new_rows = []
            for req in all_repaired_reqs:
                pre_infix = grammar_utils.to_infix(req.pre, suite)
                post_infix = grammar_utils.to_infix(req.post, suite)

                # Get desirabilities
                raw_desirability = req.raw_desirability
                sem_taut, sem_var_type = des.get_semantic_desirability_components(req)
                sat_vertical, sat_horizontal = des.get_satisfaction_desirability_components(req)

                new_rows.append({
                    "config_id": config_id,
                    "run_id": i,
                    "time": elapsed,
                    "aggregation_strategy": aggregation_strategy,
                    "weights": str(weights),
                    "precondition": pre_infix,
                    "postcondition": post_infix,
                    "f_correctness": req.correctness,
                    "f_des_semantic": raw_desirability[0],
                    "f_des_syntactic": raw_desirability[1],
                    "f_des_satisfaction": raw_desirability[2],
                    "f_des_weighted": req.desirability['des'],
                    "f_sem_taut": sem_taut,
                    "f_sem_var_type": sem_var_type,
                    "f_sat_vertical": sat_vertical,
                    "f_sat_horizontal": sat_horizontal,
                })
            pd.DataFrame(new_rows).to_csv(csv_path, mode="a", index=False, header=False)
            print(f"Results appended to {csv_path}")

