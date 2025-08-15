from abc import ABC, abstractmethod
from typing import List
from deap import gp

from repair.approach.trace import TraceSuite


class SemanticSanity(ABC):
    @abstractmethod
    def evaluate(self, trace_suite:TraceSuite, individual:gp.PrimitiveTree) -> float:
        """
        Return either 0 or 1
        """
        pass


class SyntacticSimilarity(ABC):
    @abstractmethod
    def evaluate(self, individual:gp.PrimitiveTree, original:gp.PrimitiveTree) -> float:
        """
        Return a distance in [0, 1]
        """
        pass


class ApplicabilityPreservation(ABC):
    @abstractmethod
    def evaluate(self, trace_suite:TraceSuite, individual:gp.PrimitiveTree, original:gp.PrimitiveTree) -> float:
        pass

    
class Desirability:
    def __init__(self,
                 trace_suite: TraceSuite,
                 semantic: SemanticSanity,
                 syntactic: SyntacticSimilarity,
                 applicability: ApplicabilityPreservation,
                 weights: List[float] = [1.0, 1.0, 1.0]):
        self.trace_suite = trace_suite
        self.initial_requirement = None

        self.semantic = semantic
        self.syntactic = syntactic
        self.applicability = applicability

        self.weights = weights
        assert all(w >= 0 for w in self.weights), "All weights must be positive."
        assert sum(self.weights) != 0, "Sum of weights must not be zero."

    def get_desirability_tuple(self, individual, pre_post_id) -> tuple[float, float, float]:
        initial_condition = self.initial_requirement.get_condition(pre_post_id)
        sem_val = 0.0 if self.weights[0] == 0 else self.semantic.evaluate(self.trace_suite, individual)
        syn_val = 0.0 if self.weights[1] == 0 else self.syntactic.evaluate(individual, initial_condition)
        app_val = 0.0 if self.weights[2] == 0 else self.applicability.evaluate(self.trace_suite, individual, initial_condition)
        return sem_val, syn_val, app_val

    # TODO: pre_post_id should be temporary
    def evaluate(self, individual, pre_post_id) -> float:
        des = self.get_desirability_tuple(individual, pre_post_id)
        weighted_sum = (
            self.weights[0] * des[0] +
            self.weights[1] * des[1] +
            self.weights[2] * des[2]
        )
        return weighted_sum
