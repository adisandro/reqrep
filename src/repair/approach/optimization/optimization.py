from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.approach.requirement import Requirement
from repair.approach.optimization import expressiongenerator

logger = logging.getLogger("gp_logger")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, iterations, desirability):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

        self._init_creator()
        self._add_to_toolbox()

    def _init_creator(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # Minimize both objectives
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    def _add_to_toolbox(self):
        # Add approach-specific registrations
        self.toolbox.register("individual_pre", tools.initIterate, creator.Individual, self.toolbox.expr_pre)
        self.toolbox.register("individual_post", tools.initIterate, creator.Individual, self.toolbox.expr_post)
        self.toolbox.register("population_pre", tools.initRepeat, list, self.toolbox.individual_pre)
        self.toolbox.register("population_post", tools.initRepeat, list, self.toolbox.individual_post)

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

    def _set_ind_fitness(self, ind, target):
            if target == "pre":
                ind_pre = ind
                ind_post = self.init_requirement.post
            else:
                ind_pre = self.init_requirement.pre
                ind_post = ind
            r = Requirement("Candidate", self.toolbox, self.pset_pre, ind_pre, self.pset_post, ind_post)
            ind.fitness.values = (max(0, -r.satisfaction_degrees[f"{target}_sd"][0]), r.desirability["des"])
            # TODO Aren, check above...

    def _repair(self, target):
        toolbox = self.toolbox
        # Random initial population # TODO adjust number
        pop = toolbox.population_pre(n=10) if target == "pre" else toolbox.population_post(n=10)
        hof = tools.ParetoFront() # Hall of Fame, for keeping track of the best individuals

        # (Initial) Evaluation
        for ind in pop:
            self._set_ind_fitness(ind, target)

        pop = toolbox.select(pop, len(pop))

        # Evolutionary loop: run for a fixed number of generations
        # TODO review this loop entirely
        for gen in tqdm(range(self.iterations)):
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
                    toolbox.mutate_pre(mutant) if target == "pre" else toolbox.mutate_post(mutant)
                    del mutant.fitness.values

            # (Re-)evaluation: only individuals whose fitness has changed
            for ind in offspring:
                if not ind.fitness.valid:
                    self._set_ind_fitness(ind, target)

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
        # pre | post | pre => post | repair what?
        # 0   | 0    | 1           | must repair pre, must repair post
        # 0   | 1    | 1           | must repair pre
        # 1   | 0    | 0           | must repair post
        # 1   | 1    | 1           | no repair needed

        # TODO: For now, I am only considering the single best repaired individual
        # TODO: wrt. correctness. extend this to support multiple repaired individuals (?)

        # Do we need to repair?
        to_repair_pre = self.init_requirement.satisfaction_degrees["pre_sd"][1] * 100 < threshold
        to_repair_post = self.init_requirement.satisfaction_degrees["post_sd"][1] * 100 < threshold
        if not to_repair_pre and not to_repair_post:
            return None

        # Run the repair: rank by correctness, then desirability
        # TODO Aren, check for potential problem here
        best_repaired_pre = self.init_requirement.pre
        if to_repair_pre:
            hof_repaired = self._repair("pre")
            best_repaired_pre = min(hof_repaired, key=lambda x: (x.fitness.values[0], x.fitness.values[1]))
        best_repaired_post = self.init_requirement.post
        if to_repair_post:
            hof_repaired = self._repair("post")
            best_repaired_post = min(hof_repaired, key=lambda x: (x.fitness.values[0], x.fitness.values[1]))
        repaired_req = Requirement("Repaired", self.toolbox,
                                   self.pset_pre, best_repaired_pre,
                                   self.pset_post, best_repaired_post)

        return repaired_req
