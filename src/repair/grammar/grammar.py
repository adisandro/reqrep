from repair.grammar.functions import GrammarFunction, Bool
from repair.grammar.terminals import GrammarTerminal
from deap import gp

GRAMMAR_FUNCTIONS = []
GRAMMAR_STATIC_TERMINALS = []
GRAMMAR_EPHEMERAL_TERMINALS = []
ROBUSTNESS_FN_MAP = {}
DISPLAY_MAP = {}
TERMINAL_NAMES = set()

def get_gp_primitive_sets(trace_suite):
    global GRAMMAR_FUNCTIONS, GRAMMAR_STATIC_TERMINALS, GRAMMAR_EPHEMERAL_TERMINALS, ROBUSTNESS_FN_MAP, DISPLAY_MAP,\
           TERMINAL_NAMES

    GRAMMAR_FUNCTIONS = GrammarFunction.create_functions()
    GRAMMAR_STATIC_TERMINALS = GrammarTerminal.create_terminals(trace_suite)
    GRAMMAR_EPHEMERAL_TERMINALS = GrammarTerminal.create_ephemerals(trace_suite)

    pset_pre = gp.PrimitiveSetTyped("PRE", [float] * len(trace_suite.in_variable_names), Bool)
    pset_post = gp.PrimitiveSetTyped("POST", [float] * len(trace_suite.variable_names), Bool)

    # VARIABLES
    for i, in_var_name in enumerate(trace_suite.in_variable_names):
        pset_pre.renameArguments(**{f"ARG{i}": in_var_name})
    for i, var_name in enumerate(trace_suite.variable_names):
        pset_post.renameArguments(**{f"ARG{i}": var_name})

    # print([f"{k}: {v.format()}|{v.name}" for k, v in pset_pre.mapping.items()])
    # print([f"{k}: {v.format()}|{v.name}" for k, v in pset_post.mapping.items()])

    ## OPERATORS
    for func in GRAMMAR_FUNCTIONS:
        ROBUSTNESS_FN_MAP[func.name] = func.robustness_fn
        DISPLAY_MAP[func.name] = func.display_name
        pset_pre.addPrimitive(func.impl, func.input_types, func.return_type, name=func.name)
        pset_post.addPrimitive(func.impl, func.input_types, func.return_type, name=func.name)

    # TERMINALS
    for ter in GRAMMAR_STATIC_TERMINALS:
        TERMINAL_NAMES.add(ter.name)
        if ter.name in trace_suite.in_variable_names:
            pset_pre.addTerminal(ter.value_fn(), ter.return_type)
        pset_post.addTerminal(ter.value_fn(), ter.return_type)

    # EPHEMERAL CONSTANTS
    for eph in GRAMMAR_EPHEMERAL_TERMINALS:
        TERMINAL_NAMES.add(eph.name)
        pset_pre.addEphemeralConstant(eph.name, eph.value_fn, eph.return_type)
        pset_post.addEphemeralConstant(eph.name, eph.value_fn, eph.return_type)

    return pset_pre, pset_post