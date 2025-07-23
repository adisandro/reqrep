
from repair.fitness.desirability.desirability import SyntacticSimilarity


class TreeEditDistance(SyntacticSimilarity):
    def evaluate(self, individual, original) -> float:
        pass  # to be implemented


class CosineSimilarity(SyntacticSimilarity):
    def evaluate(self, individual, original) -> float:
        pass  # to be implemented