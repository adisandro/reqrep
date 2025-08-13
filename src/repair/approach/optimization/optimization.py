from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.approach.requirement import Condition, Requirement
from repair.approach.optimization import expressiongenerator

logger = logging.getLogger("gp_logger")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, desirability):
        super().__init__(trace_suite, requirement_text, desirability)

        # STEP 1: Define the creator for individuals and fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) # TODO: multiple fitness values?
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

        self.toolboxes[pset_id].register("select", tools.selTournament, tournsize=3)
        self.toolboxes[pset_id].register("mate", gp.cxOnePoint)
        # if min_=0, then this requires a False or true terminal. Not supported.
        self.toolboxes[pset_id].register("expr_mut", expressiongenerator.generate_expr, min_=1, max_=2, condition_str="full")
        self.toolboxes[pset_id].register("mutate", gp.mutUniform, expr=self.toolboxes[pset_id].expr_mut, pset=self.psets[pset_id])
        self.toolboxes[pset_id].decorate("mate", gp.staticLimit(key=len, max_value=10))
        self.toolboxes[pset_id].decorate("mutate", gp.staticLimit(key=len, max_value=10))

    def _repair(self, toolbox):
        # TODO add support for the requirement,
        # (1) for the initialization, also
        # (2) for the fitness

        # Create an initial population of random individuals (formulas)
        pop = toolbox.population(n=10)

        # Create a Hall of Fame to keep the best individual found
        hof = tools.HallOfFame(1)

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
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            for ind in invalid_ind:

                # TODO integrate the desirability as a fitness function
                # Currently, it is only a guard
                f_des = toolbox.evaluate_des(ind)

                is_non_trivial = f_des == 0.0
                if is_non_trivial:
                    # If sanity check passes, evaluate the individual
                    # This is where the requirement would be used to evaluate fitness
                    ind.fitness.values = (toolbox.evaluate_cor(ind)[0],)
                else:
                    ind.fitness.values = (float("inf"),)

            # Replace the old population with the new one
            pop[:] = offspring
            hof.update(pop) # Update the best-so-far individual

            logger.info(f"Generation {gen}: Best = {hof[0]}, Fitness = {hof[0].fitness.values[0]}")

            # If an individual satisfies all constraints (zero violations), stop early
            if hof[0].fitness.values[0] == 0:
                break

        # Return the best individual (expression) found
        return hof[0]

    def repair(self, threshold):
        pre = None
        if (self.init_requirement.pre.correctness[1] * 100) < threshold:
            # repaired = self._repair(self.req.pre.toolbox)
            # pre = Condition("Repaired PRE", self.req.pre.pset, self.req.pre.toolbox, self.trace_suite, repaired)
            repaired = self._repair(self.toolboxes[0])
            pre = Condition("Repaired PRE", self.init_requirement.pre.pset, self.init_requirement.pre.toolbox, self.trace_suite, repaired)
        post = None
        if (self.init_requirement.post.correctness[1] * 100) < threshold:
            repaired = self._repair(self.toolboxes[1])
            post = Condition("Repaired POST", self.init_requirement.post.pset, self.init_requirement.post.toolbox, self.trace_suite, repaired)
        return Requirement(pre, post)
