
import math
import random
from repair.fitness.desirability.desirability import SemanticSanity

from repair.fitness.correctness import eval_tree


class SamplingBasedSanity(SemanticSanity):

    def __init__(self, n_samples: int = 10):
        super().__init__()
        self.n_samples = n_samples

    def evaluate(self, trace_suite, individual) -> float:
        """
        Returns:
            0.0 → candidate has variable robustness across inputs (not tautology/contradiction)
            1.0 → candidate is tautology or contradiction (robustness constant)
        """
        rob_values = []

        for _ in range(self.n_samples):
            trace = random.choice(trace_suite.traces)
            if len(trace.items) < 2:
                continue  # skip traces that are too short
            i = random.randint(1, len(trace.items) - 1)
            item = trace.items[i]
            rob = eval_tree(individual, i, item)
            if not isinstance(rob, (float, int)):
                raise TypeError(f"Robustness value must be a float or int, got {type(rob)}")
            rob_values.append(rob)

        def all_close(arr, tol=1e-6):
            return all(math.isclose(x, arr[0], abs_tol=tol) for x in arr)
        all_same = all_close(rob_values)

        # If all robustness values are the same,
        # it's (likely) trivial, i.e. a constant function (tautology/contradiction)
        return 1.0 if all_same else 0.0


class SymbolicSanity(SemanticSanity):
    def evaluate(self, trace_suite, individual) -> float:
        pass  # to be implemented

