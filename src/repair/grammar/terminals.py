from functools import partial
from typing import Callable, Type
import random

class GrammarTerminal:
    def __init__(self, name: str,
                 value_fn: Callable,
                 return_type: Type,
                 display_name: str = None):
        self.name = name
        self.value_fn = value_fn  # Callable producing terminal value
        self.return_type = return_type
        self.display_name = display_name or name

    @staticmethod
    def create_terminals(trace_suite):
        terminals = [
            # Static numeric terminals (fixed values)
            GrammarTerminal("const_-10", lambda: -10.0, float, display_name="-10"),
            GrammarTerminal("const_0", lambda: 0.0, float, display_name="0"),
            GrammarTerminal("const_10", lambda: 10.0, float, display_name="10"),
        ]
        for var_name in trace_suite.variable_names:
            # prev(_var) uses the underscore to avoid clashing with proper var names (of float type)
            terminals.append(GrammarTerminal(var_name, lambda: f"_{var_name}", str, display_name=var_name))
        return terminals

    @staticmethod
    def create_ephemerals():
        return [
            # Ephemeral numeric terminals (randomly sampled each individual)
            GrammarTerminal("rand_float", partial(random.uniform, -10, 10), float, display_name="rand(-10, 10)"),
            GrammarTerminal("rand_dur", partial(random.randint, 2, 5), int, display_name="rand(2, 5)"),
        ]
