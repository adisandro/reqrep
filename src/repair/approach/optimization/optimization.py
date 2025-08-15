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

        def random_individual():
            if random.random() < 0.5:
                ind = creator.Individual(self.toolbox.expr_pre())
                ind.target = "pre"
            else:
                ind = creator.Individual(self.toolbox.expr_post())
                ind.target = "post"
            return ind

        # Add approach-specific registrations
        # self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr_post)
        self.toolbox.register("individual", random_individual)    
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

    def _set_ind_fitness(self, ind):
            if ind.target == "pre":
                f_cor = self.toolbox.evaluate_cor(ind)[0]
                f_des = self.toolbox.evaluate_des(ind, 0)
            else:
                f_cor = self.toolbox.evaluate_cor(ind)[0]
                f_des = self.toolbox.evaluate_des(ind, 1)
            # f_cor = self.toolbox.evaluate_cor(ind)[0] # TODO add support for pre=>post
            # f_des = self.toolbox.evaluate_des(ind, 1) # TODO add support for pre=>post
            ind.fitness.values = (f_cor, f_des)

    def _repair(self):
        toolbox = self.toolbox
        pop = toolbox.population(n=10) # Random initial population # TODO adjust number
        hof = tools.ParetoFront() # Hall of Fame, for keeping track of the best individuals

        # (Initial) Evaluation
        for ind in pop:
            self._set_ind_fitness(ind)

        pop = toolbox.select(pop, len(pop))

        # Evolutionary loop: run for a fixed number of generations
        # TODO review this loop entirely
        for gen in tqdm(range(10)):
            offspring = toolbox.select(pop, len(pop)) # Selection
            offspring = list(map(toolbox.clone, offspring))  # Deep copy the individuals

            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.5 and child1.target == child2.target:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in offspring:
                if random.random() < 0.3:
                    if mutant.target == "pre":
                        toolbox.mutate_pre(mutant)
                    else:
                        toolbox.mutate_post(mutant)
                    del mutant.fitness.values

            # (Re-)evaluation: only individuals whose fitness has changed
            for ind in offspring:
                if not ind.fitness.valid:
                    self._set_ind_fitness(ind)

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

        to_repair = self.init_requirement.correctness[0][1] * 100 < threshold or\
              (self.init_requirement.correctness[1][1] * 100) < threshold # TODO support unified correctness

        if to_repair:
            # Run the repair
            hof_repaired = self._repair()
            best_repaired = min(hof_repaired, key=lambda x: x.fitness.values[0]) # correctness-based ranking  # TODO once correctness is unified
            if best_repaired.target == "pre":
                repaired_req.set_pre(self.pset_pre, best_repaired)
                repaired_req.set_post(self.pset_post, self.init_requirement.post)
            else:
                repaired_req.set_post(self.pset_post, best_repaired)
                repaired_req.set_pre(self.pset_pre, self.init_requirement.pre)
            
            return repaired_req
        else:
            return None
