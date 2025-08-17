from repair.approach.approach import Approach


class TransformationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, desirability):
        super().__init__(trace_suite, requirement_text, desirability)

    def repair(self, threshold):
        pass
