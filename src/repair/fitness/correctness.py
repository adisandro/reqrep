from collections import deque

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
                rob = eval_tree(individual, i, item)
                total_rob += max(0.0, rob)  # Only penalize violations
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {individual} | {e}")

    return (total_rob,)


def eval_tree(individual, i, item) -> float:
    """
    Evaluates a DEAP PrimitiveTree individual using robustness semantics.

    Parameters:
        individual: gp.PrimitiveTree — the GP expression to evaluate
        i: int - the current trace item index
        item: TraceItem - the current trace item

    Returns:
        float — robustness value (negative = valid, positive = invalid)
    """

    remaining_nodes = deque(iter(individual))
    return eval_node(remaining_nodes, i, item)


def eval_node(remaining_nodes, i, item) -> (float, int):
    node = remaining_nodes.popleft()
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
        if node.name == "dur": # dur(time, Bool)
            time = eval_node(remaining_nodes, i, item)
            if time > i+1: # not enough trace items to cover duration time
                # dur will always fail on the initial items of trace, do not penalize it
                return float(0.0)
            else:
                rob_dur = float("-inf")
                i_dur = i+1-time
                for t in range(i_dur, i+1): # i_dur <= t <= i
                    # copy nodes for past iterations, advance as normal for current iteration
                    nodes_dur = deque(remaining_nodes) if t != i else remaining_nodes
                    item_dur = item.trace.items[t] if t != i else item
                    rob = eval_node(nodes_dur, t, item_dur) # eval Bool component at each t
                    rob_dur = max(rob_dur, rob) # keep max (worst)
                return rob_dur
        else:
            # Recursively evaluate all children
            children = [eval_node(remaining_nodes, i, item) for _ in range(node.arity)]
            # Use robustness function for this primitive
            rob_fn = ROBUSTNESS_FN_MAP.get(node.name)
            if rob_fn is None:
                raise NotImplementedError(f"No robustness function defined for {node.name}")
            return rob_fn(*children)

    else:
        raise TypeError(f"Unexpected node type: {node}")
