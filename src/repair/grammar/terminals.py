from typing import Callable, Type, List
import random

from repair.trace import Trace


class GrammarTerminal:
    def __init__(self, name: str,
                 value_fn: Callable,
                 return_type: Type,
                 display_name: str = None):
        self.name = name
        self.value_fn = value_fn  # Callable producing terminal value
        self.return_type = return_type
        self.display_name = display_name or name

# Static numeric terminals (fixed values)
GRAMMAR_STATIC_TERMINALS = [
    GrammarTerminal("const_-10", lambda: -10.0, float, display_name="-10"),
    GrammarTerminal("const_0", lambda: 0.0, float, display_name="0"),
    GrammarTerminal("const_10", lambda: 10.0, float, display_name="10"),
]

# Ephemeral numeric terminals (randomly sampled each individual)
GRAMMAR_EPHEMERAL_TERMINALS = [
    GrammarTerminal("rand_float", lambda: random.uniform(-10, 10), float, display_name="rand(-10, 10)"),
]

