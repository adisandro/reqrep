#!/usr/bin/env python3
import os
from argparse import ArgumentParser
from operator import eq

from repair.check import Requirement, Transformation
from repair.trace import Trace

if __name__ == "__main__":
    parser = ArgumentParser(description='Repairs test requirements')
    parser.add_argument('traces', help='Path to the directory containing test traces')
    args = parser.parse_args()
    # TODO: Metrics: correctness (% of time, distance from desired value) + desirableness?
    # TODO: Loop to find the right repair (e.g. passing threshold % of rows)
    r1 = Requirement('Req 1', 'BL <= ic <= TL and reset == 0', 'yout == ic')
    r2 = Requirement('Req 2', 'True', 'TL >= yout >= BL')
    # TODO: Are pre/post transformations bundled together, or are they independent?
    t1 = Transformation('Add true', lambda pre: f'True or ({pre})', lambda post: f'True or ({post})')
    with os.scandir(args.traces) as it:
        for entry in it:
            if entry.is_dir() or not entry.name.endswith('.csv'):
                continue
            trace = Trace(entry.path)
            trace.parse()
            trace.evaluate([r1, r2], [t1])
            print(trace)
