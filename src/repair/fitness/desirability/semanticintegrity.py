import logging
import random
from collections import deque
from deap import gp
from repair.fitness.desirability.desirability import SemanticIntegrity
from repair.fitness.correctness.correctness import eval_tree, is_within_margin
from z3 import Solver, sat, unsat, unknown

logger = logging.getLogger("gp_logger")


class SamplingBasedTautologyCheck(SemanticIntegrity):
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
        if all_same_merged:
            logger.info(f"      Tautology found (Sampling): {requirement.merged}")
        return 1.0 if all_same_merged else 0.0


class Z3TautologyCheck(SemanticIntegrity):
    @staticmethod
    def evaluate_sat(requirement) -> float:
        consts = {node.value for node in requirement.merged # use set to filter duplicates
                  if isinstance(node, gp.Terminal) and isinstance(node.value, str)}
        smtlib_decl = " ".join([f"(declare-const {const} Real)" for const in consts])
        smtlib_req = (requirement.merged.__str__()
                      .replace(",", "")
                      .replace("prev('", "")
                      .replace("')", "")
                      .replace("implies(", "(=> ")
                      .replace("eq(", "(= ")
                      .replace("ge(", "(>= ")
                      .replace("gt(", "(> ")
                      .replace("le(", "(<= ")
                      .replace("lt(", "(< ")
                      .replace("sub(", "(- ")
                      .replace("add(", "(+ ")
                      .replace("and(", "(and ")
                      .replace("or(", "(or ")
                      .replace("not(", "(not "))
        smtlib = f"{smtlib_decl} (assert (not {smtlib_req}))"
        solver = Solver()
        solver.from_string(smtlib)
        result = solver.check()
        if result != sat:
            logger.info(f"      Tautology found (Z3): {smtlib_req}")

        return result

    def evaluate(self, trace_suite, requirement) -> float:
        return 1.0 if self.evaluate_sat(requirement) != sat else 0.0


class Z3TautologyCheckWithSamplingFallback(SemanticIntegrity):
    def __init__(self, n_samples: int = 10):
        super().__init__()
        self.z3 = Z3TautologyCheck()
        self.sampling = SamplingBasedTautologyCheck(n_samples)

    def evaluate(self, trace_suite, requirement) -> float:
        result = self.z3.evaluate_sat(requirement)
        if result == unknown:
            return self.sampling.evaluate(trace_suite, requirement)
        elif result == unsat:
            return 1.0
        else:
            return 0.0


class VarTypeConsistencyCheck(SemanticIntegrity):
    def evaluate_nodes(self, trace_suite, remaining_nodes):
        node = remaining_nodes.popleft()
        if isinstance(node, gp.Terminal):
            value = node.value
            # Number
            if isinstance(value, (float, int)):
                if node.name.startswith("rand_float_"):
                    return node.name  # Random (typed) number
                return "*"  # Fixed (initial) number
            # Variable
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
                    if child.startswith("_"):  # Variable from the prev primitive (starts with underscore)
                        child = child[1:]
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
        result = max(self.evaluate_nodes(trace_suite, deque(iter(requirement.pre))),
                     self.evaluate_nodes(trace_suite, deque(iter(requirement.post))))
        if result == 1.0:
            logger.info(f"      Var type inconsistency found: {requirement.merged}")
        return result


class TautologyAndVarTypeSanity(SemanticIntegrity):
    def __init__(self, tautology_checker):
        super().__init__()
        self.tautology = tautology_checker
        self.var_type = VarTypeConsistencyCheck()
        self.composed=True

    def get_two_components(self, trace_suite, requirement):
        result_tautology = self.tautology.evaluate(trace_suite, requirement) # {0.0, 1.0}
        result_var_type = self.var_type.evaluate(trace_suite, requirement) # {0.0, 1.0} (may become continuous)
        return result_tautology, result_var_type

    def evaluate(self, trace_suite, requirement):
        result_tautology, result_var_type = self.get_two_components(trace_suite, requirement)
        # Define fitness
        result_combined = 0.5*result_tautology + 0.5*result_var_type
        # result = max(result, self.var_type.evaluate(trace_suite, requirement))
        return result_combined