from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.approach.requirement import PreCondition, PostCondition, Requirement
from repair.approach.optimization import expressiongenerator

logger = logging.getLogger("gp_logger")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, desirability):
        super().__init__(trace_suite, requirement_text, desirability)

        # STEP 1: Define the creator for individuals and fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # Minimize both objectives
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

        # STEP 2: Add Optimization-specific registrations
        self.add_to_toolbox(0)
        self.add_to_toolbox(1)
        
        # TODO: check lt and gt robustness, a value of zero should be wrong there

    def add_to_toolbox(self, pset_id):
        super().init_toolbox(pset_id)

        # Add approach-specific registrations
        self.toolboxes[pset_id].register("individual", tools.initIterate, creator.Individual, self.toolboxes[pset_id].expr)
        self.toolboxes[pset_id].register("population", tools.initRepeat, list, self.toolboxes[pset_id].individual)

        self.toolboxes[pset_id].register("select", tools.selNSGA2)
        self.toolboxes[pset_id].register("mate", gp.cxOnePoint)
        # if min_=0, then this requires a False or true terminal. Not supported.
        self.toolboxes[pset_id].register("expr_mut", expressiongenerator.generate_expr, min_=1, max_=2, condition_str="full")
        self.toolboxes[pset_id].register("mutate", gp.mutUniform, expr=self.toolboxes[pset_id].expr_mut, pset=self.psets[pset_id])

        # Decorators to limit tree size
        self.toolboxes[pset_id].decorate("mate", gp.staticLimit(key=len, max_value=10))
        self.toolboxes[pset_id].decorate("mutate", gp.staticLimit(key=len, max_value=10))

    def _repair(self, pre_post_id):
        # TODO add support for the requirement,
        # for the initialization

        toolbox = self.toolboxes[pre_post_id]

        # Create an initial population of random individuals (formulas)
        pop = toolbox.population(n=10)

        # Create a Hall of Fame to keep the best individual found
        hof = tools.ParetoFront()
    
        # Evaluate initial population
        for ind in pop:
            f_cor = toolbox.evaluate_cor(ind)[0]
            f_des = toolbox.evaluate_des(ind, pre_post_id)
            ind.fitness.values = (f_cor, f_des)

        pop = toolbox.select(pop, len(pop))

        # Evolutionary loop: run for a fixed number of generations
        # TODO review this loop entirely
        for gen in tqdm(range(5)):
            # Select individuals for the next generation using tournament selection
            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))  # Deep copy the individuals

            # Apply crossover (recombination) to pairs of offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.5:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation to some individuals
            for mutant in offspring:
                if random.random() < 0.3:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Re-evaluate individuals whose fitness has changed
            for ind in offspring:
                if not ind.fitness.valid:
                    f_cor = toolbox.evaluate_cor(ind)[0]
                    f_des = toolbox.evaluate_des(ind, pre_post_id)
                    ind.fitness.values = (f_cor, f_des)

            # Select the new population
            pop = toolbox.select(pop + offspring, len(pop))
            hof.update(pop) # Update the best-so-far individual

            logger.info(f"Generation {gen}: Pareto size = {len(hof)}")

            # If an individual is perfectly correct and perfectly desirable
            # stop early. This is theoretically impossible for a faulty input requirement
            if any(f_cor == 0 and f_des == 0 for f_cor, f_des in (ind.fitness.values for ind in pop)):
                break

        # Return the best individual (expression) found
        return hof

    def repair(self, threshold):
        # TODO: For now, I am only considering the single best repaired individual
        # wrt. correctness. extend this to support multiple repaired individuals (?)

        pre = None
        if (self.init_requirement.pre.correctness[1] * 100) < threshold:
            hof_repaired = self._repair(0)
            best_repaired = min(hof_repaired, key=lambda x: x.fitness.values[0])
            pre = PreCondition("Repaired", self.init_requirement.pre.pset, self.init_requirement.pre.toolbox, self.trace_suite, best_repaired)

        post = None
        if (self.init_requirement.post.correctness[1] * 100) < threshold:
            hof_repaired = self._repair(1)
            # ordered_hof = sorted(hof_repaired, key=lambda ind: ind.fitness.values[0])
            # print(len(hof_repaired))
            # for ind in ordered_hof:
            #     print(ind.fitness.values)
            # print('-------------------')
            best_repaired = min(hof_repaired, key=lambda x: x.fitness.values[0])
            post = PostCondition("Repaired", self.init_requirement.post.pset, self.init_requirement.post.toolbox, self.trace_suite, best_repaired)
        return Requirement(pre, post)
