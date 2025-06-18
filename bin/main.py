#!/usr/bin/env python3
from argparse import ArgumentParser

from repair.tester import Requirement, Trace

if __name__ == "__main__":
    parser = ArgumentParser(description='Repairs test requirements')
    parser.add_argument('traces', help='Path to the directory containing test traces')
    args = parser.parse_args()
    # TODO: modify both, calculate percentage of passes before and after
    # TODO: create library of transformations, care about the size of the change
    req1 = Requirement('Req 1', lambda v: v['BL'] <= v['ic'] <= v['TL'] and v['reset'] == 0,
                       lambda v: v['yout'] == v['ic'])
    req2 = Requirement('Req 2', lambda v: True, lambda v: v['TL'] >= v['yout'] >= v['BL'])
    trace = Trace('traces/TUI_0001.csv')
    trace.parse([req1, req2])
