
from deap import gp
from repair.approach.optimization.gplanguage import GP_FUNCTIONS

ROBUSTNESS_FN_MAP = {f.name: f.robustness_fn for f in GP_FUNCTIONS if f.robustness_fn is not None}


# TODO Fix this.some theoretical stuff to do here
# TODO how about multiple fitness values?
# Fitness function: count how many time steps FAIL the requirement
def eval_requirement(individual, traces, variable_names):
    """
    Evaluates the robustness of a requirement represented by a GP individual.

    Returns:
        (robustness,) — lower is better; 0 means satisfied; positive means violated.
    """

    # Sanity check: ensure at least one variable is used in the individual
    # TODO Improve this sanity check
    if not any(var in str(individual) for var in variable_names):
        return (float("inf"),)

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

    def eval_node(node, iterator):
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
            children = [eval_node(next(iterator), iterator) for _ in range(node.arity)]

            # Use robustness function for this primitive
            rob_fn = ROBUSTNESS_FN_MAP.get(node.name)
            if rob_fn is None:
                raise NotImplementedError(f"No robustness function defined for {node.name}")
            return rob_fn(*children)

        else:
            raise TypeError(f"Unexpected node type: {node}")

    iterator = iter(individual)
    root = next(iterator)
    return eval_node(root, iterator)
