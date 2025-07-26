from deap import gp
from repair.grammar.grammar import ROBUSTNESS_FN_MAP

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
        if node.name == "dur":
            # dur(time, Bool)
            time = eval_node(next(iterator), iterator, i, item)
            if time > i+1: # not enough trace items to cover duration time
                return float("inf") # TODO: How much should the penalty be?
            else:
                node_dur = next(iterator) # the Bool component of dur
                rob_dur = eval_node(node_dur, iterator, i, item) # advance as normal for t == i
                for t in range(i-time, i): # time <= t < i
                    iter_dur = iter(node_dur) # use separate iterator
                    item_dur = item.trace.items[t] # use previous item
                    rob_dur += eval_node(node_dur, iter_dur, t, item_dur) # eval Bool component with previous item
                return rob_dur
        else:
            # Recursively evaluate all children
            children = [eval_node(next(iterator), iterator, i, item) for _ in range(node.arity)]
            # Use robustness function for this primitive
            rob_fn = ROBUSTNESS_FN_MAP.get(node.name)
            if rob_fn is None:
                raise NotImplementedError(f"No robustness function defined for {node.name}")
            return rob_fn(*children)

    else:
        raise TypeError(f"Unexpected node type: {node}")
