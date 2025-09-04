#!/usr/bin/env python3
from argparse import ArgumentParser

from repair.fitness.desirability.satisfactionmagnitude import TraceSuiteSatisfactionMagnitude
from utils import REQUIREMENTS
from repair.approach.transformation.transformation import TransformationApproach
from repair.fitness.desirability.applicabilitypreservation import PreconditionSatisfaction
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingAndVarTypeSanity, SamplingBasedSanity
from repair.fitness.desirability.syntacticsimilarity import CosineSimilarity, TreeEditDistance
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
import time

# How to run:

# bin/main.py data/dummy x
# bin/main.py data/traces xin reset TL BL dT ic
# bin/main.py data/case_studies/AFC Throttle Engine
# bin/main.py data/case_studies/AT Throttle Brake
# bin/main.py data/case_studies/CC Throttle Brake
# bin/main.py data/case_studies/EU Phi Theta Psi Vin_x Vin_y Vin_z
# bin/main.py data/case_studies/NNP xIn yIn
# bin/main.py data/case_studies/TUI xin reset TL BL dT ic

if __name__ == "__main__":
    parser = ArgumentParser(description="Repairs test requirements")
    parser.add_argument("trace_suite", help="Path to the directory containing the trace suite")
    parser.add_argument("input_vars", nargs="+", help="The names of the input variables, space separated")
    parser.add_argument("-p", "--prev0", type=float, default=0.0,
                        help="Initial value for the prev() operator at time 0 (defaults to 0.0)")
    parser.add_argument("-i", "--iterations", type=int, default=10,
                        help="The number of iterations the approach tries when repairing, defaults to 10")
    args = parser.parse_args()
    utils.setup_logger("repair.log")

    # Define TRACE SUITE
    suite = TraceSuite(args.trace_suite, set(args.input_vars), args.prev0)

    # Define REQUIREMENT
    req_text = REQUIREMENTS[args.trace_suite]

    # Define DESIRABILITY
    d = Desirability(
        trace_suite=suite,
        magnitude=TraceSuiteSatisfactionMagnitude(),
        semantic=SamplingAndVarTypeSanity(n_samples=10),
        syntactic=TreeEditDistance(),
        applicability=PreconditionSatisfaction(),
        weights=[1.0, 20.0, 1.0, 1.0]
    )

    # Define APPROACH
    a = OptimizationApproach(suite, req_text, args.iterations, d)
    # a = TransformationApproach(suite, req_text, args.iterations, d)

    # Perform REPAIR
    start_time = time.time()
    repaired_req = a.repair()
    elapsed = time.time() - start_time
    print(a.init_requirement.to_str(suite))
    if repaired_req is not None:
        print(repaired_req.to_str(suite))
    else:
        print("No repair necessary")
    print(f"Repair time: {elapsed:.2f} seconds")
