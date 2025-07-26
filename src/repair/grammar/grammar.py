from repair.grammar.functions import GrammarFunction, Bool
from repair.grammar.terminals import GrammarTerminal
from deap import gp

GRAMMAR_FUNCTIONS = []
GRAMMAR_STATIC_TERMINALS = []
GRAMMAR_EPHEMERAL_TERMINALS = []
ROBUSTNESS_FN_MAP = {}
DISPLAY_MAP = {}
TERMINAL_NAMES = set()

def getGPPrimitiveSet(trace_suite):
    global GRAMMAR_FUNCTIONS, GRAMMAR_STATIC_TERMINALS, GRAMMAR_EPHEMERAL_TERMINALS, ROBUSTNESS_FN_MAP, DISPLAY_MAP,\
           TERMINAL_NAMES

    pset = gp.PrimitiveSetTyped("MAIN", [float] * len(trace_suite.variable_names), Bool)

    # VARIABLES
    for i, var_name in enumerate(trace_suite.variable_names):
        pset.renameArguments(**{f"ARG{i}": var_name})

    ## OPERATORS
    GRAMMAR_FUNCTIONS = GrammarFunction.create_functions()
    for func in GRAMMAR_FUNCTIONS:
        pset.addPrimitive(func.impl, func.input_types, func.return_type, name=func.name)
        ROBUSTNESS_FN_MAP[func.name] = func.robustness_fn
        DISPLAY_MAP[func.name] = func.display_name

    # TERMINALS
    GRAMMAR_STATIC_TERMINALS = GrammarTerminal.create_terminals(trace_suite)
    for ter in GRAMMAR_STATIC_TERMINALS:
        name = ter.display_name if ter.name.startswith("prev") else None
        pset.addTerminal(ter.value_fn(), ter.return_type, name=name)
        TERMINAL_NAMES.add(ter.name)

    # EPHEMERAL CONSTANTS
    GRAMMAR_EPHEMERAL_TERMINALS = GrammarTerminal.create_ephemerals(trace_suite)
    for eph in GRAMMAR_EPHEMERAL_TERMINALS:
        pset.addEphemeralConstant(eph.name, eph.value_fn, eph.return_type)
        TERMINAL_NAMES.add(eph.name)

    return pset