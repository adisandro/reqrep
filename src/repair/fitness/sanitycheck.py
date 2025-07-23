
import random

from repair.fitness.correctness import get_robustness_at_time_i

# Sampling-based sanity check
def is_non_trivial_candidate(individual, variable_names: list[str], n_samples: int = 10,) -> bool:
    """
    Returns:
        True → candidate has variable robustness across inputs (not tautology/contradiction)
        False → candidate is tautology or contradiction (robustness constant)
    """
    rob_values = []

    for _ in range(n_samples):
        # TODO: Change sample to be a TraceItem, with a random i, and what about traces?
        sample = {var: random.uniform(0, 10) for var in variable_names}
        rob = get_robustness_at_time_i(individual, sample)
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
    # is_trivial = all_same
    return not all_same