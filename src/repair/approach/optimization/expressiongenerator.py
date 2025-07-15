import random
import sys
from deap import gp

def get_condition_from_string(condition: str):
    """
    Converts a string condition to a callable function.
    """
    if condition == "full":
        return lambda height, depth: depth == height
    elif condition == "grow":
        return lambda height, depth: depth == height or (depth >= 2 and random.random() < 0.5)
    else:
        raise ValueError(f"Unknown condition: {condition}")

def generate_expr(pset, min_, max_, type_=None, condition_str:str=None):

    if condition_str is None:
        # Randomly choose between full and grow conditions
        # condition = random.choice((condition_full, condition_grow))
        # For now, use only full condition
        condition_str = random.choice(("full", "grow"))
    
    condition = get_condition_from_string(condition_str)

    if type_ is None:
        type_ = pset.ret
    expr = []
    height = random.randint(min_, max_)
    stack = [(0, type_)]
    while len(stack) != 0:
        depth, type_ = stack.pop()
        if condition(height, depth):
            try:
                term = random.choice(pset.terminals[type_])
            except IndexError:
                _, _, traceback = sys.exc_info()
                raise IndexError("The gp.generate function tried to add "
                                 "a terminal of type '%s', but there is "
                                 "none available." % (type_,)).with_traceback(traceback)
            if type(term) is gp.MetaEphemeral:
                term = term()
            expr.append(term)
        else:
            # If thereare 2 depth levels levels remaining,
            # we can only use primitives that do not take bool arguments
            # to avoid False or True terminals, which mess everything up
            remaining_layers = height - depth
            primitives = [
                prim for prim in pset.primitives[type_]
                if not (remaining_layers <= 2 and any(arg == bool for arg in prim.args))
            ]
            try:
                prim = random.choice(primitives)
            except IndexError:
                _, _, traceback = sys.exc_info()
                raise IndexError("The gp.generate function tried to add "
                                 "a primitive of type '%s', but there is "
                                 "none available." % (type_,)).with_traceback(traceback)
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((depth + 1, arg))
    return expr

