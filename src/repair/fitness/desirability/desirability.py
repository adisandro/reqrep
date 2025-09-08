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

    def get_desirability_tuple(self, requirement) -> tuple[float, float, float]:
        sem_val = 0.0 if self.weights[0] == 0 else self.semantic.evaluate(self.trace_suite, requirement)
        syn_val = 0.0 if self.weights[1] == 0 else self.syntactic.evaluate(requirement, self.initial_requirement)
        app_val = 0.0 if self.weights[2] == 0 else self.satisfaction.evaluate(requirement, self.initial_requirement)
        return sem_val, syn_val, app_val

    def evaluate(self, requirement) -> float:
        des = self.get_desirability_tuple(requirement)
        weighted_sum = (
            self.weights[0] * des[0] +
            self.weights[1] * des[1] +
            self.weights[2] * des[2]
        )
        out = {
            "des": weighted_sum,
            "tuple": des
        }
        return out
