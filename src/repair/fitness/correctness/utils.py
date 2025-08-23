from collections import deque

from repair.fitness.correctness.correctness import is_within_margin, eval_nodes
import pandas as pd


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
                else:
                    # (pre does not hold)
                    # (pre=>post trivially holds)
                    delta_cor += 0.0
                    count_cor += 1
            data.append({
                "trace_index": j,
                "delta_cor": delta_cor,
                "perc_cor": count_cor / count_total,
                "violating_indices": violating_indices
            })
            results = pd.DataFrame(data)
    except Exception as e:
        raise ValueError(f"Error evaluating: {precondition} => {postcondition} | {e}")
    return results

