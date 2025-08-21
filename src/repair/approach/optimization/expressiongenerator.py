import random
from deap import gp

from repair.grammar.functions import Bool


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
        expr_candidates = [ter for ter in pset.terminals[type_]] # always add terminals
        if not condition(height, depth): # add primitives too
            # If thereare 2 depth levels levels remaining,
            # we can only use primitives that do not take bool arguments
            # to avoid False or True terminals, which mess everything up
            remaining_layers = height - depth
            expr_candidates.extend([
                prim for prim in pset.primitives[type_]
                if not (remaining_layers <= 2 and any(arg == Bool for arg in prim.args))])
        if len(expr_candidates) == 0:
            raise LookupError(f"Could not find any {type_} terminal or primitive to create expression")
        expr_choice = random.choice(expr_candidates)
        if type(expr_choice) is gp.MetaEphemeral:
            expr_choice = expr_choice()
        elif type(expr_choice) is gp.Primitive:
            for arg in reversed(expr_choice.args):
                stack.append((depth + 1, arg))
        expr.append(expr_choice)
    return expr

