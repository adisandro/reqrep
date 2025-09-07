from typing import Callable, List, Type
import operator

def logical_and(a, b): return a and b
def logical_or(a, b): return a or b
def logical_impl(a, b): return (not a) or b

def add_robustness(a, b): return a + b
def sub_robustness(a, b): return a - b
def lt_robustness(a, b): return b - a + 1e-5
def le_robustness(a, b): return b - a
def gt_robustness(a, b): return a - b + 1e-5
def ge_robustness(a, b): return a - b
def eq_robustness(a, b): return abs(a - b)

def and_robustness(a, b): return min(a, b)
def or_robustness(a, b): return max(a, b)
def impl_robustness(a, b): return max(-a, b)
def not_robustness(a): return -a

# this differentiates bool and int types, since bool is a subclass of int in Python
class Bool: pass

class GrammarFunction:
    def __init__(self, name: str,
                 impl: Callable,
                 input_types: List[Type],
                 return_type: Type,
                 robustness_fn: Callable,
                 display_name: str = None):
        self.name = name  # Python identifier
        self.impl = impl  # Function used in the GP tree
        self.input_types = input_types
        self.return_type = return_type
        self.robustness_fn = robustness_fn  # Used for violation scoring
        self.display_name = display_name or name

    @staticmethod
    def create_functions():
        return [
            # Arithmetic ops
            GrammarFunction("add", operator.add, [float, float], float, robustness_fn=add_robustness, display_name="+"),
            GrammarFunction("sub", operator.sub, [float, float], float, robustness_fn=sub_robustness, display_name="-"),
            # Comparison ops
            GrammarFunction("lt", operator.lt, [float, float], Bool, robustness_fn=lt_robustness, display_name="<"),
            GrammarFunction("le", operator.le, [float, float], Bool, robustness_fn=le_robustness, display_name="<="),
            GrammarFunction("gt", operator.gt, [float, float], Bool, robustness_fn=gt_robustness, display_name=">"),
            GrammarFunction("ge", operator.ge, [float, float], Bool, robustness_fn=ge_robustness, display_name=">="),
            GrammarFunction("eq", operator.eq, [float, float], Bool, robustness_fn=eq_robustness, display_name="=="),
            # Logic ops
            GrammarFunction("and", logical_and, [Bool, Bool], Bool, robustness_fn=and_robustness, display_name="and"),
            GrammarFunction("or", logical_or, [Bool, Bool], Bool, robustness_fn=or_robustness, display_name="or"),
            GrammarFunction("implies", logical_impl, [Bool, Bool], Bool, robustness_fn=impl_robustness, display_name="=>"),
            GrammarFunction("not", operator.not_, [Bool], Bool, robustness_fn=not_robustness, display_name="not"),
            GrammarFunction("prev", lambda: None, [str], float, robustness_fn=lambda: None, display_name="prev"),
            GrammarFunction("dur", lambda: None, [int, Bool], Bool, robustness_fn=lambda: None, display_name="dur")
        ]
