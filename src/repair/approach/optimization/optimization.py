from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.fitness import correctness
from repair.approach.optimization import expressiongenerator
from repair.grammar import grammar
import repair.grammar.utils as grammar_utils

logger = logging.getLogger("gp_logger")

# TODO: Find better location for these two when introducing other approaches
class RequirementCondition:
    def __init__(self, condition, approach):
        self.condition = gp.PrimitiveTree.from_string(condition, approach.pset) if isinstance(condition, str)\
            else condition
        self.correctness = approach.toolbox.evaluate_cor(self.condition)
        self.desirability = approach.toolbox.evaluate_des(self.condition)
        self.approach = approach

    def __repr__(self):
        return (
            f"\t\t{grammar_utils.to_infix(self.condition, self.approach)}\n"
            f"\t\t{self.condition}\n"
            f"\t\tCorrectness: Δ = {self.correctness[0]}, % = {self.correctness[1] * 100}\n"
            f"\t\tDesirability: {self.desirability}\n")


class Requirement:
    def __init__(self, name, requirement, approach):
        self.name = name
        self.pre = RequirementCondition(requirement[0], approach)
        self.post = RequirementCondition(requirement[1], approach)

    def __repr__(self):
        return (
            f"{self.name}:\n"
            f"\tPRE\n"
            f"{self.pre}"
            f"\tPOST\n"
            f"{self.post}")


class OptimizationApproach(Approach):

    def __init__(self, trace_suite, requirement_text, desirability):
        super().__init__(trace_suite, requirement_text, desirability)
        # TODO: there should be two separate sets, one with the input vars only, and one with all vars
        # TODO: check lt and gt robustness, a value of zero should be wrong there
        self.pset = grammar.get_gp_primitive_sets(self.trace_suite)[0]
        self.set_creator()
        self.toolbox = self.get_toolbox()
        self.requirement = Requirement("Initial Requirement", requirement_text, self)

    def set_creator(self):
        # STEP 2: Define the creator for individuals and fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) # TODO: multiple fitness values?
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=self.pset)
        
    def get_toolbox(self):
        # STEP 3: Define the toolbox with genetic programming operations
        toolbox = base.Toolbox()
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr", expressiongenerator.generate_expr, pset=self.pset, min_=2, max_=3)
        toolbox.register("compile", gp.compile, pset=self.pset)

        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate_cor", correctness.get_fitness_correctness,
                         trace_suite=self.trace_suite, # this is fixed throughout execution
        )
        toolbox.register("evaluate_des", self.desirability.evaluate,
                         original=None,  # TODO: add original requirement
        )
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("mate", gp.cxOnePoint)
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr_mut", expressiongenerator.generate_expr, min_=1, max_=2, condition_str="full")
        toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=self.pset)
        toolbox.decorate("mate", gp.staticLimit(key=len, max_value=10))
        toolbox.decorate("mutate", gp.staticLimit(key=len, max_value=10))
        return toolbox

    def repair(self):
        # TODO add support for the requirement,
        # (1) for the initialization, also
        # (2) for the fitness

        # Create an initial population of random individuals (formulas)
        pop = self.toolbox.population(n=10)

        # Create a Hall of Fame to keep the best individual found
        hof = tools.HallOfFame(1)

        # Evolutionary loop: run for a fixed number of generations
        # TODO review this loop entirely
        for gen in tqdm(range(5)):
            # Select individuals for the next generation using tournament selection
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))  # Deep copy the individuals

            # Apply crossover (recombination) to pairs of offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.5:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation to some individuals
            for mutant in offspring:
                if random.random() < 0.3:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Re-evaluate individuals whose fitness has changed
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            for ind in invalid_ind:

                # TODO integrate the desirability as a fitness function
                # Currently, it is only a guard
                f_des = self.toolbox.evaluate_des(ind)

                is_non_trivial = f_des == 0.0
                if is_non_trivial:
                    # If sanity check passes, evaluate the individual
                    # This is where the requirement would be used to evaluate fitness
                    ind.fitness.values = (self.toolbox.evaluate_cor(ind)[0],)
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
        return Requirement("Repaired Requirement", (hof[0], "True"), self)
