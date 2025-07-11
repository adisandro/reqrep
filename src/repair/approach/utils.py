# TODO Fix this.some theoretical stuff to do here
# TODO how about multiple fitness values?
# Fitness function: count how many time steps FAIL the requirement
def eval_requirement(individual, traces, compile_func, variable_names):

    # TODO Improve this sanity check
    if not any(var in str(individual) for var in variable_names):
        return (float("inf"),)

    func = compile_func(expr=individual)
    violations = 0

    try:
        for trace in traces:
            for item in trace.items:

                # TODO need to expand this with temporal operators
                inputs = [float(item.values[var]) for var in variable_names]
                outcome = func(*inputs)
                if not outcome:
                    violations += 1
    except Exception:
        raise ValueError(f"Error evaluating individual: {individual}.")

    return (violations,)
    
    # print(fitness)
    # print()
    return (fitness,)