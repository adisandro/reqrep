from repair.grammar.functions import GRAMMAR_FUNCTIONS
from repair.grammar.terminals import GRAMMAR_EPHEMERAL_TERMINALS, GRAMMAR_STATIC_TERMINALS
from deap import gp

from repair.utils import Bool, Float

def getGPPrimitiveSet(variable_names):

    pset = gp.PrimitiveSetTyped("MAIN", [Float] * len(variable_names), Bool)

    # VARIABLES
    for i, var_name in enumerate(variable_names):
        pset.renameArguments(**{f"ARG{i}": var_name})

    ## OPERATORS
    for func in GRAMMAR_FUNCTIONS:
        pset.addPrimitive(func.impl, func.input_types, func.return_type, name=func.name)

    # TERMINALS
    for ter in GRAMMAR_STATIC_TERMINALS:
        pset.addTerminal(ter.generate_value(), ter.return_type)

    # EPHEMERAL CONSTANTS
    for eph in GRAMMAR_EPHEMERAL_TERMINALS:
        pset.addEphemeralConstant(eph.name, eph.value_fn, eph.return_type)
    
    return pset