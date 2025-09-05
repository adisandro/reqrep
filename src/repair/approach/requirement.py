from functools import cached_property

from repair.fitness.desirability.desirability import DIMENSION_IDS
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
        self.implies_primitive = pset_post.mapping['implies']

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
    def merged(self):
        return gp.PrimitiveTree([self.implies_primitive] + list(self.pre) + list(self.post))

    @cached_property
    def satisfaction_degrees(self):
        return self.toolbox.get_sat_deg(self.pre, self.post)

    @cached_property
    def correctness(self):
        return self.toolbox.get_fitness_correctness(self.satisfaction_degrees)

    @cached_property
    def desirability(self):
        if not hasattr(self.toolbox, "get_fitness_desirability"):
            return {"des": None, "tuple": None}
        return self.toolbox.get_fitness_desirability(self)

    def __repr__(self):
        return f"Requirement(name={self.name}, pre={self.pre}, post={self.post})"

    def to_str(self, trace_suite):
        merged_infix = grammar_utils.to_infix(self.merged, trace_suite)

        # correctness
        sd_delta, sd_perc, sd_count = self.satisfaction_degrees["sd"]
        sd_pre_delta, sd_pre_perc, sd_pre_count = self.satisfaction_degrees["pre_sd"]
        sd_post_delta, sd_post_perc, sd_post_count = self.satisfaction_degrees["post_sd"]

        return (
            f"{self.name}:\n"
            f"\t{merged_infix}\n"
            f"\t{self.merged}\n"
            f"\tSAT DEG - Pre=>Post:    Δ = {sd_delta}, % = {sd_perc*100}, # = {sd_count}\n"
            f"\tSAT DEG - Pre:          Δ = {sd_pre_delta}, % = {sd_pre_perc*100}, # = {sd_pre_count}\n"
            f"\tSAT DEG - Post:         Δ = {sd_post_delta}, % = {sd_post_perc*100}, # = {sd_post_count}\n"

            f"\tFITNESS - Correctness:  {self.correctness}\n"
            f"\tFITNESS - Desirability: {[f'{i}={round(v, 3)}' for i, v in zip(DIMENSION_IDS, self.desirability['tuple'])]}\n"
            f"\tFITNESS - Desirability: {self.desirability['des']}\n")

