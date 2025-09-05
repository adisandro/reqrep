from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.approach.requirement import Requirement
from repair.approach.optimization import expressiongenerator
import repair.grammar.utils as grammar_utils

logger = logging.getLogger("gp_logger")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, iterations, desirability):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

        self._init_creator()
        self._add_to_toolbox()

    def _init_creator(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # Minimize both objectives
        creator.create("Individual", Requirement, fitness=creator.FitnessMin)

    def _add_to_toolbox(self):

        def requirement_individual():
            ind_pre = gp.PrimitiveTree(self.toolbox.expr_pre())
            ind_post = gp.PrimitiveTree(self.toolbox.expr_post())
            ind = creator.Individual(name="Candidate", toolbox=self.toolbox, pset_pre=self.pset_pre,
                                     pset_post=self.pset_post, precond=ind_pre, postcond=ind_post)
            return ind

        # Add approach-specific registrations
        # self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr_post)
        self.toolbox.register("individual", requirement_individual)
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

        def _set_ind_fitness(ind):
            ind.fitness.values = (max(0, -ind.satisfaction_degrees["sd"][0]), ind.desirability["des"])

        toolbox = self.toolbox
        pop = toolbox.population(n=9) # Random initial population # TODO adjust number
        orig = creator.Individual(name="Candidate", toolbox=self.toolbox, pset_pre=self.pset_pre,
                                  pset_post=self.pset_post, precond=toolbox.clone(self.init_requirement.pre),
                                  postcond=toolbox.clone(self.init_requirement.post))
        pop.append(orig) # Plus original requirement
        hof = tools.ParetoFront() # Hall of Fame, for keeping track of the best individuals

        # (Initial) Evaluation
        for ind in pop:
            _set_ind_fitness(ind)
        pop = toolbox.select(pop, len(pop))

        # Evolutionary loop: run for a fixed number of generations
        for gen in tqdm(range(self.iterations)):
            # offspring = toolbox.select(pop, len(pop)) # Selection
            # offspring = list(map(toolbox.clone, offspring))  # Deep copy the individuals
            offspring = []
            for ind in pop:
                ind_copy = creator.Individual(name="Candidate", toolbox=self.toolbox, pset_pre=self.pset_pre,
                                              pset_post=self.pset_post, precond=toolbox.clone(ind.pre),
                                              postcond=toolbox.clone(ind.post))
                ind_copy.fitness.values = ind.fitness.values
                offspring.append(ind_copy)


            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                mated = False
                if random.random() < 0.5:
                    mated = True
                    toolbox.mate(child1.pre, child2.pre)
                if random.random() < 0.5:
                    mated = True
                    toolbox.mate(child1.post, child2.post)
                if mated:
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in offspring:
                mutated = False
                if random.random() < 0.3:
                    mutated = True
                    toolbox.mutate_pre(mutant.pre)
                if random.random() < 0.3:
                    mutated = True
                    toolbox.mutate_post(mutant.post)
                if mutated:
                    del mutant.fitness.values

            # (Re-)evaluation: only individuals whose fitness has changed
            for ind in offspring:
                if not ind.fitness.valid:
                    _set_ind_fitness(ind)

            # Selection
            pop = toolbox.select(pop + offspring, len(pop))
            hof.update(pop) # Update the best-so-far individual

            logger.info(f"Generation {gen}: Pareto size = {len(hof)}")

            # If an individual is perfectly correct and perfectly desirable
            # stop early. This is theoretically impossible for a faulty input requirement
            if any(f_cor == 0 and f_des == 0 for f_cor, f_des in (ind.fitness.values for ind in pop)):
                break

        return hof

    def repair(self):
        # TODO: For now, I am only considering the single best repaired individual
        # TODO: wrt. correctness. extend this to support multiple repaired individuals (?)

        # Do we need to repair?
        to_repair = self.init_requirement.satisfaction_degrees["sd"][1] < 1
        if not to_repair:
            return None

        # Run the repair: rank by correctness, then desirability
        hof_repaired = self._repair()
        best_repaired = min(hof_repaired, key=lambda x: (x.fitness.values[0], x.fitness.values[1]))
        best_repaired.name = "Repaired"

        return best_repaired
