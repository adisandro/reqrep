from abc import ABC, abstractmethod
from typing import List

from repair.trace import TraceSuite


class SemanticSanity(ABC):
    @abstractmethod
    def evaluate(self, trace_suite, individual) -> float:
        pass


class SyntacticSimilarity(ABC):
    @abstractmethod
    def evaluate(self, individual, original) -> float:
        pass


class ApplicabilityPreservation(ABC):
    @abstractmethod
    def evaluate(self, trace_suite, individual, original) -> float:
        pass

    
class Desirability:
    def __init__(self,
                 trace_suite: TraceSuite,
                 semantic: SemanticSanity,
                 syntactic: SyntacticSimilarity,
                 applicability: ApplicabilityPreservation,
                 weights: List[float] = [1.0, 1.0, 1.0]):
        self.trace_suite = trace_suite
        self.semantic = semantic
        self.syntactic = syntactic
        self.applicability = applicability

        self.weights = weights
        assert all(w >= 0 for w in self.weights), "All weights must be positive."
        assert sum(self.weights) != 0, "Sum of weights must not be zero."

    def evaluate(self, individual, original=None) -> float:
        sem_val = 0.0 if self.weights[0] == 0 else self.semantic.evaluate(self.trace_suite, individual)
        syn_val = 0.0 if self.weights[1] == 0 else self.syntactic.evaluate(individual, original)
        app_val = 0.0 if self.weights[2] == 0 else self.applicability.evaluate(self.trace_suite, individual, original)
        weighted_sum = (
            self.weights[0] * sem_val +
            self.weights[1] * syn_val +
            self.weights[2] * app_val
        )
        return weighted_sum
