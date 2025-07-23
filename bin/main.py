#!/usr/bin/env python3
from argparse import ArgumentParser

from repair.check import Requirement, Transformation
from repair.trace import TraceSuite

if __name__ == "__main__":
    parser = ArgumentParser(description='Repairs test requirements')
    parser.add_argument('traceSuite', help='Path to the directory containing the trace suite')
    args = parser.parse_args()
    # TODO: Define a fitness functions: desirebleness (e.g. # of trans, semantic from the language as black box)
    # TODO: Support concatenation of transformations
    # TODO: Pre/post transformations are independent
    # TODO: Create a framework with the budget loop and optimization algorithm, vs a random baseline
    r1 = Requirement('BL <= ic <= TL and reset == 0', 'yout == ic')
    r2 = Requirement('True', 'TL >= yout >= BL')
    t1 = Transformation('Add true', lambda pre: f'True or ({pre})', lambda post: f'True or ({post})')
    ts = TraceSuite(args.traceSuite)
    r1.repair(ts, [t1])
    r2.repair(ts, [t1])

