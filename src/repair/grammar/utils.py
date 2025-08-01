from repair.grammar.grammar import TERMINAL_NAMES, DISPLAY_MAP
from deap import gp

def to_infix(individual, approach):

    ARG_NAMES = {}
    for i, var_name in enumerate(approach.trace_suite.variable_names):
        ARG_NAMES[f"ARG{i}"] = var_name

    def recurse(node, iterator):
        if isinstance(node, gp.Terminal):
            name = getattr(node, "name", None)

            # TODO very hacky way to handle ARG0, ARG1, ...             
            if name in ARG_NAMES:
                # Replace ARG0 with 'x'
                name = ARG_NAMES[name]
            if name in TERMINAL_NAMES:
                name = str(node.value)
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

