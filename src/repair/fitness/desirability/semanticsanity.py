import random
from collections import deque

from deap import gp

from repair.fitness.desirability.desirability import SemanticSanity

from repair.fitness.correctness.correctness import eval_tree, is_within_margin


class SamplingBasedSanity(SemanticSanity):
    def __init__(self, n_samples: int = 10):
        super().__init__()
        self.n_samples = n_samples

    def evaluate(self, trace_suite, requirement) -> float:
        """
        Returns:
            0.0 → candidate has variable correctness across inputs (not tautology/contradiction)
            1.0 → candidate is tautology or contradiction (correctness constant)
        """
        all_same = True
        base_cor_pre = None
        base_cor_post = None

        for _ in range(self.n_samples):
            trace = random.choice(trace_suite.traces)
            if len(trace.items) < 2:
                continue  # skip traces that are too short
            i = random.randint(1, len(trace.items) - 1)
            item = trace.items[i]

            cor_pre = eval_tree(requirement.pre, i, item)
            if base_cor_pre is None:
                base_cor_pre = cor_pre
            elif not is_within_margin(cor_pre, base_cor_pre):
                all_same = False
                break

            cor_post = eval_tree(requirement.post, i, item)
            if base_cor_post is None:
                base_cor_post = cor_post
            elif not is_within_margin(cor_post, base_cor_post):
                all_same = False
                break

        # If all robustness values are the same,
        # it's (likely) trivial, i.e. a constant function (tautology/contradiction)
        return 1.0 if all_same else 0.0


class SymbolicSanity(SemanticSanity):
    def evaluate(self, trace_suite, individual) -> float:
        pass  # to be implemented


class VarTypeSanity(SemanticSanity):
    def evaluate_nodes(self, trace_suite, remaining_nodes):
        node = remaining_nodes.popleft()
        if isinstance(node, gp.Terminal):
            value = node.value
            # Constant (e.g., fixed or random constant)
            if isinstance(value, (float, int)):
                return "*" # wildcard
            # Variable (named terminal)
            if value.startswith("_"):  # Variable from the prev primitive (starts with underscore)
                return trace_suite.variables[value[1:]]
            return trace_suite.variables[value]
        elif isinstance(node, gp.Primitive):
            if node.name == "dur":  # dur(time1, time2, Bool)
                # pop times, eval Bool
                remaining_nodes.popleft()
                remaining_nodes.popleft()
                return self.evaluate_nodes(trace_suite, remaining_nodes)
            if node.name == "prev":  # prev(_var)
                return self.evaluate_nodes(trace_suite, remaining_nodes)
            children = [self.evaluate_nodes(trace_suite, remaining_nodes) for _ in range(node.arity)]
            if node.name in {"not", "and", "or"}:
                return max(children)  # return desirability value
            children2 = [c for c in children if c != "*"]  # filter out numbers
            if node.name in {"add", "sub"}:
                if len(children2) == 0:  # all numbers
                    return "*"
                return children2[0] if all(c == children2[0] for c in children2) else "TYPE_MISMATCH"  # return a type
            return 0.0 if all(c != "TYPE_MISMATCH" and c == children2[0] for c in children2) else 1.0  # return desirability value
        else:
            raise TypeError(f"Unexpected node type: {node}")

    def evaluate(self, trace_suite, requirement):
        return max(self.evaluate_nodes(trace_suite, deque(iter(requirement.pre))),
                   self.evaluate_nodes(trace_suite, deque(iter(requirement.post))))


class SamplingAndVarTypeSanity(SemanticSanity):
    def __init__(self, n_samples: int = 10):
        super().__init__()
        self.sampling = SamplingBasedSanity(n_samples)
        self.var_type = VarTypeSanity()

    def evaluate(self, trace_suite, requirement):
        result = self.sampling.evaluate(trace_suite, requirement)
        if result < 1.0: # 1.0 is already a tautology
            result = max(result, self.var_type.evaluate(trace_suite, requirement))
        return result
