from abc import ABC, abstractmethod

from repair.approach.approachConfig import ApproachConfig
from repair.approach.requirement import Requirement
from repair.grammar import grammar
from repair.fitness.desirability.desirability import Desirability
from repair.approach.trace import TraceSuite
from deap import base, gp
from repair.approach.optimization import expressiongenerator
from repair.fitness.correctness import correctness


# TODO complete below, once we have multiple approaches
class Approach(ABC):
    """
    Base class for requirement repair approaches.
    """

    def __init__(self, trace_suite: TraceSuite, requirement_text: tuple[str, str], iterations: int,
                 numbers_factor: float, desirability: Desirability=None, config:ApproachConfig=None):
    
        self.trace_suite = trace_suite
        self.iterations = iterations
        self.desirability = desirability
        self.config = config

        self.pset_pre, self.pset_post= grammar.get_gp_primitive_sets(self.trace_suite, numbers_factor)
        self.toolbox = self.init_toolbox()
        self.init_requirement = Requirement("Initial", self.toolbox, self.pset_pre, requirement_text[0],
                                            self.pset_post, requirement_text[1])

        # Handle desirability
        if self.desirability is not None:
            self.desirability.initial_requirement = self.init_requirement

    def init_toolbox(self):
        toolbox = base.Toolbox()

        # (1) Generator for pre and post repairs
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr_pre", expressiongenerator.generate_expr,
                         pset=self.pset_pre,
                         min_=self.config.pre_tree_min_depth,
                         max_=self.config.pre_tree_max_depth)
        toolbox.register("expr_post", expressiongenerator.generate_expr,
                         pset=self.pset_post, 
                         min_=self.config.post_tree_min_depth,
                         max_=self.config.post_tree_max_depth)
        # TODO does the expressiongenerator belong to the subclass?

        # (2) Compilation
        toolbox.register("compile_pre", gp.compile, pset=self.pset_pre)
        toolbox.register("compile_post", gp.compile, pset=self.pset_post)

        # (3) Metrics
        toolbox.register("get_sat_deg", correctness.get_satisfaction_degrees, trace_suite=self.trace_suite)
        toolbox.register("get_fitness_correctness", correctness.get_fitness_correctness)
        if self.desirability is not None:
            toolbox.register("get_fitness_desirability", self.desirability.evaluate)
            toolbox.register("get_raw_desirability", self.desirability.get_raw_desirability_tuple)
        return toolbox

    @abstractmethod
    def repair(self):
        pass
    