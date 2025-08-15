from abc import ABC, abstractmethod

from repair.approach.requirement import PreCondition, PostCondition, Requirement
from repair.grammar import grammar
from repair.fitness.desirability.desirability import Desirability
from repair.approach.trace import TraceSuite
from deap import base, creator, gp, tools
from repair.approach.optimization import expressiongenerator
from repair.fitness import correctness


# TODO complete below, once we have multiple approaches
class Approach(ABC):
    """
    Base class for requirement repair approaches.
    """

    def __init__(self, trace_suite: TraceSuite, requirement_text: tuple[str, str], desirability: Desirability=None):
    
        self.trace_suite = trace_suite
        self.desirability = desirability

        self.pset_pre, self.pset_post= grammar.get_gp_primitive_sets(self.trace_suite)
        self.toolbox = self.init_toolbox()

        # Process initial requirement
        self.init_requirement = Requirement(
            PreCondition("Initial", self.pset_pre, self.toolbox, trace_suite, requirement_text[0]),
            PostCondition("Initial", self.pset_post, self.toolbox, trace_suite, requirement_text[1])
        )

        # Handle desirability
        self.desirability.initial_requirement = self.init_requirement

    def init_toolbox(self):
        toolbox = base.Toolbox()

        # (1) Generator for pre and post repairs
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr_pre", expressiongenerator.generate_expr, pset=self.pset_pre, min_=2, max_=3)
        toolbox.register("expr_post", expressiongenerator.generate_expr, pset=self.pset_post, min_=2, max_=3)
        # TODO does the expressiongenerator belong to the subclass?

        # (2) Compilation
        toolbox.register("compile_pre", gp.compile, pset=self.pset_pre)
        toolbox.register("compile_post", gp.compile, pset=self.pset_post)

        # (3) Metrics
        toolbox.register("evaluate_cor", correctness.get_fitness_correctness,
                         trace_suite=self.trace_suite, # this is fixed throughout execution
        )
        toolbox.register("evaluate_des", self.desirability.evaluate)
        toolbox.register("evaluate_des_tuple", self.desirability.get_desirability_tuple)
        return toolbox

    @abstractmethod
    def repair(self, threshold):
        pass

# TODO this could be useful for the future
# class AlgorithmicApproach(Approach):
#     """
#     Exact approach for requirement repair.
#     """

#     def __init__(self, requirement, transformations):
#         super().__init__(requirement)

#     def repair(self, requirement, transformations):
#         # Implement exact repair logic here
#         print("Repairing requirement using exact approach.")
#         # Placeholder return
#         return requirement
    
    