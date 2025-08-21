import random

from repair.approach.approach import Approach
from repair.approach.requirement import Requirement
from repair.approach.transformation.library import ChangeConstant


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
            candidate = random.choice(transformations).transform(self.init_requirement.post)
            candidates.append(candidate)
        best = min(candidates, key=lambda c:self.toolbox.evaluate_cor(self.init_requirement.pre, c)["post_cor"][0])

        return Requirement("Repaired", self.toolbox, self.pset_pre, self.init_requirement.pre, self.pset_post, best)
