from repair.fitness.correctness.utils import is_within_margin
from repair.fitness.desirability.desirability import SatisfactionExtent


class TraceSuiteSatisfactionMagnitude(SatisfactionExtent):
    def evaluate(self, current_req) -> float:
        '''
        Returns:
            0.0 → perfect satisfaction (sd=0.0)
            >0.0 → otherwise
        '''
        # NOTE: this is temp. Worst case satisfaction

        sd = current_req.satisfaction_degrees["sd"][0]
        return abs(sd)
    
class AvoidAbsoluteSatisfaction(SatisfactionExtent):
    def evaluate(self, current_req, initial_req) -> float:
        '''
        Returns:
            0.0 → (pre_sd=0.0 or (pre_sd=1.0 and post_sd=1.0))
            1.0 → otherwise
        '''

        pre_sat_ratio_of_items = current_req.satisfaction_degrees["pre_sd"][1]
        post_sat_ratio_of_items = current_req.satisfaction_degrees["post_sd"][1]
        pre_sat_ratio_of_traces = current_req.satisfaction_degrees["pre_sd"][3]
        post_sat_ratio_of_traces = current_req.satisfaction_degrees["post_sd"][3]

        pre_relevant = pre_sat_ratio_of_items
        post_relevant = post_sat_ratio_of_items

        if is_within_margin(pre_relevant, 0.0) or \
            (is_within_margin(post_relevant, 1.0) and is_within_margin(post_relevant, 1.0)):
            return 1.0
        else:
            return 0.0
        

class VerticalAndHorizontalExtent(SatisfactionExtent):
    def __init__(self):
        super().__init__()
        self.vertical = TraceSuiteSatisfactionMagnitude()
        self.horizontal = AvoidAbsoluteSatisfaction()

    def get_two_components(self, current_req, initial_req):
        result_vertical = self.vertical.evaluate(current_req) # [0, inf)
        normalized_vertical = result_vertical/(1.0+result_vertical) # [0, 1)

        result_horizontal = self.horizontal.evaluate(current_req, initial_req) # {0.0, 1.0}
        return normalized_vertical, result_horizontal

    def evaluate(self, current_req, initial_req):
        result_vertical, result_horizontal = self.get_two_components(current_req, initial_req)

        result_combined = 0.5*result_vertical + 0.5*result_horizontal
        return result_combined


# class PreconditionSatisfaction(SatisfactionExtent):
#     def evaluate(self, current_req, initial_req) -> float:
#         pre_sd = current_req.satisfaction_degrees["pre_sd"][0]
#         return max(0, -pre_sd)
    

    