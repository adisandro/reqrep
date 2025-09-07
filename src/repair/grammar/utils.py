from repair.grammar.grammar import DISPLAY_MAP
from deap import gp

def to_infix(individual, trace_suite):
    def recurse(node, iterator):
        if isinstance(node, gp.Terminal):
            name = node.name
            if isinstance(node.value, str):
                name = node.value
            return name
        elif isinstance(node, gp.Primitive):
            args = [recurse(next(iterator), iterator) for _ in range(node.arity)]
            name = DISPLAY_MAP.get(node.name, node.name)
            if node.arity == 1:
                return f"({name} {args[0]})"
            elif node.arity == 2:
                return f"({args[0]} {name} {args[1]})"
            else:
                return f"{name}({', '.join(args)})"

    it = iter(individual)
    return recurse(next(it), it)

