
from repair.fitness.desirability.desirability import ApplicabilityPreservation


class AggregatedRobustnessDifference(ApplicabilityPreservation):
    def evaluate(self, traces, individual, original) -> float:
        pass  # to be implemented


class SatisfiedTimestepDifference(ApplicabilityPreservation):
    def evaluate(self, traces, individual, original) -> float:
        pass  # to be implemented