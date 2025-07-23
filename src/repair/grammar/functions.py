from typing import Callable, List, Type
import operator

class GrammarFunction:
    def __init__(self, name: str,
                 impl: Callable,
                 input_types: List[Type],
                 return_type: Type,
                 robustness_fn: Callable = None,
                 display_name: str = None):
        self.name = name  # Python identifier
        self.impl = impl  # Function used in the GP tree
        self.input_types = input_types
        self.return_type = return_type
        self.robustness_fn = robustness_fn  # Used for violation scoring
        self.display_name = display_name or name

def logical_and(a, b): return a and b
def logical_or(a, b): return a or b
# def prev(a): return 0
# def dur(a, t): return 0

def add_robustness(a, b): return a + b
def sub_robustness(a, b): return a - b
def lt_robustness(a, b): return a - b
def gt_robustness(a, b): return b - a
def eq_robustness(a, b): return abs(a - b)
def and_robustness(a, b): return min(a, b)
def or_robustness(a, b): return max(a, b)
def not_robustness(a): return -a
# def prev_robustness(a): return a
# def dur_robustness(a): return a

GRAMMAR_FUNCTIONS = [
    # Arithmetic ops
    GrammarFunction("add", operator.add, [float, float], float, robustness_fn=add_robustness, display_name="+"),
    GrammarFunction("sub", operator.sub, [float, float], float, robustness_fn=sub_robustness, display_name="-"),

    # Comparison ops
    GrammarFunction("lt", operator.lt, [float, float], bool, robustness_fn=lt_robustness, display_name="<"),
    GrammarFunction("gt", operator.gt, [float, float], bool, robustness_fn=gt_robustness, display_name=">"),
    GrammarFunction("eq", operator.eq, [float, float], bool, robustness_fn=eq_robustness, display_name="=="),

    # Logic ops
    GrammarFunction("and", logical_and, [bool, bool], bool, robustness_fn=and_robustness, display_name="and"),
    GrammarFunction("or", logical_or, [bool, bool], bool, robustness_fn=or_robustness, display_name="or"),
    GrammarFunction("not", operator.not_, [bool], bool, robustness_fn=not_robustness, display_name="not"),

    # TEMPORAL OPERATORS
    # GrammarFunction("prev", prev, [float], float, robustness_fn=prev_robustness, display_name="prev")
    # GrammarFunction("dur", dur, [float], float, robustness_fn=dur_robustness, display_name="dur")
    # TODO: Add custom temporal operators if needed
]
