
from repair.fitness.desirability.desirability import SyntacticSimilarity
import math
from collections import Counter
from zss import simple_distance, Node


class TreeEditDistance(SyntacticSimilarity):
    
    def __init__(self):
        super().__init__()

    def tree_to_zss_node(self, tree):
        # tree is iterable, root is tree[0]
        def build_subtree(expr, idx=0):
            node = Node(expr[idx].name) # name is important here
            arity = expr[idx].arity if hasattr(expr[idx], "arity") else 0
            next_idx = idx + 1
            for _ in range(arity):
                child, next_idx = build_subtree(expr, next_idx)
                node.addkid(child)
            return node, next_idx
        root, _ = build_subtree(tree)
        return root

    def _get_tree_edit_distance(self, individual, original):
        node1 = self.tree_to_zss_node(individual)
        node2 = self.tree_to_zss_node(original)
        return simple_distance(node1, node2)
        
    def evaluate(self, current_req, initial_req):
        tree_edit_distance = self._get_tree_edit_distance(current_req.merged, initial_req.merged)

        fitness = tree_edit_distance # TODO (MAYBE) improve
        return fitness


class CosineSimilarity(SyntacticSimilarity):
    """
    Computes cosine similarity between two GP PrimitiveTrees.
    Returns 1 - similarity as the 'distance'.
    """

    def __init__(self):
        super().__init__()

    def _tree_to_vector(self, tree):
        # Convert a PrimitiveTree into a frequency vector of its nodes.
        counts = Counter(node.name for node in tree) # Node names are important for similarity
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
        return similarity

    def evaluate(self, current_req, initial_req):
        cosine_similarity = self._get_cosine_similarity(current_req.merged, initial_req.merged)
        fitness = 1 - cosine_similarity
        return fitness
    