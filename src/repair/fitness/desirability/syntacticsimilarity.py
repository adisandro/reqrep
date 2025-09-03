
from repair.fitness.desirability.desirability import SyntacticSimilarity
import math
from collections import Counter
from deap import gp


class TreeEditDistance(SyntacticSimilarity):
    def evaluate(self, individual, original) -> float:
        pass  # to be implemented


class CosineSimilarity(SyntacticSimilarity):
    """
    Computes cosine similarity between two GP PrimitiveTrees.
    Returns 1 - similarity as the 'distance'.
    """

    def __init__(self):
        super().__init__()

    def _tree_to_vector(self, tree):
        # Convert a PrimitiveTree into a frequency vector of its nodes.
        counts = Counter(node.name for node in tree)
        return counts
    
    def _get_cosine_similarity(self, individual, original):
        """
        individual, original: gp.PrimitiveTree
        Returns a distance in [0, 1].
        """
        # TODO rethink the return value (currently in [0, 1]). Return something that is closer to
        # the "semantic desirability" order of magnitude

        vec_ind = self._tree_to_vector(individual)
        vec_orig = self._tree_to_vector(original)

        # All unique tokens from both trees
        all_tokens = set(vec_ind.keys()).union(set(vec_orig.keys()))

        # Convert to aligned lists
        v1 = [vec_ind.get(tok, 0) for tok in all_tokens]
        v2 = [vec_orig.get(tok, 0) for tok in all_tokens]

        if v1 == v2:
            return 0.0 #Identical trees

        # Compute dot product and magnitudes
        dot = sum(a*b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a*a for a in v1))
        mag2 = math.sqrt(sum(b*b for b in v2))

        if mag1 == 0 or mag2 == 0:
            return 1.0  # No similarity if one is empty

        similarity = dot / (mag1 * mag2)
        distance = 1 - similarity
        return distance

    def evaluate(self, current_req, initial_req):
        # TODO currently using the average distance between the pre and post conditions
        pre_dist = self._get_cosine_similarity(current_req.pre, initial_req.pre)
        post_dist = self._get_cosine_similarity(current_req.post, initial_req.post)
        return (pre_dist + post_dist) / 2