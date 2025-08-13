# TODO: Find better location for these when introducing other approaches
from collections import namedtuple
import repair.grammar.utils as grammar_utils
from deap import gp


Requirement = namedtuple("Requirement", ["pre", "post"])
class Condition:
    def __init__(self, name, pset, toolbox, trace_suite, condition):
        self.name = name
        self.pset = pset
        self.toolbox = toolbox
        self.trace_suite = trace_suite
        self.condition = gp.PrimitiveTree.from_string(condition, pset) if isinstance(condition, str)\
            else condition

    @property
    def correctness(self):
        return self.toolbox.evaluate_cor(self.condition)

    @property
    def desirability(self):
        return self.toolbox.evaluate_des(self.condition)

    def __repr__(self):
        return (
            f"{self.name}:\n"
            f"\t{grammar_utils.to_infix(self.condition, self.trace_suite)}\n"
            f"\t{self.condition}\n"
            f"\tCorrectness: Δ = {round(self.correctness[0], 4)}, % = {self.correctness[1] * 100}\n"
            f"\tDesirability: {self.desirability}\n")