from collections import deque
import logging

from repair.fitness.correctness.utils import is_within_margin, eval_nodes

logger = logging.getLogger("gp_logger")



# Fitness function: count how many time steps FAIL the requirement
def get_fitness_correctness(satisfaction_degrees=None):
    sd = satisfaction_degrees["sd"][0]
    fitness = max(0.0, -sd)  # we want to minimize fitness, so 0 is best (fully correct)
    return fitness


def get_satisfaction_degrees(precondition, postcondition, trace_suite):

    def is_sat(sd):
        return sd >= 0.0 or is_within_margin(sd, 0.0)

    # print("Running get_satisfaction_degrees on: ", precondition, " => ", postcondition)

    ts_pre_sd = float("inf")
    ts_post_sd = float("inf")
    ts_impl_sd = float("inf")

    t_count_pre_sat = 0
    t_count_post_sat = 0
    t_count_impl_sat = 0
    t_count_total = len(trace_suite.traces)

    item_count_pre_sat = 0
    item_count_post_sat = 0
    item_count_impl_sat = 0
    item_count_total = 0
    try:
        all_nodes_pre = deque(iter(precondition))
        all_nodes_post = deque(iter(postcondition))
        # For each trace, ...
        logger.info(f"    Trace checking:  {precondition}   =>   {postcondition}")
        for trace in trace_suite.traces[:10]:
            item_count_total += len(trace.items)

            t_pre_sd = float("inf")
            t_post_sd = float("inf")
            t_impl_sd = float("inf")

            # ... at each time stamp, ...
            for i, item in enumerate(trace.items):
                # ... does PRE hold? ...
                item_pre_sd = eval_nodes(deque(all_nodes_pre), i, item)
                item_count_pre_sat += 1 if is_sat(item_pre_sd) else 0

                t_pre_sd = min(t_pre_sd, item_pre_sd)
                ts_pre_sd = min(ts_pre_sd, item_pre_sd)

                # ... does POST hold?
                item_post_sd = eval_nodes(deque(all_nodes_post), i, item)
                item_count_post_sat += 1 if is_sat(item_post_sd) else 0

                t_post_sd = min(t_post_sd, item_post_sd)
                ts_post_sd = min(ts_post_sd, item_post_sd)

                # ... does PRE=>POST hold?
                item_impl_sd = max(-item_pre_sd, item_post_sd)
                item_count_impl_sat += 1 if is_sat(item_impl_sd) else 0

                t_impl_sd = min(t_impl_sd, item_impl_sd)
                ts_impl_sd = min(ts_impl_sd, item_impl_sd)

            # Measure trace-level stats
            t_count_pre_sat += 1 if is_sat(t_pre_sd) else 0
            t_count_post_sat += 1 if is_sat(t_post_sd) else 0
            t_count_impl_sat += 1 if is_sat(t_impl_sd) else 0

    except Exception as e:
        raise ValueError(f"Error evaluating: {precondition} => {postcondition} | {e}")

    out = {
        "sd": (ts_impl_sd, item_count_impl_sat / item_count_total, item_count_total - item_count_impl_sat, t_count_impl_sat/t_count_total, t_count_total - t_count_impl_sat),
        "pre_sd": (ts_pre_sd, item_count_pre_sat / item_count_total, item_count_total - item_count_pre_sat, t_count_pre_sat/t_count_total, t_count_total - t_count_pre_sat),
        "post_sd": (ts_post_sd, item_count_post_sat / item_count_total, item_count_total - item_count_post_sat, t_count_post_sat/t_count_total, t_count_total - t_count_post_sat),
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

