
from repair.fitness.desirability.desirability import ApplicabilityPreservation


class AggregatedRobustnessDifference(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:
        pass  # to be implemented.
        # Will be complicated since need to compare at each time step individually


class SatisfiedTimestepDifference(ApplicabilityPreservation):
    def evaluate(self, current_req, initial_req) -> float:

        # correctness ratio, in [0, 1], 
        cor_cur = current_req.correctness["pre_cor"][1]
        cor_init = initial_req.correctness["pre_cor"][1]

        d = abs(cor_cur - cor_init)
        return d
    
