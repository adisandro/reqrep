def to_infix(expr):
    """
    Convert a GP expression to an infix string representation.
    """

    ops = {
        "add": "+",
        "sub": "-",
        "mul": "*",
        "truediv": "/",
        "lt": "<",
        "gt": ">",
        "eq": "==",
        "and_": "and",
        "or_": "or",
        "not_": "not",
    }

    ARG_NAMES = {
        "ARG0": "x",
        # TODO Add ARG1: 'y', etc. if needed. Do this dynamically.
    }

    def recurse(index):
        node = expr[index]
        name = getattr(node, "name", None)

        # TODO very hacky way to handle ARG0, ARG1, ... as well as "rand100"
        if name is None:
            # Terminal: ephemeral constant or variable name (string)
            name = str(node)
        else:
            # Replace ARG0 with 'x'
            if name in ARG_NAMES:
                name = ARG_NAMES[name]
            if name == "rand100":
                name = str(node.value)
        arity = getattr(node, "arity", 0)

        if arity == 0:
            return name, index + 1
        elif arity == 1:
            arg1, next_index = recurse(index + 1)
            op = ops.get(name, name)
            return f"({op} {arg1})", next_index
        elif arity == 2:
            arg1, next_index = recurse(index + 1)
            arg2, next_index = recurse(next_index)
            op = ops.get(name, name)
            return f"({arg1} {op} {arg2})", next_index
        else:
            children = []
            next_index = index + 1
            for _ in range(arity):
                child_str, next_index = recurse(next_index)
                children.append(child_str)
            return f"{name}({', '.join(children)})", next_index

    infix_str, _ = recurse(0)
    return infix_str

