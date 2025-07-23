from repair.grammar.functions import GRAMMAR_FUNCTIONS
from repair.grammar.terminals import GRAMMAR_EPHEMERAL_TERMINALS, GRAMMAR_STATIC_TERMINALS, GrammarTerminal
from deap import gp

def getGPPrimitiveSet(variable_names):

    pset = gp.PrimitiveSetTyped("MAIN", [float] * len(variable_names), bool)

    # VARIABLES
    for i, var_name in enumerate(variable_names):
        pset.renameArguments(**{f"ARG{i}": var_name})

    ## OPERATORS
    for func in GRAMMAR_FUNCTIONS:
        pset.addPrimitive(func.impl, func.input_types, func.return_type, name=func.name)

    # TERMINALS
    for ter in GRAMMAR_STATIC_TERMINALS:
        pset.addTerminal(ter.value_fn(), ter.return_type)
    for var_name in variable_names:
        ter = GrammarTerminal(f"prev_{var_name}", lambda: None, float, display_name=f"prev({var_name})")
        GRAMMAR_STATIC_TERMINALS.append(ter)
        pset.addTerminal(ter.value_fn(), ter.return_type, name=f"prev({var_name})")

    # EPHEMERAL CONSTANTS
    for eph in GRAMMAR_EPHEMERAL_TERMINALS:
        pset.addEphemeralConstant(eph.name, eph.value_fn, eph.return_type)
    
    return pset