#!/usr/bin/env python3
from argparse import ArgumentParser

# from repair.approach.approach import OptimizationApproach
from repair.fitness.desirability.applicabilitypreservation import AggregatedRobustnessDifference
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingBasedSanity
from repair.fitness.desirability.syntacticsimilarity import TreeEditDistance
import repair.utils as utils
import repair.grammar.utils as grammar_utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.check import Requirement
from repair.trace import TraceSuite
import time

# run on the dummy data as follows:
# `bin/dummy.py data/dummy`
if __name__ == "__main__":
    parser = ArgumentParser(description='Repairs test requirements')
    parser.add_argument('trace_suite', help='Path to the directory containing the trace suite')
    parser.add_argument('-p', '--prev0', default=0.0,
                        help='Initial value for the prev() operator at time 0 (defaults to 0.0)')
    args = parser.parse_args()
    utils.setup_logger("repair.log")

    # Get Trace Suite
    suite = TraceSuite(args.trace_suite, args.prev0)
    # Define requirement
    r1 = Requirement('True', 'x < 1')
    # Define transformations # TODO not used for now
    # t1 = Transformation('Add true', lambda pre: f'True or ({pre})', lambda post: f'True or ({post})')
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
    a1 = OptimizationApproach(suite, d1, None) # TODO add transformations?

    # Perform Repair
    print(f"Initial Requirement:\n{r1}")
    start_time = time.time()
    repaired_req = a1.repair(r1) # TODO r1 is not supported yet
    elapsed = time.time() - start_time
    print(f"Repaired Requirement: {grammar_utils.to_infix(repaired_req, a1)}")
    print(f"Repaired Requirement: {repaired_req}")
    print(f"Correctness-Robustness: {a1.toolbox.evaluate_cor(repaired_req)}")
    print(f"Desirability: {a1.toolbox.evaluate_des(repaired_req)}")
    print(f"Repair time: {elapsed:.2f} seconds")
