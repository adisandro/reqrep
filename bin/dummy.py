#!/usr/bin/env python3
import os
from argparse import ArgumentParser

# from repair.approach.approach import OptimizationApproach
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.check import Requirement, Transformation
from repair.trace import Trace, TraceSuite
from repair.approach.optimization import utils as optimization_utils
import time


if __name__ == "__main__":
    parser = ArgumentParser(description='Repairs test requirements')
    parser.add_argument('tracesuite', help='Path to the directory containing the trace suite')
    args = parser.parse_args()

    utils.setup_logger("repair.log")

    # TODO list from Alessio
    # TODO: Support concatenation of transformations
    # TODO: Pre/post transformations are independent
    # TODO: Create a framework with the budget loop and optimization algorithm, vs a random baseline
    # TODO: Add to Github

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
    print(f"Initial Requirement: {r1}")
    start_time = time.time()
    repaired_req = a1.repair(r1) # TODO r1 is not supported yet
    elapsed = time.time() - start_time
    print(f"Repaired Requirement: {optimization_utils.to_infix(repaired_req, a1)}")
    print(f"Repair time: {elapsed:.2f} seconds")

# run on the dummy data as follows:
# `python bin/dummy.py data/dummy`

