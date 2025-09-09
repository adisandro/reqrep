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

    @staticmethod
    def _set_condition(pset, condition):
        return gp.PrimitiveTree.from_string(condition, pset) if isinstance(condition, str) else condition

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
    
    def raw_desirability(self):
        if not hasattr(self.toolbox, "get_raw_desirability"):
            return None
        return self.toolbox.get_raw_desirability(self)

    def __repr__(self):
        return f"Requirement(name={self.name}, pre={self.pre}, post={self.post})"

    def to_str(self, trace_suite, digits=3):
        merged_infix = grammar_utils.to_infix(self.merged, trace_suite)

        # correctness
        impl_sd, impl_item_perc, impl_item_viol, impl_t_perc, impl_trace_viol = self.satisfaction_degrees["sd"]
        pre_sd,  pre_item_perc,  pre_item_viol,  pre_t_perc,  pre_trace_viol  = self.satisfaction_degrees["pre_sd"]
        post_sd, post_item_perc, post_item_viol, post_t_perc, post_trace_viol = self.satisfaction_degrees["post_sd"]

        return (
            f"{self.name}:\n"
            f"\t{merged_infix}\n"
            f"\t{self.merged}\n"
            f"\tSAT DEG - Pre=>Post:            Δ = {impl_sd:<8.{digits}f}, %_it_suc = {impl_item_perc*100:<8.{digits}f}, #_it_vio = {impl_item_viol:<5}, %_tr_suc = {impl_t_perc*100:<8.{digits}f}, #_tr_vio = {impl_trace_viol:<5}\n"
            f"\tSAT DEG - Pre:                  Δ = {pre_sd:<8.{digits}f}, %_it_suc = {pre_item_perc*100:<8.{digits}f}, #_it_vio = {pre_item_viol:<5}, %_tr_suc = {pre_t_perc*100:<8.{digits}f}, #_tr_vio = {pre_trace_viol:<5}\n"
            f"\tSAT DEG - Post:                 Δ = {post_sd:<8.{digits}f}, %_it_suc = {post_item_perc*100:<8.{digits}f}, #_it_vio = {post_item_viol:<5}, %_tr_suc = {post_t_perc*100:<8.{digits}f}, #_tr_vio = {post_trace_viol:<5}\n"
            f"\tFITNESS - Correctness (value):  {self.correctness:<8.{digits}f}\n"
            f"\tFITNESS - Correctness (truth):  {self.correctness == 0}\n"
            f"\tFITNESS - Des (raw dims):       {[f'{i}={v:.{digits}f}' for i, v in zip(DIMENSION_IDS, self.raw_desirability())]}\n"
            f"\tFITNESS - Des (weighted dims):  {[f'{i}={v:.{digits}f}' for i, v in zip(DIMENSION_IDS, self.desirability['tuple'])]}\n"
            f"\tFITNESS - Des (weighted sum):   {self.desirability['des']:.{digits}f}\n"
        )

