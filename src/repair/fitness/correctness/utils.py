import math
from collections import deque

from deap import gp
from repair.grammar.grammar import ROBUSTNESS_FN_MAP
import pandas as pd


def is_within_margin(a, b):
    return math.isclose(a, b, abs_tol=1e-6)

# Fitness function: count how many time steps FAIL the requirement
def get_trace_correctness(precondition, postcondition, trace_suite):
    """
    Evaluates the correctness of a requirement represented by a GP individual.

    Returns:
        List of dicts, one per trace in trace_suite, each containing:
            {
                "cor": (delta_cor, perc_cor),
                "pre_cor": (delta_pre_sat, perc_pre_sat),
                "post_cor": (delta_post_sat, perc_post_sat),
            }
    """
    results = {}
    try:
        data = []
        for j, trace in enumerate(trace_suite.traces):
            delta_cor = 0.0
            count_cor = 0
            count_total = len(trace.items)
            all_nodes_pre = deque(iter(precondition))
            all_nodes_post = deque(iter(postcondition))
            violating_indices = []
            violating_times = []
            for i, item in enumerate(trace.items):
                # ... does precondition hold? ...
                pre_rob = max(0.0, eval_nodes(deque(all_nodes_pre), i, item))
                if is_within_margin(pre_rob, 0.0):
                    # (pre holds)
                    # ... does postcondition hold?
                    post_rob = max(0.0, eval_nodes(deque(all_nodes_post), i, item))
                    delta_cor += post_rob
                    if is_within_margin(post_rob, 0.0):
                        # (post holds)
                        # (pre=>post holds)
                        count_cor += 1
                    else:
                        # (pre holds, post fails)
                        violating_indices.append(i)
                        violating_times.append(item.time)
                else:
                    # (pre does not hold)
                    # (pre=>post trivially holds)
                    delta_cor += 0.0
                    count_cor += 1
            data.append({
                "trace_index": j,
                "delta_cor": delta_cor,
                "perc_cor": count_cor / count_total,
                "violating_indices": violating_indices,
                "violating_times": violating_times
            })
            results = pd.DataFrame(data)
    except Exception as e:
        raise ValueError(f"Error evaluating: {precondition} => {postcondition} | {e}")
    return results


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