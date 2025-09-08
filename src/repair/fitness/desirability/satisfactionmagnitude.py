from repair.fitness.desirability.desirability import SatisfactionExtent


class TraceSuiteSatisfactionMagnitude(SatisfactionExtent):
    def evaluate(self, trace_suite, current_req) -> float:
        # NOTE: this is temp. Worst case satisfaction

        sd = current_req.satisfaction_degrees["sd"][0]
        return abs(sd)
