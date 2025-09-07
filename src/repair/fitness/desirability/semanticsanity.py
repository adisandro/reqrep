import random
from collections import deque
from os.path import samefile

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
        base_cor_merged = None
        all_same_merged = True

        for _ in range(self.n_samples):
            trace = random.choice(trace_suite.traces)
            if len(trace.items) < 2:
                continue  # skip traces that are too short
            i = random.randint(1, len(trace.items) - 1)
            item = trace.items[i]

            cor_merged = eval_tree(requirement.merged, i, item)
            if base_cor_merged is None:
                base_cor_merged = cor_merged
            elif not is_within_margin(cor_merged, base_cor_merged):
                all_same_merged = False
                break

        # If all robustness values are the same,
        # it's (likely) trivial, i.e. a constant function (tautology/contradiction)
        # return 1.0 if all_same_pre or all_same_post else 0.0
        return 1.0 if all_same_merged else 0.0


class SymbolicSanity(SemanticSanity):
    def evaluate(self, trace_suite, individual) -> float:
        pass  # to be implemented


class VarTypeSanity(SemanticSanity):
    def evaluate_nodes(self, trace_suite, remaining_nodes):
        node = remaining_nodes.popleft()
        if isinstance(node, gp.Terminal):
            value = node.value
            # Number
            if isinstance(value, (float, int)):
                if isinstance(node.name, str):
                    return node.name  # Random (typed) number
                return "*"  # Fixed number
            # Variable
            # if value.startswith("_"):  # Variable from the prev primitive (starts with underscore)
            #     return trace_suite.variables[value[1:]]["unit"]
            # return trace_suite.variables[value]["unit"]
            if value.startswith("_"):  # Variable from the prev primitive (starts with underscore)
                return value[1:]
            return value
        elif isinstance(node, gp.Primitive):
            # dur(time, Bool)
            if node.name == "dur":
                # pop time, eval Bool
                remaining_nodes.popleft()
                return self.evaluate_nodes(trace_suite, remaining_nodes)
            # prev(_var)
            if node.name == "prev":
                return self.evaluate_nodes(trace_suite, remaining_nodes)
            children = [self.evaluate_nodes(trace_suite, remaining_nodes) for _ in range(node.arity)]
            # not, and, or
            if node.name in {"not", "and", "or", "implies"}:
                return max(children)  # worst desirability value
            # float args functions
            all_numbers = True
            all_same_var = True
            same_var = None
            children_units = []
            for child in children:
                if child == "*":
                    all_same_var = False
                    continue
                if child.startswith("rand_float_"):
                    all_same_var = False
                    child = child.split("rand_float_")[1]
                else:
                    all_numbers = False
                    if same_var is None:
                        same_var = child
                    elif child != same_var:
                        all_same_var = False
                    if child in trace_suite.variables:
                        child = trace_suite.variables[child]["unit"]
                children_units.append(child)
            if node.name in {"add", "sub"}:
                if all_numbers or all_same_var or any(u != children_units[0] for u in children_units):
                    return "UNIT_MISMATCH"
                return children_units[0]  # return unit
            # return desirability value
            if all_numbers or all_same_var or any(u == "UNIT_MISMATCH" or u != children_units[0] for u in children_units):
                return 1.0
            return 0.0
        else:
            raise TypeError(f"Unexpected node type: {node}")

    def evaluate(self, trace_suite, requirement):
        #TODO can we check for same var comparison?
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
