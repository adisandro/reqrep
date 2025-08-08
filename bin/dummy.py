#!/usr/bin/env python3
from argparse import ArgumentParser

# from repair.approach.approach import OptimizationApproach
from repair.fitness.desirability.applicabilitypreservation import AggregatedRobustnessDifference
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingBasedSanity
from repair.fitness.desirability.syntacticsimilarity import TreeEditDistance
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
import time

# run on the dummy data as follows:
# `bin/dummy.py data/dummy`
if __name__ == "__main__":
    parser = ArgumentParser(description="Repairs test requirements")
    parser.add_argument("trace_suite", help="Path to the directory containing the trace suite")
    parser.add_argument("-p", "--prev0", type=float, default=0.0,
                        help="Initial value for the prev() operator at time 0 (defaults to 0.0)")
    args = parser.parse_args()
    utils.setup_logger("repair.log")

    # Get Trace Suite
    suite = TraceSuite(args.trace_suite, {"x"}, args.prev0)
    # Define requirement
    req = ("True", "lt(x, 1.0)")
    # Define Desirability
    # TODO For now, only semantic is implemented, so syntactic and applicability are set to 0.0
    d1 = Desirability(
        trace_suite=suite,
        semantic=SamplingBasedSanity(n_samples=10),
        syntactic=TreeEditDistance(), # TODO
        applicability=AggregatedRobustnessDifference(), # TODO
        weights=[1.0, 0.0, 0.0]
    )
    # Define Approach
    a1 = OptimizationApproach(suite, req, d1)

    # Perform Repair
    start_time = time.time()
    repaired_req = a1.repair()
    elapsed = time.time() - start_time
    print(a1.pre_cond)
    print(a1.post_cond)
    print(repaired_req)
    print(f"Repair time: {elapsed:.2f} seconds")
