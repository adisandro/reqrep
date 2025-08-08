
import math
import random
from statistics import correlation

from repair.fitness.desirability.desirability import SemanticSanity

from repair.fitness.correctness import eval_tree, is_within_margin


class SamplingBasedSanity(SemanticSanity):

    def __init__(self, n_samples: int = 10):
        super().__init__()
        self.n_samples = n_samples

    def evaluate(self, trace_suite, individual) -> float:
        """
        Returns:
            0.0 → candidate has variable correctness across inputs (not tautology/contradiction)
            1.0 → candidate is tautology or contradiction (correctness constant)
        """
        all_same = True
        base_cor = None

        for _ in range(self.n_samples):
            trace = random.choice(trace_suite.traces)
            if len(trace.items) < 2:
                continue  # skip traces that are too short
            i = random.randint(1, len(trace.items) - 1)
            item = trace.items[i]
            cor = eval_tree(individual, i, item)
            if base_cor is None:
                base_cor = cor
            elif not is_within_margin(cor, base_cor):
                all_same = False
                break

        # If all robustness values are the same,
        # it's (likely) trivial, i.e. a constant function (tautology/contradiction)
        return 1.0 if all_same else 0.0


class SymbolicSanity(SemanticSanity):
    def evaluate(self, trace_suite, individual) -> float:
        pass  # to be implemented

