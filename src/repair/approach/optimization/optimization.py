from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.approach.requirement import Requirement
from repair.approach.optimization import expressiongenerator

logger = logging.getLogger("gp_logger")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, desirability):
        super().__init__(trace_suite, requirement_text, desirability)

        self._init_creator()
        self._add_to_toolbox()
       
        # TODO: check lt and gt robustness, a value of zero should be wrong there

    def _init_creator(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # Minimize both objectives
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    def _add_to_toolbox(self):
        # super().init_toolbox(pset_id)

        # Add approach-specific registrations
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr_post) # TODO alternate between pre and post randomly
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("select", tools.selNSGA2)
        self.toolbox.register("mate", gp.cxOnePoint)
        # if min_=0, then this requires a False or true terminal. Not supported.
        self.toolbox.register("expr_mut", expressiongenerator.generate_expr, min_=1, max_=2, condition_str="full")
        self.toolbox.register("mutate_pre", gp.mutUniform, expr=self.toolbox.expr_mut, pset=self.pset_pre)
        self.toolbox.register("mutate_post", gp.mutUniform, expr=self.toolbox.expr_mut, pset=self.pset_post)

        # Decorators to limit tree size
        self.toolbox.decorate("mate", gp.staticLimit(key=len, max_value=10))
        self.toolbox.decorate("mutate_pre", gp.staticLimit(key=len, max_value=10))
        self.toolbox.decorate("mutate_post", gp.staticLimit(key=len, max_value=10))

    def _repair(self):
        toolbox = self.toolbox
        pop = toolbox.population(n=10) # Random initial population # TODO adjust number
        hof = tools.ParetoFront() # Hall of Fame, for keeping track of the best individuals

        # (Initial) Evaluation
        for ind in pop:
            f_cor = toolbox.evaluate_cor(ind)[0] # TODO add support for pre=>post
            f_des = toolbox.evaluate_des(ind, 1) # TODO add support for random pre vs post
            ind.fitness.values = (f_cor, f_des)

        pop = toolbox.select(pop, len(pop))

        # Evolutionary loop: run for a fixed number of generations
        # TODO review this loop entirely
        for gen in tqdm(range(5)):
            offspring = toolbox.select(pop, len(pop)) # Selection
            offspring = list(map(toolbox.clone, offspring))  # Deep copy the individuals

            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.5:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in offspring:
                if random.random() < 0.3:
                    toolbox.mutate_post(mutant) # TODO add support for random pre vs post
                    del mutant.fitness.values

            # (Re-)evaluation: only individuals whose fitness has changed
            for ind in offspring:
                if not ind.fitness.valid:
                    f_cor = toolbox.evaluate_cor(ind)[0] # TODO add support for pre=>
                    f_des = toolbox.evaluate_des(ind, 1) # TODO add support for random pre vs post
                    ind.fitness.values = (f_cor, f_des)

            # Selection
            pop = toolbox.select(pop + offspring, len(pop))
            hof.update(pop) # Update the best-so-far individual

            logger.info(f"Generation {gen}: Pareto size = {len(hof)}")

            # If an individual is perfectly correct and perfectly desirable
            # stop early. This is theoretically impossible for a faulty input requirement
            if any(f_cor == 0 and f_des == 0 for f_cor, f_des in (ind.fitness.values for ind in pop)):
                break

        return hof

    def repair(self, threshold):
        # TODO: For now, I am only considering the single best repaired individual
        # wrt. correctness. extend this to support multiple repaired individuals (?)

        repaired_req = Requirement("Repaired", self.toolbox, self.trace_suite)

        repaired = False
        if (self.init_requirement.correctness[0][1] * 100) < threshold:
            hof_repaired = self._repair()
            best_repaired = min(hof_repaired, key=lambda x: x.fitness.values[0])
            repaired_req.set_pre(self.pset_pre, best_repaired)
            repaired = True
        else:
            repaired_req.set_pre(self.pset_pre, self.init_requirement.pre)

        if (self.init_requirement.correctness[1][1] * 100) < threshold:
            hof_repaired = self._repair()
            # ordered_hof = sorted(hof_repaired, key=lambda ind: ind.fitness.values[0])
            # print(len(hof_repaired))
            # for ind in ordered_hof:
            #     print(ind.fitness.values)
            # print('-------------------')
            best_repaired = min(hof_repaired, key=lambda x: x.fitness.values[0])
            repaired_req.set_post(self.pset_post, best_repaired)
            repaired = True
        else:
            repaired_req.set_post(self.pset_post, self.init_requirement.post)

        return repaired_req if repaired else None
