import random
from abc import ABC, abstractmethod

from deap import gp


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
        constant.name = str(constant.value)

        return transformed
