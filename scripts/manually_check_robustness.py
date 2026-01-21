from repair.approach.optimization.optimization import OptimizationApproach
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticintegrity import SamplingBasedTautologyCheck
from repair.grammar import utils
from repair.approach.trace import TraceSuite
import repair.fitness.correctness.correctness as correctness
from deap import gp

# Set up
ts = TraceSuite("data/dummy", {"x"}, 0)
d1 = Desirability(
    trace_suite=ts,
    semantic=None,
    syntactic=None,
    applicability=None
)
a1 = OptimizationApproach(ts, ("True", "True"), d1)

# define requirement
s = "and_(False, lt(0.0, x))"
s = "lt(0.0, x)"
s = "or_(gt(5.0, x), lt(0.0, x))"
s = "or_(True, False)"
s = "eq(add(5.0, 5.125377100590745), x)"
s = "lt(add(0.0, x), add(10.0, x))"
expr = gp.PrimitiveTree.from_string(s, a1.req.pre.pset)
print(f"Repaired Requirement: {utils.to_infix(expr)}")
print(f"Repaired Requirement: {expr}")

# Compute Robustness

case = "des" # "des" | "cor"
if case == "des":
    sem = SamplingBasedTautologyCheck(n_samples=10)
    taut = sem.evaluate(ts, expr)
    print(f"Desirability (semantic): {taut}")
    exit()
elif case == "cor":
    total_cor = 0.0
    try:
        for trace in ts.traces:
            for i, item in enumerate(trace.items):
                cor = correctness.eval_tree(expr, i, item)
                total_cor += max(0.0, cor)  # Only penalize violations
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {expr} | {e}")

    print("Robustness:", total_cor)

# print(f"Requirement: {s}")
# print(f"Robustness: {robustness}")
# print(f"Robustness type: {type(robustness)}")
# # print(f"robustness: {float(robustness)}")
