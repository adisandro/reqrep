#!/usr/bin/env python3
from argparse import ArgumentParser

from repair.fitness.desirability.satisfactionmagnitude import TraceSuiteSatisfactionMagnitude
from utils import REQUIREMENTS, INPUT_VARIABLES
from repair.approach.transformation.transformation import TransformationApproach
from repair.fitness.desirability.applicabilitypreservation import AvoidAbsoluteSatisfaction
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingAndVarTypeSanity
from repair.fitness.desirability.syntacticsimilarity import TreeEditDistance
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
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
    parser.add_argument("-s", "--suffix", default="", help="An optional output file suffix")
    parser.add_argument("-v", "--verbose", action="store_true", help="Activates logging")
    args = parser.parse_args()
    if args.verbose:
        utils.setup_logger("repair.log")

    # Define TRACE SUITE
    suite = TraceSuite(args.trace_suite, INPUT_VARIABLES[args.trace_suite], args.prev0)

    # Define DESIRABILITY
    d = Desirability(
        trace_suite=suite,
        magnitude=TraceSuiteSatisfactionMagnitude(),
        semantic=SamplingAndVarTypeSanity(n_samples=10),
        syntactic=TreeEditDistance(),
        applicability=AvoidAbsoluteSatisfaction(),
        weights=[100.0, 1.0, 1.0, 1.0]
    )
    # NOTE: ranges for desirability dimensions are (lower is better):
    #       satisfaction magnitude: [0, inf)
    #       semantic sanity: {0, 1}
    #       syntactic similarity: [0, 1]
    #       applicability preservation: {0, 1}

    # Define REQUIREMENT
    req_text = REQUIREMENTS[args.trace_suite][args.requirement]

    # Define APPROACH
    agg_strat = "no_aggregation" # "weighted_sum" or "no_aggregation"
    a = OptimizationApproach(suite, req_text, args.iterations, args.numbers, d, agg_strat)
    # a = TransformationApproach(suite, req_text, args.iterations, args.numbers, d)

    # Perform REPAIR
    start_time = time.time()
    all_repaired_reqs = a.repair()
    elapsed = time.time() - start_time

    # Save stats and print results
    if all_repaired_reqs is None:
        print("No repair necessary")
        exit()
    repaired_req = all_repaired_reqs[0]
    print(a.init_requirement.to_str(suite))
    print(repaired_req.to_str(suite))
    print(f"Repair time: {elapsed:.2f} seconds")

    # Store to file
    output_name = f"output/repair_{args.trace_suite.split("/")[-1]}_{args.requirement}{args.suffix}.txt"
    with open(output_name, "w", encoding="utf-8") as f:
        f.write(f"Repair time: {elapsed:.2f} seconds\n\n")
        for req in all_repaired_reqs:
            f.write(req.to_str(suite) + "\n\n")
