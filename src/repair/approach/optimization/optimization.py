from repair.approach.approach import Approach
from tqdm import tqdm
import random
import logging
from deap import base, creator, gp, tools
from repair.fitness import correctness, sanitycheck
from repair.approach.optimization import expressiongenerator
from repair.grammar import grammar

logger = logging.getLogger("gp_logger")

class OptimizationApproach(Approach):

    def __init__(self, tracesuite=None, transformation=None, desirability=None):
        super().__init__()
        self.traces = tracesuite.traces
        self.variable_names = sorted([v for v in tracesuite.variables if v != "Time"])
        self.transformation = transformation # TODO
        self.desirability = desirability # TODO

        self.pset = grammar.getGPPrimitiveSet(self.variable_names)
        self.set_creator()
        self.toolbox = self.getToolbox()

    def set_creator(self):
        # STEP 2: Define the creator for individuals and fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) # TODO: multiple fitness values?
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)
        
    def getToolbox(self):
        # STEP 3: Define the toolbox with genetic programming operations

        toolbox = base.Toolbox()
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr", expressiongenerator.generate_expr, pset=self.pset, min_=2, max_=2)
        toolbox.register("compile", gp.compile, pset=self.pset)

        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # TODO IMPO: Currently we are doing a sanity check based on random sampleing.
        # tbh it's decent, but its not fully sound.
        # Replace this with a better "expr" entry in toolbox.register. see expressiongenerator.py
        toolbox.register("sanitycheck", sanitycheck.is_non_trivial_candidate,
                         variable_names=self.variable_names, # this is fixed throughout execution
        )

        toolbox.register("evaluate", correctness.get_fitness_correctness,
                         traces=self.traces, # this is fixed throughout execution
        )
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("mate", gp.cxOnePoint)
        # if min_=0, then this requires a False or true terminal. Not supported.
        toolbox.register("expr_mut", expressiongenerator.generate_expr, 
                         min_=1, max_=2, condition_str="full")
        toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=self.pset)
        toolbox.decorate("mate", gp.staticLimit(key=len, max_value=10))
        toolbox.decorate("mutate", gp.staticLimit(key=len, max_value=10))
        return toolbox

    def repair(self, requirement):
        # TODO add support for the requirement parameter,
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
                # STEP 1: Perform Sanity Check
                # TODO: restore
                #is_non_trivial = self.toolbox.sanitycheck(ind)
                is_non_trivial = True
                if not is_non_trivial:
                    ind.fitness.values = (float("inf"),)
                else:
                    # If sanity check passes, evaluate the individual
                    # This is where the requirement would be used to evaluate fitness
                    ind.fitness.values = self.toolbox.evaluate(ind)

            # Replace the old population with the new one
            pop[:] = offspring
            hof.update(pop) # Update the best-so-far individual

            logger.info(f"Generation {gen}: Best = {hof[0]}, Fitness = {hof[0].fitness.values[0]}")

            # If an individual satisfies all constraints (zero violations), stop early
            if hof[0].fitness.values[0] == 0:
                break

        # Return the best individual (expression) found as a string
        return hof[0]

