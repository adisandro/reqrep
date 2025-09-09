#!/usr/bin/env python3
import os
from argparse import ArgumentParser

import pandas as pd

from repair.fitness.desirability.satisfactionextent import TraceSuiteSatisfactionMagnitude, VerticalAndHorizontalExtent
from utils import REQUIREMENTS, INPUT_VARIABLES
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticintegrity import SamplingAndVarTypeSanity
from repair.fitness.desirability.syntacticsimilarity import TreeEditDistance
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
import repair.grammar.utils as grammar_utils
import time

# How to run:

# bin/main.py data/dummy REQ
# bin/main.py data/traces REQ
# bin/main.py data/case_studies/AFC REQ
# bin/main.py data/case_studies/AT AT1
# bin/main.py data/case_studies/AT AT2
# bin/main.py data/case_studies/CC CC1
# bin/main.py data/case_studies/CC CCX
# bin/main.py data/case_studies/EU EU3
# bin/main.py data/case_studies/EU EU8
# bin/main.py data/case_studies/NNP NNP1
# bin/main.py data/case_studies/NNP NNP2
# bin/main.py data/case_studies/TUI REQ

def perform_repair(approach):
    start_time = time.time()
    all_repaired_reqs = approach.repair()
    elapsed = time.time() - start_time

    return all_repaired_reqs, elapsed

if __name__ == "__main__":
    parser = ArgumentParser(description="Repairs test requirements")
    parser.add_argument("trace_suite", help="Path to the directory containing the trace suite")
    parser.add_argument("requirement", help="The name of the requirement to check")
    parser.add_argument("-p", "--prev0", type=float, default=0.0,
                        help="Initial value for the prev() operator at time 0 (defaults to 0.0)")
    parser.add_argument("-i", "--iterations", type=int, default=10,
                        help="The number of iterations the approach tries when repairing, defaults to 10")
    parser.add_argument("-n", "--numbers", type=float, default=1.2,
                        help="When generating numbers, each variable has a window [min, max] based on the values"
                             "seen in the traces; this widens/shrinks the window by a factor, defaults to 1.2")
    parser.add_argument("-a", "--aggregation", default="no_aggregation",
                        help="The aggregation strategy in {no_aggregation, weighted_sum}, defaults to no_aggregation")
    parser.add_argument("-w", "--weights", default="1.0,1.0,1.0",
                        help="The desirability weights, defaults to 1.0,1.0,1.0")
    parser.add_argument("-s", "--suffix", default="", help="An optional output file suffix")
    parser.add_argument("-v", "--verbose", action="store_true", help="Activates logging")
    args = parser.parse_args()
    if args.verbose:
        utils.setup_logger("repair.log")

    # Define TRACE SUITE and REQUIREMENT
    case_study = args.trace_suite.split("/")[-1]
    req_text = REQUIREMENTS[case_study][args.requirement]
    suite = TraceSuite(args.trace_suite, INPUT_VARIABLES[case_study], args.prev0)

    # Define DESIRABILITY
    weights = [float(w) for w in args.weights.split(",")]
    des = Desirability(
        trace_suite=suite,
        semantic=SamplingAndVarTypeSanity(n_samples=10),
        syntactic=TreeEditDistance(),
        satisfaction=VerticalAndHorizontalExtent(),
        weights=weights
    )

    # Define APPROACH and run REPAIR
    a = OptimizationApproach(suite, req_text, args.iterations, args.numbers, des, args.aggregation)
    all_repaired_reqs, elapsed = perform_repair(a)
    # Rank requirements by (1) correctness, (2) semantic desirability, (3) syntactic desirability, (4) satisfaction desirability
    all_repaired_reqs.sort(
        key=lambda r: (r.correctness, r.raw_desirability[0], r.raw_desirability[1], r.raw_desirability[2]))

    # Save results..
    config_id = f"{case_study}_{args.requirement}_{args.aggregation.replace("_", "")}_{round(weights[0])}{round(weights[1])}{round(weights[2])}"
    output_dir = f"output/{config_id}"
    os.makedirs(output_dir, exist_ok=True)

    # ..to file
    #TODO add logger calls + set up without file
    output_path = f"{output_dir}/repair{args.suffix}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Repair time: {elapsed:.2f} seconds\n\n")
        f.write(a.init_requirement.to_str(suite) + "\n\n")
        if all_repaired_reqs is None:
            f.write("No repair necessary")
        else:
            for req in all_repaired_reqs:
                f.write(req.to_str(suite) + "\n\n")
        print(f"Results saved to {output_path}")

    # ..to CSV
    csv_path = f"{output_dir}/results.csv"
    new_rows = []
    for req in all_repaired_reqs:
        pre_infix = grammar_utils.to_infix(req.pre, suite)
        post_infix = grammar_utils.to_infix(req.post, suite)
        raw_desirability = req.raw_desirability
        sem_taut, sem_var_type = des.get_semantic_desirability_components(req)
        sat_vertical, sat_horizontal = des.get_satisfaction_desirability_components(req)
        new_rows.append({
            "config_id": config_id,
            "run_id": args.suffix,
            "time": elapsed,
            "aggregation_strategy": args.aggregation,
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
    pd.DataFrame(new_rows).to_csv(csv_path, mode="w", index=False)
    print(f"Results saved to {csv_path}")
