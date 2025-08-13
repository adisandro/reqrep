#!/usr/bin/env python3
from argparse import ArgumentParser

from repair.fitness.desirability.applicabilitypreservation import AggregatedRobustnessDifference
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingBasedSanity
from repair.fitness.desirability.syntacticsimilarity import CosineSimilarity
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
import time

# run on the dummy data as follows:
# `bin/dummy.py data/dummy`
if __name__ == "__main__":
    parser = ArgumentParser(description="Repairs test requirements")
    parser.add_argument("trace_suite", help="Path to the directory containing the trace suite")
    parser.add_argument("input_vars", nargs="+", help="The names of the input variables, space separated")
    parser.add_argument("-p", "--prev0", type=float, default=0.0,
                        help="Initial value for the prev() operator at time 0 (defaults to 0.0)")
    parser.add_argument("-t", "--threshold", type=float, default=100.0,
                        help="Requirement repair threshold: repair if correctness % < threshold (defaults to 100)")
    args = parser.parse_args()
    utils.setup_logger("repair.log")

    # Define TRACE SUITE
    suite = TraceSuite(args.trace_suite, set(args.input_vars), args.prev0)

    # Define REQUIREMENT
    req = ("True", "lt(x, 1.0)")
    req = ("True", "lt(y, 1.0)")
    # req = ("and(eq(reset, 1.0), and(le(BL, ic), le(ic, TL)))", "eq(yout, ic)")
    # req = ("True", "and(le(yout, TL), ge(yout, BL))")

    # Define DESIRABILITY
    # TODO For now, only semantic is implemented, so syntactic and applicability are set to 0.0
    d = Desirability(
        trace_suite=suite,
        semantic=SamplingBasedSanity(n_samples=10),
        syntactic=CosineSimilarity(), # TODO
        applicability=AggregatedRobustnessDifference(), # TODO
        weights=[1.0, 0.0, 0.0]
    )

    # Define APPROACH
    a = OptimizationApproach(suite, req, d)

    # Perform REPAIR
    start_time = time.time()
    repaired_req = a.repair(args.threshold)
    elapsed = time.time() - start_time
    print(a.init_requirement.pre)
    print("No repair necessary\n" if repaired_req.pre is None else repaired_req.pre)
    print(a.init_requirement.post)
    print("No repair necessary\n" if repaired_req.post is None else repaired_req.post)
    print(f"Repair time: {elapsed:.2f} seconds")
