# TODO Fix this.some theoretical stuff to do here
# TODO how about multiple fitness values?
# Fitness function: count how many time steps FAIL the requirement
def eval_requirement(individual, traces, compile_func):

    # TODO Improve this sanity check
    # Ensure the individual contains the variable 'x'
    if "x" not in str(individual):
        return (float("inf"),)

    func = compile_func(expr=individual)
    fitness = 0
    try:
        # add support for arbitrary variables
        for trace in traces:
            for item in trace.items:
                # TODO need to expand this with temporal operators
                x = float(item.values['x'])

                if not func(x):
                    # If the function fails for this trace item, increment the fitness
                    fitness += 1
    except Exception as e:
        raise ValueError(f"Error evaluating individual: {individual}.")
    
    return (fitness,)