from abc import ABC, abstractmethod

from repair.approach.requirement import Condition, Requirement
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
        self.psets = grammar.get_gp_primitive_sets(self.trace_suite)
        self.toolboxes = self.init_toolbox(0), self.init_toolbox(1) # TODO: should we have pre_toolbox and post_toolbox separately?

        # Process initial requirement
        self.init_requirement = Requirement(
            Condition("Initial PRE", self.psets[0], self.toolboxes[0], trace_suite, requirement_text[0]),
            Condition("Initial POST", self.psets[1], self.toolboxes[1], trace_suite, requirement_text[1])
        )

        # Handle desirability
        self.desirability = desirability
        self.add_desirability_to_toolboxes()

    def init_toolbox(self, pset_id):
        toolbox = base.Toolbox()
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr", expressiongenerator.generate_expr, pset=self.psets[pset_id], min_=2, max_=3)
        # TODO does the expressiongenerator beong to the subclass?
        toolbox.register("compile", gp.compile, pset=self.psets[pset_id])

        toolbox.register("evaluate_cor", correctness.get_fitness_correctness,
                         trace_suite=self.trace_suite, # this is fixed throughout execution
        )
        return toolbox
    
    def add_desirability_to_toolboxes(self):
        for toolbox in self.toolboxes:
            toolbox.register("evaluate_des", self.desirability.evaluate,
                             original=None,  # TODO: add original requirement
            )

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
    
    