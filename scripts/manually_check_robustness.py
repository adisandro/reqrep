from repair.approach.optimization.optimization import OptimizationApproach
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingBasedSanity
from repair.grammar import utils
from repair.trace import TraceSuite
import repair.fitness.correctness as correctness
from deap import gp

# Set up
ts = TraceSuite("data/dummy", 0)
d1 = Desirability(
    trace_suite=ts,
    semantic=None,
    syntactic=None,
    applicability=None
)
a1 = OptimizationApproach(ts, d1, None) # TODO add transformations?

# define requirement
s = "and_(False, lt(0.0, x))"
s = "lt(0.0, x)"
s = "or_(gt(5.0, x), lt(0.0, x))"
s = "or_(True, False)"
s = "eq(add(5.0, 5.125377100590745), x)"
s = "lt(add(0.0, x), add(10.0, x))"
expr = gp.PrimitiveTree.from_string(s, a1.pset)
print(f"Repaired Requirement: {utils.to_infix(expr, a1)}")
print(f"Repaired Requirement: {expr}")

# Compute Robustness

case = "des" # "des" | "rob"
if case == "des":
    sem = SamplingBasedSanity(n_samples=10)
    taut = sem.evaluate(ts, expr)
    print(f"Desirability (semantic): {taut}")
    exit()
elif case == "rob":
    total_rob = 0.0
    try:
        for trace in ts.traces:
            for i, item in enumerate(trace.items):
                rob = correctness.get_robustness_at_time_i(expr, i, item)
                total_rob += max(0.0, rob)  # Only penalize violations
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {expr} | {e}")

    print("Robustness:", total_rob)

# print(f"Requirement: {s}")
# print(f"Robustness: {robustness}")
# print(f"Robustness type: {type(robustness)}")
# # print(f"robustness: {float(robustness)}")
