#!/usr/bin/env python3
from argparse import ArgumentParser

from repair.approach.transformation.transformation import TransformationApproach
from repair.fitness.desirability.applicabilitypreservation import AggregatedRobustnessDifference
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingBasedSanity
from repair.fitness.desirability.syntacticsimilarity import CosineSimilarity
import repair.utils as utils
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.trace import TraceSuite
import time

# Check the REQUIREMENT section for info on how to run it
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
    REQUIREMENTS = {
        # bin/main.py data/dummy x
        "data/dummy": ("True", "lt(x, 1.0)"),
        # bin/main.py data/dummy2 x
        "data/dummy2": ("True", "lt(y, 1.0)"),
        # bin/main.py data/traces xin reset TL BL dT ic
        "data/traces": ("and(eq(reset, 1.0), and(le(BL, ic), le(ic, TL)))", "eq(yout, ic)"),
        # "data/traces": ("True", "and(le(yout, TL), ge(yout, BL))"),
        # bin/main.py data/case_studies/AFC Throttle Engine
        "data/case_studies/AFC": (
            "and(and(ge(Throttle, 0.0), lt(Throttle, 61.2)), and(ge(Engine, 900.0), le(Engine, 1100.0)))",
            "dur(11, 50, lt(Error, 0.007))"
        ),
        # bin/main.py data/case_studies/TUI xin reset TL BL dT ic
        "data/case_studies/TUI": (
            "and(and(ge(xin, 0.0), lt(xin, 1.0)), and(eq(reset, 0.0), and(eq(TL, 10.0), and(eq(BL, -10.0), eq(ic, 0.0)))))",
            "and(le(yout, TL), ge(yout, BL))"
        ),
    }
    req_text = REQUIREMENTS[args.trace_suite]

    # Define DESIRABILITY
    # TODO For now, only semantic and syntactic are implemented, so applicability is set to 0.0
    d = Desirability(
        trace_suite=suite,
        semantic=SamplingBasedSanity(n_samples=10),
        syntactic=CosineSimilarity(),
        applicability=AggregatedRobustnessDifference(), # TODO
        weights=[1.0, 1.0, 0.0]
    )

    # Define APPROACH
    a = OptimizationApproach(suite, req_text, d)
    # a = TransformationApproach(suite, req_text, d)

    # Perform REPAIR
    start_time = time.time()
    repaired_req = a.repair(args.threshold)
    elapsed = time.time() - start_time
    print(a.init_requirement.to_str(suite))
    if repaired_req is not None:
        print(repaired_req.to_str(suite))
    else:
        print("No repair necessary")
    print(f"Repair time: {elapsed:.2f} seconds")
