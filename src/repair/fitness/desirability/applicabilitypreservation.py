
from repair.fitness.correctness.utils import is_within_margin
from repair.fitness.desirability.desirability import ApplicabilityPreservation


class AggregatedRobustnessDifference(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:
        pass  # to be implemented.
        # Will be complicated since need to compare at each time step individually


class PreconditionSatisfaction(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:

        pre_sd = current_req.satisfaction_degrees["pre_sd"][0]
        return max(0, -pre_sd)
    
class AvoidAbsoluteSatisfaction(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:

        pre_sat_ratio_of_traces = current_req.satisfaction_degrees["pre_sd"][3]
        post_sat_ratio_of_traces = current_req.satisfaction_degrees["post_sd"][3]

        if is_within_margin(pre_sat_ratio_of_traces, 0.0) or \
            (is_within_margin(pre_sat_ratio_of_traces, 1.0) and is_within_margin(post_sat_ratio_of_traces, 1.0)):
            return 0.0
        else:
            return 1.0
    
