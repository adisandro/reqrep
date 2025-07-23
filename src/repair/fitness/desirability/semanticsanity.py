
import random
from repair.fitness.desirability.desirability import SemanticSanity

from repair.fitness.correctness import get_robustness_at_time_i


class SamplingBasedSanity(SemanticSanity):

    def __init__(self, traces, n_samples: int = 10):
        super().__init__()
        self.traces = traces
        self.n_samples = n_samples

    def evaluate(self, individual) -> float:
        """
        Returns:
            0.0 → candidate has variable robustness across inputs (not tautology/contradiction)
            1.0 → candidate is tautology or contradiction (robustness constant)
        """
        rob_values = []

        for _ in range(self.n_samples):

            trace = random.choice(self.traces)
            if len(trace.items) < 2:
                continue  # skip traces that are too short
            i = random.randint(1, len(trace.items) - 1)
            item = trace.items[i]

            rob = get_robustness_at_time_i(individual, i, item, trace)
            # sample_item = {var: random.uniform(*sample_range) for var in variable_names}

            # sample = {var: random.uniform(*sample_range) for var in variable_names}
            # rob = get_robustness_at_time_i(individual, sample)
            if not isinstance(rob, (float, int)):
                if isinstance(rob, bool):
                    # if robustness is boolean, it is trivial
                    return False
                raise TypeError(f"Robustness value must be a float or int, got {type(rob)}")
            rob_values.append(rob)

        first_rob = rob_values[0]
        all_same = all(rob == first_rob for rob in rob_values)

        # If all robustness values are the same,
        # it's (likely) trivial, i.e. a constant function (tautology/contradiction)
        return 1.0 if all_same else 0.0


class SymbolicSanity(SemanticSanity):
    def evaluate(self, individual) -> float:
        pass  # to be implemented

