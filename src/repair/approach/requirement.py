import repair.grammar.utils as grammar_utils
from deap import gp


class Requirement:
    
    def __init__(self, name, toolbox, trace_suite):
        self.name = name
        self.toolbox = toolbox
        self.trace_suite = trace_suite
        self.pre = None # TODO Temp
        self.post = None # TODO Temp

    def _set_condition(self, pset, condition):
        return gp.PrimitiveTree.from_string(condition, pset) if isinstance(condition, str)\
            else condition

    def set_pre(self, pset, condition):
        self.pre = self._set_condition(pset, condition)

    def set_post(self, pset, condition):
        self.post = self._set_condition(pset, condition)

    def get_condition(self, pre_post_id):
        if pre_post_id == 0:
            return self.pre
        elif pre_post_id == 1:
            return self.post
        else:
            raise ValueError("Invalid pre_post_id")

    @property
    def correctness(self):
        # TODO
        return (self.toolbox.evaluate_cor(self.pre),
                self.toolbox.evaluate_cor(self.post))

    @property
    def desirability(self):
        # TODO
        return (self.toolbox.evaluate_des_tuple(self.pre, 0),
                self.toolbox.evaluate_des_tuple(self.post, 1))
    
    def __repr__(self):
        # infix
        pre_infix = grammar_utils.to_infix(self.pre, self.trace_suite)
        post_infix = grammar_utils.to_infix(self.post, self.trace_suite)

        # correctness
        c_delta = (self.correctness[0][0], self.correctness[1][0])
        c_perc = (self.correctness[0][1]*100, self.correctness[1][1]*100)

        return (
            f"{self.name}:\n"
            f"\t{pre_infix}\t=>\t{post_infix}\n"
            f"\t{self.pre}\t=>\t{self.post}\n"
            f"\tCorrectness: Δ = {c_delta}, % = {c_perc}\n"
            f"\tDesirability: {self.desirability}\n")

