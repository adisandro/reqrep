from abc import ABC, abstractmethod

from repair.fitness.desirability.desirability import Desirability
from repair.trace import TraceSuite


# TODO complete below, once we have multiple approaches
class Approach(ABC):
    """
    Base class for requirement repair approaches.
    """

    def __init__(self, trace_suite: TraceSuite, requirement: tuple[str, str], desirability: Desirability=None):
        # TODO The pset probably belongs here, as it is used to manipulate the grammar for all approaches
        self.trace_suite = trace_suite
        self.pre_cond = requirement[0]
        self.post_cond = requirement[1]
        self.desirability = desirability

    @abstractmethod
    def repair(self):
        """
        Repair the requirement.
        """
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
    
    