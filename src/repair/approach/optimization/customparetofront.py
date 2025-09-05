from deap.tools import ParetoFront
from bisect import bisect_right

class LightweightParetoFront(ParetoFront):
    def __init__(self):
        super().__init__()

    def insert(self, item):
        """
        Copied from, DEAP's HallOfFame class
        Changed the deepcopy into a lightweight representation
        """

        # item = deepcopy(item)
        item = LightweightRequirement(item)
        i = bisect_right(self.keys, item.fitness)
        self.items.insert(len(self) - i, item)
        self.keys.insert(i, item.fitness)

class LightweightRequirement:
    def __init__(self, item):
        self.pre = str(item.pre)
        self.post = str(item.post)
        self.fitness = item.fitness