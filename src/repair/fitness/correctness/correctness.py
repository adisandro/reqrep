import math
from collections import deque
import logging

from deap import gp
from repair.grammar.grammar import ROBUSTNESS_FN_MAP
import traceback

logger = logging.getLogger("gp_logger")

def is_within_margin(a, b):
    return math.isclose(a, b, abs_tol=1e-6)


# Fitness function: count how many time steps FAIL the requirement
def get_fitness_correctness(satisfaction_degrees=None):
    sd = satisfaction_degrees["sd"][0]
    fitness = max(0.0, -sd)  # we want to minimize fitness, so 0 is best (fully correct)
    return fitness


def get_satisfaction_degrees(precondition, postcondition, trace_suite):

    # print("Running get_satisfaction_degrees on: ", precondition, " => ", postcondition)

    ts_delta_cor = float("inf")
    ts_delta_pre_cor = float("inf")
    ts_delta_post_cor = float("inf")

    t_delta_cor = float("inf")
    t_delta_pre_cor = float("inf")
    t_delta_post_cor = float("inf")
    count_cor = 0
    count_pre_cor = 0
    count_post_cor = 0
    count_total = 0
    try:
        # TODO somehow cache the correctness outcomes of pre- and post-
        all_nodes_pre = deque(iter(precondition))
        all_nodes_post = deque(iter(postcondition))
        # For each trace, ...
        logger.info(f"    Trace checking:  {precondition}   =>   {postcondition}")
        for trace in trace_suite.traces:
            count_total += len(trace.items)
            # ... at each time stamp, ...
            for i, item in enumerate(trace.items):
                # ... does PRE hold? ...
                # pre_cor = max(0.0, eval_nodes(deque(all_nodes_pre), i, item))
                pre_cor = eval_nodes(deque(all_nodes_pre), i, item)
                # pre_sat = is_within_margin(pre_cor, 0.0)
                pre_sat = pre_cor >= 0.0 or is_within_margin(pre_cor, 0.0)
                count_pre_cor += 1 if pre_sat else 0

                # delta_pre_cor += pre_cor
                t_delta_pre_cor = min(t_delta_pre_cor, pre_cor)
                ts_delta_pre_cor = min(ts_delta_pre_cor, pre_cor)

                # ... does POST hold?
                # post_cor = max(0.0, eval_nodes(deque(all_nodes_post), i, item))
                post_cor = eval_nodes(deque(all_nodes_post), i, item)
                # post_sat = is_within_margin(post_cor, 0.0)
                post_sat = post_cor >= 0.0 or is_within_margin(post_cor, 0.0)
                count_post_cor += 1 if post_sat else 0

                # delta_post_cor += post_cor
                t_delta_post_cor = min(t_delta_post_cor, post_cor)
                ts_delta_post_cor = min(ts_delta_post_cor, post_cor)

                # ... does PRE=>POST hold?
                t_cor = max(-pre_cor, post_cor)
                # t_sat = is_within_margin(t_cor, 0.0)
                t_sat = t_cor >= 0.0 or is_within_margin(t_cor, 0.0)
                count_cor += 1 if t_sat else 0
                # print(f"{t_cor:.2f} = min(-({pre_cor:.2f}), {post_cor:.2f})")
                t_delta_cor = min(t_delta_cor, t_cor)
                ts_delta_cor = min(ts_delta_cor, t_cor)
    except Exception as e:
        raise ValueError(f"Error evaluating: {precondition} => {postcondition} | {e}")

    out = {
        "sd": (ts_delta_cor, count_cor / count_total, count_total - count_cor),
        "pre_sd": (ts_delta_pre_cor, count_pre_cor / count_total, count_total - count_pre_cor),
        "post_sd": (ts_delta_post_cor, count_post_cor / count_total, count_total - count_post_cor),
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
