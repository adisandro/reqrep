import time
from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.approach.optimization.customparetofront import LightweightParetoFront
from repair.approach.requirement import Requirement
from repair.approach.optimization import expressiongenerator

logger = logging.getLogger("gp_logger")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, iterations, desirability, fitness_aggregation="weighted_sum"):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

        self.set_fitness_aggregation(fitness_aggregation)
        self._init_creator()
        self._add_to_toolbox()

    def set_fitness_aggregation(self, fitness_aggregation):
        allowed = {"weighted_sum", "no_aggregation"}
        if fitness_aggregation not in allowed:
            raise ValueError(f"Invalid fitness aggregation method: {fitness_aggregation}")
        self.fitness_aggregation = fitness_aggregation

    def _init_creator(self):
        if self.fitness_aggregation == "weighted_sum":
            creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
        elif self.fitness_aggregation == "no_aggregation":
            creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0, -1.0, -1.0, -1.0))
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
            if self.fitness_aggregation == "weighted_sum":
                ind.fitness.values = (ind.correctness, ind.desirability["des"])
            elif self.fitness_aggregation == "no_aggregation":
                ind.fitness.values = (ind.correctness,) + ind.desirability["tuple"]

        toolbox = self.toolbox
        pop = toolbox.population(n=9) # Random initial population # TODO adjust number
        orig = creator.Individual(name="Candidate", toolbox=self.toolbox, pset_pre=self.pset_pre,
                                  pset_post=self.pset_post, precond=toolbox.clone(self.init_requirement.pre),
                                  postcond=toolbox.clone(self.init_requirement.post))
        pop.append(orig) # Plus original requirement
        hof = LightweightParetoFront() # Hall of Fame, for keeping track of the best individuals

        # (Initial) Evaluation
        for ind in pop:
            _set_ind_fitness(ind)
        pop = toolbox.select(pop, len(pop))

        # Evolutionary loop: run for a fixed number of generations
        for gen in tqdm(range(self.iterations)):
            start_time = time.time()
            logger.info(f"  Generation {gen}:")

            logger.info("  Creating POPULATION ...")
            # offspring = toolbox.select(pop, len(pop)) # Selection
            # offspring = list(map(toolbox.clone, offspring))  # Deep copy the individuals
            offspring = []
            for ind in pop:
                ind_copy = creator.Individual(name="Candidate", toolbox=self.toolbox, pset_pre=self.pset_pre,
                                              pset_post=self.pset_post, precond=toolbox.clone(ind.pre),
                                              postcond=toolbox.clone(ind.post))
                ind_copy.fitness.values = ind.fitness.values
                offspring.append(ind_copy)
            logger.info(f"  ... population created ({time.time() - start_time:.2f}s)")
            start_time = time.time()

            logger.info("  CROSSOVER application ...")
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
            logger.info(f"  ... crossover applied ({time.time() - start_time:.2f}s)")
            start_time = time.time()

            logger.info("  MUTATION application ...")
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
            logger.info(f"  ... mutation applied ({time.time() - start_time:.2f}s)")
            start_time = time.time()

            logger.info(f"  RE-EVALUATION of individuals with invalid fitness ...")
            for ind in offspring:
                if not ind.fitness.valid:
                    _set_ind_fitness(ind)
            logger.info(f"  ... individuals re-evaluated ({time.time() - start_time:.2f}s)")
            start_time = time.time()

            logger.info("  SELECTION + UPDATE of HoF ...")
            pop = toolbox.select(pop + offspring, len(pop))

            # Deduplication
            unique_pop = []
            seen = set()
            hof_genomes = set((str(ind.pre), str(ind.post)) for ind in hof)

            for ind in pop:
                genome = (str(ind.pre), str(ind.post))
                if genome not in seen and genome not in hof_genomes:
                    seen.add(genome)
                    unique_pop.append(ind)

            hof.update(unique_pop)
            # hof.update(pop)
            # for ind in hof:
            #     print(f"  HoF ind: {ind.pre} => {ind.post}, fitness: {ind.fitness.values}")

            logger.info(f"  ... HoF updated ({time.time() - start_time:.2f}s)")

            logger.info(f"Generation {gen}: Pareto size = {len(hof)}")

            # If an individual is perfectly correct and perfectly desirable
            if any(all(f == 0 for f in ind.fitness.values) for ind in pop):
                break

        return hof

    def repair(self):
        # Do we need to repair?
        to_repair = self.init_requirement.satisfaction_degrees["sd"][1] < 1
        if not to_repair:
            return None

        # Run the repair: rank by correctness
        hof_repaired = self._repair()
        sorted_hof_repaired = sorted(hof_repaired, key=lambda x: (x.fitness.values[0]))

        sorted_hof_requirements = []
        for i, ind in enumerate(sorted_hof_repaired):
            sorted_hof_requirements.append(Requirement(name=f"Repaired_{i}", toolbox=self.toolbox,
                                        pset_pre=self.pset_pre, pset_post=self.pset_post,
                                        precond=ind.pre, postcond=ind.post))

        return sorted_hof_requirements
