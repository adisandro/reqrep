from functools import cached_property

import repair.grammar.utils as grammar_utils
from deap import gp
from functools import cached_property


class Requirement:
    __slots__ = ("name", "toolbox", "pre", "post", "__dict__")
    
    def __init__(self, name, toolbox, pset_pre, precond, pset_post, postcond):
        self.name = name
        self.toolbox = toolbox
        self.pre = self._set_condition(pset_pre, precond)
        self.post = self._set_condition(pset_post, postcond)

    def _set_condition(self, pset, condition):
        return gp.PrimitiveTree.from_string(condition, pset) if isinstance(condition, str)\
            else condition

    def get_condition(self, pre_post_id):
        if pre_post_id == 0:
            return self.pre
        elif pre_post_id == 1:
            return self.post
        else:
            raise ValueError("Invalid pre_post_id")

    @cached_property
    def correctness(self):
        return self.toolbox.evaluate_cor(self.pre, self.post)

    @cached_property
    def desirability(self):
        if not hasattr(self.toolbox, "evaluate_des"):
            return {"des": None, "tuple": None}
        return self.toolbox.evaluate_des(self)
    
    def __repr__(self):
        return f"Requirement(name={self.name}, pre={self.pre}, post={self.post})"

    def to_str(self, trace_suite):
        pre_infix = grammar_utils.to_infix(self.pre, trace_suite)
        post_infix = grammar_utils.to_infix(self.post, trace_suite)

        # correctness
        c_delta, c_perc = self.correctness["cor"]
        c_pre_delta, c_pre_perc = self.correctness["pre_cor"]
        c_post_delta, c_post_perc = self.correctness["post_cor"]

        return (
            f"{self.name}:\n"
            f"\t{pre_infix}\t=>\t{post_infix}\n"
            f"\t{self.pre}\t=>\t{self.post}\n"
            f"\tCorrectness: Δ = {c_delta}, % = {c_perc*100}\n"
            f"\tPre-correctness: Δ = {c_pre_delta}, % = {c_pre_perc*100}\n"
            f"\tPost-correctness: Δ = {c_post_delta}, % = {c_post_perc*100}\n"
            f"\tDesirability: {self.desirability["tuple"]}\n")

