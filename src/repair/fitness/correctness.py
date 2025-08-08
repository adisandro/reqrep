import math
from collections import deque

from deap import gp
from repair.grammar.grammar import ROBUSTNESS_FN_MAP


def is_within_margin(a, b):
    return math.isclose(a, b, abs_tol=1e-6)


# Fitness function: count how many time steps FAIL the requirement
def get_fitness_correctness(individual, trace_suite):
    """
    Evaluates the correctness of a requirement represented by a GP individual.

    Returns:
        (delta correctness, perc correctness) —
          delta: 0 means 100% correct, positive means violated, lower is better.
          perc: percentage of violations.
    """
    delta_cor = 0.0
    count_cor = 0
    count_total = 0
    try:
        all_nodes = deque(iter(individual))
        for trace in trace_suite.traces:
            count_total += len(trace.items)
            for i, item in enumerate(trace.items):
                cor = max(0.0, eval_nodes(deque(all_nodes), i, item)) # only penalize violations
                delta_cor += cor
                if is_within_margin(cor, 0.0):
                    count_cor += 1
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {individual} | {e}")

    return delta_cor, count_cor/count_total


def eval_tree(individual, i, item) -> float | int:
    """
    Evaluates a DEAP PrimitiveTree individual using robustness semantics.

    Parameters:
        individual: gp.PrimitiveTree — the GP expression to evaluate
        i: int - the current trace item index
        item: TraceItem - the current trace item

    Returns:
        float — robustness value (negative = valid, positive = invalid)
    """
    return eval_nodes(deque(iter(individual)), i, item)


def eval_nodes(remaining_nodes, i, item) -> float | int:
    node = remaining_nodes.popleft()
    if isinstance(node, gp.Terminal):
        value = node.value
        # True/False booleans (we never generate them when repairing, but could be in the input requirement)
        if isinstance(value, bool):
            return 0.0 if value else float("inf")
        # Constant (e.g., fixed or random constant)
        if isinstance(value, (float, int)):
            return value
        # Variable (named terminal)
        if value.startswith("_"): # Variable from the prev primitive (starts with underscore)
            value = value[1:]
        if value in item.values:
            return item.values[value]
        # Something went wrong
        raise ValueError(f"Unrecognized terminal: {node}, name={node.name}, value={value}")

    elif isinstance(node, gp.Primitive):
        if node.name == "prev": # prev(_var)
            if i == 0: # no previous trace item
                # pop and assign default
                remaining_nodes.popleft()
                return item.trace.suite.prev0
            else:
                return eval_nodes(remaining_nodes, i-1, item.trace.items[i-1])
        elif node.name == "dur": # dur(time, Bool)
            time = eval_nodes(remaining_nodes, i, item)
            if time > i+1: # not enough trace items to cover duration time
                # dur will always fail on the initial items of trace, do not penalize it
                # TODO We should popleft the whole Bool component
                return 0.0
            else:
                rob_dur = float("-inf")
                i_dur = i+1-time
                for t in range(i_dur, i+1): # i_dur <= t <= i
                    # copy nodes for past iterations, advance as normal for current iteration
                    nodes_dur = deque(remaining_nodes) if t != i else remaining_nodes
                    item_dur = item.trace.items[t] if t != i else item
                    rob = eval_nodes(nodes_dur, t, item_dur) # eval Bool component at each t
                    rob_dur = max(rob_dur, rob) # keep max (worst)
                return rob_dur
        else:
            # Recursively evaluate all children
            children = [eval_nodes(remaining_nodes, i, item) for _ in range(node.arity)]
            # Use robustness function for this primitive
            rob_fn = ROBUSTNESS_FN_MAP.get(node.name)
            if rob_fn is None:
                raise NotImplementedError(f"No robustness function defined for {node.name}")
            return rob_fn(*children)

    else:
        raise TypeError(f"Unexpected node type: {node}")
