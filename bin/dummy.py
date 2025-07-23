#!/usr/bin/env python3
from argparse import ArgumentParser

# from repair.approach.approach import OptimizationApproach
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
    parser.add_argument('tracesuite', help='Path to the directory containing the trace suite')
    args = parser.parse_args()
    utils.setup_logger("repair.log")

    # Get Trace Suite
    ts = TraceSuite(args.tracesuite)
    # Define requirement
    r1 = Requirement('True', 'x < 1')
    # Define transformations # TODO not used for now
    # t1 = Transformation('Add true', lambda pre: f'True or ({pre})', lambda post: f'True or ({post})')
    # Define Desirability
    # TODO: Define a fitness functions: desirebleness (e.g. # of trans, semantic from the language as black box)
    # Define Approach
    a1 = OptimizationApproach(ts, None, None) # TODO add transformations? add desirability?

    # Perform Repair
    print(f"Initial Requirement:\n{r1}")
    start_time = time.time()
    repaired_req = a1.repair(r1) # TODO r1 is not supported yet
    elapsed = time.time() - start_time
    print(f"Repaired Requirement: {grammar_utils.to_infix(repaired_req, a1)}")
    print(f"Repaired Requirement: {repaired_req}")
    print(f"Robustness: {a1.toolbox.evaluate(repaired_req)}")
    print(f"Repair time: {elapsed:.2f} seconds")
