import math
from collections import deque

from deap import gp
from repair.grammar.grammar import ROBUSTNESS_FN_MAP


def is_within_margin(a, b):
    return math.isclose(a, b, abs_tol=1e-6)

# Fitness function: count how many time steps FAIL the requirement
def get_fitness_correctness(precondition, postcondition, trace_suite):
    """
    Evaluates the correctness of a requirement represented by a GP individual.

    Returns:
        (delta correctness, perc correctness) —
          delta: 0 means 100% correct, positive means violated, lower is better.
          perc: percentage of violations.
    """
    delta_cor = 0.0
    delta_pre_cor = 0.0
    delta_post_cor = 0.0
    count_cor = 0
    count_pre_cor = 0
    count_post_cor = 0
    count_total = 0
    try:
        # TODO somehow cache the correctness outcomes of pre- and post-
        all_nodes_pre = deque(iter(precondition))
        all_nodes_post = deque(iter(postcondition))
        # For each trace, ...
        for trace in trace_suite.traces:
            count_total += len(trace.items)
            # ... at each time stamp, ...
            for i, item in enumerate(trace.items):
                # ... does pre hold? ...
                pre_cor = max(0.0, eval_nodes(deque(all_nodes_pre), i, item))
                pre_sat = is_within_margin(pre_cor, 0.0)
                delta_pre_cor += pre_cor
                # ... does post hold?
                post_cor = max(0.0, eval_nodes(deque(all_nodes_post), i, item))
                post_sat = is_within_margin(post_cor, 0.0)
                delta_post_cor += post_cor
                if pre_sat:
                    # (pre holds)
                    count_pre_cor += 1
                    if post_sat:
                        # (post holds)
                        count_post_cor += 1
                        # (pre=>post holds)
                        count_cor += 1
                    else:
                        # (pre=>post does not hold)
                        delta_cor += post_cor
                else:
                    # (pre=>post holds)
                    count_cor += 1
                    if post_sat:
                        # (post holds)
                        count_post_cor += 1
    except Exception as e:
        raise ValueError(f"Error evaluating: {precondition} => {postcondition} | {e}")

    out = {
        "cor": (delta_cor, count_cor / count_total),
        "pre_cor": (delta_pre_cor, count_pre_cor / count_total),
        "post_cor": (delta_post_cor, count_post_cor / count_total),
    }
    return out


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
        elif node.name == "dur": # dur(time1, time2, Bool), times can be unordered
            time1 = eval_nodes(remaining_nodes, i, item)
            time2 = eval_nodes(remaining_nodes, i, item)
            start_time = min(time1, time2)
            end_time = max(time1, time2)
            cor = eval_nodes(remaining_nodes, i, item) # needed to advance nodes even for out of duration bounds
            return 0.0 if (item.time < start_time or item.time > end_time) else cor
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
