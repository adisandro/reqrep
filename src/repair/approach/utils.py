
import random
from deap import gp
from repair.grammar.functions import GRAMMAR_FUNCTIONS

ROBUSTNESS_FN_MAP = {f.name: f.robustness_fn for f in GRAMMAR_FUNCTIONS if f.robustness_fn is not None}

# Sampling-based sanity check
def is_non_trivial_candidate(individual, variable_names: list[str], n_samples: int = 10,) -> bool:
    """
    Returns:
        True → candidate has variable robustness across inputs (not tautology/contradiction)
        False → candidate is tautology or contradiction (robustness constant)
    """
    rob_values = []

    for _ in range(n_samples):
        sample = {var: random.uniform(0, 10) for var in variable_names}
        rob = evaluate_with_robustness(individual, sample)
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


# TODO Fix this.some theoretical stuff to do here
# TODO how about multiple fitness values?
# Fitness function: count how many time steps FAIL the requirement
def eval_requirement(individual, traces, variable_names):
    """
    Evaluates the robustness of a requirement represented by a GP individual.

    Returns:
        (robustness,) — lower is better; 0 means satisfied; positive means violated.
    """
    total_rob = 0.0
    try:
        for trace in traces:
            for item in trace.items:
                variable_values = {
                    var: float(item.values[var]) for var in variable_names
                }

                rob = evaluate_with_robustness(individual, variable_values)
                total_rob += max(0.0, rob)  # Only penalize violations
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {individual} | {e}")

    return (total_rob,)


def evaluate_with_robustness(individual, variable_values: dict[str, float]) -> float:
    """
    Evaluates a DEAP PrimitiveTree individual using robustness semantics.

    Parameters:
        individual: gp.PrimitiveTree — the GP expression to evaluate
        variable_values: dict — mapping from variable names (str) to float values

    Returns:
        float — robustness value (negative = valid, positive = invalid)
    """

    iterator = iter(individual)
    root = next(iterator)
    return eval_node(root, iterator, variable_values)


def eval_node(node, iterator, variable_values: dict[str, float]) -> float:
    if isinstance(node, gp.Terminal):
        # Variable (named terminal)
        if node.value in variable_values:
            
            return variable_values[node.value]

        # Ephemeral constant (e.g., random constant)
        if isinstance(node.value, (float, int)):
            return node.value

        # Something went wrong
        raise ValueError(f"Unrecognized terminal: {node}, name={node.name}, value={node.value}")

    elif isinstance(node, gp.Primitive):
        # Recursively evaluate all children
        children = [eval_node(next(iterator), iterator, variable_values) for _ in range(node.arity)]

        # Use robustness function for this primitive
        rob_fn = ROBUSTNESS_FN_MAP.get(node.name)
        if rob_fn is None:
            raise NotImplementedError(f"No robustness function defined for {node.name}")
        return rob_fn(*children)

    else:
        raise TypeError(f"Unexpected node type: {node}")
