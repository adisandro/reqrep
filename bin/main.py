#!/usr/bin/env python3
from argparse import ArgumentParser
from operator import eq

from repair.tester import Requirement, Trace, Transformation


def and_(a, b):
    return a and b

def or_(a, b):
    return a or b
if __name__ == "__main__":
    parser = ArgumentParser(description='Repairs test requirements')
    parser.add_argument('traces', help='Path to the directory containing test traces')
    args = parser.parse_args()
    # TODO: calculate percentage of passes before and after
    # TODO: create library of transformations, care about the size of the change
    r1 = Requirement('Req 1', 'BL <= ic <= TL and reset == 0', 'yout == ic')
    r2 = Requirement('Req 2', 'True', 'TL >= yout >= BL')
    t1 = Transformation('Add term', lambda pre: pre + ' or True', lambda post: post + ' or True')
    trace = Trace('traces/TUI_0001.csv')
    trace.parse([r1, r2], [t1])
