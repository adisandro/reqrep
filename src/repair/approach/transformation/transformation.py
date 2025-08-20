from repair.approach.approach import Approach


class TransformationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, iterations, desirability):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

    def repair(self, threshold):
        for i in range(self.iterations):
            pass
