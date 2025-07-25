from deap import gp
from repair.grammar.functions import GRAMMAR_FUNCTIONS

ROBUSTNESS_FN_MAP = {f.name: f.robustness_fn for f in GRAMMAR_FUNCTIONS if f.robustness_fn is not None}

# TODO Fix this.some theoretical stuff to do here
# TODO how about multiple fitness values?
# Fitness function: count how many time steps FAIL the requirement
def get_fitness_correctness(individual, trace_suite):
    """
    Evaluates the robustness of a requirement represented by a GP individual.

    Returns:
        (robustness,) — lower is better; 0 means satisfied; positive means violated.
    """
    total_rob = 0.0
    try:
        for trace in trace_suite.traces:
            for i, item in enumerate(trace.items):
                rob = get_robustness_at_time_i(individual, i, item)
                total_rob += max(0.0, rob)  # Only penalize violations
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {individual} | {e}")

    return (total_rob,)


def get_robustness_at_time_i(individual, i, item) -> float:
    """
    Evaluates a DEAP PrimitiveTree individual using robustness semantics.

    Parameters:
        individual: gp.PrimitiveTree — the GP expression to evaluate
        i: int - the current trace item index
        item: TraceItem - the current trace item

    Returns:
        float — robustness value (negative = valid, positive = invalid)
    """

    iterator = iter(individual)
    root = next(iterator)
    return eval_node(root, iterator, i, item)


def eval_node(node, iterator, i, item) -> float:
    if isinstance(node, gp.Terminal):
        value = node.value
        # Variable (named terminal)
        if value in item.values:
            return item.values[value]
        # Constant (e.g., fixed or random constant)
        if isinstance(value, (float, int)):
            return value
        # prev(var_name)
        if isinstance(value, str):
            var_name = value[5:-1]
            return item.trace.suite.prev0 if i == 0 else item.trace.items[i-1].values[var_name]
        # Something went wrong
        raise ValueError(f"Unrecognized terminal: {node}, name={node.name}, value={value}")

    elif isinstance(node, gp.Primitive):
        # Recursively evaluate all children
        children = [eval_node(next(iterator), iterator, i, item) for _ in range(node.arity)]

        # Use robustness function for this primitive
        rob_fn = ROBUSTNESS_FN_MAP.get(node.name)
        if rob_fn is None:
            raise NotImplementedError(f"No robustness function defined for {node.name}")
        return rob_fn(*children)

    else:
        raise TypeError(f"Unexpected node type: {node}")
