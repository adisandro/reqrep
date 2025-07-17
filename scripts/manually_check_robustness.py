from repair.approach.optimization.optimization import OptimizationApproach
from repair.check import Requirement
from repair.trace import TraceSuite
import repair.fitness.correctness as correctness
from deap import gp

ts = TraceSuite("data/dummy")
a1 = OptimizationApproach(ts, None, None) # TODO add transformations? add desirability?

s = "and_(False, lt(0.0, x))"
s = "lt(0.0, x)"
s = "or_(gt(5.0, x), lt(0.0, x))"
s = "or_(True, False)"
s = "eq(add(5.0, 5.125377100590745), x)"
expr = gp.PrimitiveTree.from_string(s, a1.pset)

# Example input
if False:
    sample_input = {'x': 10.0}
    # Call your robustness evaluation function
    robustness = correctness.get_robustness_at_time_i(expr, sample_input)
else:
    robustness = 0.0
    for trace in ts.traces:
        for item in trace.items:
            variable_values = {
                var: float(item.values[var]) for var in a1.variable_names
            }

            rob = correctness.get_robustness_at_time_i(expr, variable_values)
            robustness += max(0.0, rob)  # Only penalize violations

print(f"Requirement: {s}")
print(f"Robustness: {robustness}")
print(f"Robustness type: {type(robustness)}")
# print(f"robustness: {float(robustness)}")
