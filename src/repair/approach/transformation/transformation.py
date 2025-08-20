import copy
import random
from abc import ABC, abstractmethod

from deap import gp
from repair.approach.approach import Approach
from repair.approach.requirement import Requirement


class Transformation(ABC):
    def __init__(self, approach):
        self.approach = approach

    @abstractmethod
    def transform(self, condition):
        return gp.PrimitiveTree.from_string(condition.__str__(), self.approach.pset_post)


class ChangeConstant(Transformation):
    def __init__(self, approach):
        super().__init__(approach)

    def transform(self, condition):
        transformed = super().transform(condition)
        constants = [node for node in transformed if isinstance(node, gp.Terminal) and isinstance(node.value, float)]
        constant = random.choice(constants)
        constant.value = constant.value + random.uniform(-constant.value, constant.value)

        return transformed


class TransformationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, iterations, desirability):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

    def repair(self, threshold):
        to_repair = self.init_requirement.correctness["cor"][1] * 100 < threshold
        if not to_repair:
            return None

        candidates = []
        transformations = [ChangeConstant(self)]
        for i in range(self.iterations):
            candidate = random.choice(transformations)(self.init_requirement.post)
            candidates.append(candidate)
        best = min(candidates, key=lambda c:self.toolbox.evaluate_cor(self.init_requirement.pre, c)["post_cor"][0])

        return Requirement("Repaired", self.toolbox, self.pset_pre, self.init_requirement.pre, self.pset_post, best)
