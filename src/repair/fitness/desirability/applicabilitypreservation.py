
from repair.fitness.desirability.desirability import ApplicabilityPreservation


class AggregatedRobustnessDifference(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:
        pass  # to be implemented.
        # Will be complicated since need to compare at each time step individually


class PreconditionSatisfaction(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:

        pre_sd = current_req.satisfaction_degrees["pre_sd"][0]
        return max(0, -pre_sd)
    
