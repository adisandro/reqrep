from abc import ABC, abstractmethod
from typing import List
from deap import gp

from repair.approach.trace import TraceSuite

DIMENSION_IDS = ['Sem', 'Syn', 'Sat']

class SemanticIntegrity(ABC):
    @abstractmethod
    def evaluate(self, trace_suite:TraceSuite, individual:gp.PrimitiveTree) -> float:
        """
        Return either 0 or 1 OR in [0, 1]
        """
        pass


class SyntacticSimilarity(ABC):
    @abstractmethod
    def evaluate(self, individual:gp.PrimitiveTree, original:gp.PrimitiveTree) -> float:
        """
        Return a distance in [0, 1]
        """
        pass


class SatisfactionExtent(ABC):
    @abstractmethod
    def evaluate(self, trace_suite:TraceSuite, individual:gp.PrimitiveTree) -> float:
        """
        Return a distance in [0, inf)
        """
        pass

    
class Desirability:
    def __init__(self,
                 trace_suite: TraceSuite,
                 semantic: SemanticIntegrity,
                 syntactic: SyntacticSimilarity,
                 satisfaction: SatisfactionExtent,
                 weights: List[float] = [1.0, 1.0, 1.0]):
        self.trace_suite = trace_suite
        self.initial_requirement = None

        self.semantic = semantic
        self.syntactic = syntactic
        self.satisfaction = satisfaction

        self.weights = weights
        assert all(w >= 0 for w in self.weights), "All weights must be positive."
        assert sum(self.weights) != 0, "Sum of weights must not be zero."

        self.num_active_dimensions = sum(1 for w in self.weights if w > 0)

    def get_semantic_desirability_components(self, requirement) -> tuple[float, float]:
        if not hasattr(self.semantic, "get_two_components"):
            raise ValueError("The semantic integrity measure does not support get_two_components.")
        return self.semantic.get_two_components(self.trace_suite, requirement)
    
    def get_satisfaction_desirability_components(self, requirement) -> tuple[float, float]:
        if not hasattr(self.satisfaction, "get_two_components"):
            raise ValueError("The satisfaction extent measure does not support get_two_components.")
        return self.satisfaction.get_two_components(requirement, self.initial_requirement)

    def get_desirability_tuple(self, requirement, sem_enabled, syn_enabled, sat_enabled) -> tuple[float, float, float]:
        sem_val = self.semantic.evaluate(self.trace_suite, requirement) if sem_enabled else 0.0
        syn_val = self.syntactic.evaluate(requirement, self.initial_requirement) if syn_enabled else 0.0
        sat_val = self.satisfaction.evaluate(requirement, self.initial_requirement) if sat_enabled else 0.0
        return sem_val, syn_val, sat_val

    def get_raw_desirability_tuple(self, requirement) -> tuple[float, float, float]:
        return self.get_desirability_tuple(requirement, True, True, True)

    def evaluate(self, requirement) -> float:
        des = self.get_desirability_tuple(requirement, self.weights[0] > 0, self.weights[1] > 0, self.weights[2] > 0)
        weighted_des = (
            self.weights[0] * des[0],
            self.weights[1] * des[1],
            self.weights[2] * des[2]
        )
        weighted_sum = sum(weighted_des)
        out = {
            "des": weighted_sum,
            "tuple": weighted_des
        }
        return out
