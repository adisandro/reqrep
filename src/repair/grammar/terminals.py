from typing import Callable, Type, List
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
        # TODO: having a prev for each variable increases the chance that prev is picked while constructing the expression
        for var_name in trace_suite.variable_names:
            terminals.append(GrammarTerminal(f"prev_{var_name}", lambda: None, float, display_name=f"prev({var_name})"))
        return terminals

    @staticmethod
    def create_ephemerals(trace_suite):
        return [
            # Ephemeral numeric terminals (randomly sampled each individual)
            GrammarTerminal("rand_float", lambda: random.uniform(-10, 10), float, display_name="rand(-10, 10)"),
            GrammarTerminal("rand_dur", lambda: random.uniform(1, min([len(trace) for trace in trace_suite.traces])),
                            int, display_name="rand(1, min_trace_len)"),
        ]
