from repair.approach.approach import Approach
import operator
import random
import logging
from deap import base, creator, gp, tools
from repair.approach import utils

logger = logging.getLogger("gp_logger")

class OptimizationApproach(Approach):

    def __init__(self, tracesuite=None, transformation=None, desirability=None):
        self.traces = tracesuite.traces
        self.transformation = transformation # TODO
        self.desirability = desirability # TODO
        # super().__init__()

        self.pset = self.getGPLanguage()
        self.set_creator()
        self.toolbox = self.getToolbox()


    def getGPLanguage(self):
        # # STEP 1: Define the set of operations and terminals

        # Define types
        Float = float
        Bool = bool

        # Define the typed primitive set
        pset = gp.PrimitiveSetTyped("MAIN", [Float], Bool)  # input: x: float → returns: Bool

        # Add arithmetic ops: only for Float inputs → Float output
        pset.addPrimitive(operator.add, [Float, Float], Float)
        pset.addPrimitive(operator.sub, [Float, Float], Float)

        # Add comparisons: Float inputs → Bool output
        pset.addPrimitive(operator.lt, [Float, Float], Bool)
        pset.addPrimitive(operator.gt, [Float, Float], Bool)
        pset.addPrimitive(operator.eq, [Float, Float], Bool)

        # Add logic ops: Bool inputs → Bool output
        pset.addPrimitive(operator.and_, [Bool, Bool], Bool)
        pset.addPrimitive(operator.or_, [Bool, Bool], Bool)
        pset.addPrimitive(operator.not_, [Bool], Bool)

        # Terminals: input variable x, floats, numeric constants and bools
        pset.renameArguments(ARG0='x')
        for const in [-10.0, -5.0, 0.0, 5.0, 10.0]:
            pset.addTerminal(const, Float)
        pset.addEphemeralConstant("rand100", lambda: random.uniform(0, 10), Float)

        # TODO, select best option for us
        # FIXES TO `IndexError: The gp.generate function tried to add a terminal of type '<class 'bool'>', but there is none available.`
        pset.addTerminal(True, bool)
        pset.addTerminal(False, bool)
        # # limit depth
        # toolbox.register("expr", gp.genFull, pset=pset, min_=1, max_=3)

        # lambda wrapper for typesetting
        # def logical_and(a: bool, b: bool) -> bool:
        #     return a and b

        # pset.addPrimitive(logical_and, [bool, bool], bool)

        # TODO add some custom temporal operators

        return pset

    def set_creator(self):
        # STEP 2: Define the creator for individuals and fitness
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) # TODO: multiple fitness values?
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)
        
    def getToolbox(self):
        # STEP 3: Define the toolbox with genetic programming operations

        toolbox = base.Toolbox()
        toolbox.register("expr", gp.genHalfAndHalf, pset=self.pset, min_=1, max_=3)
        toolbox.register("compile", gp.compile, pset=self.pset)

        # # TODO this is temp, we need to ensure that the generated individuals contain the variable 'x'
        # def contains_variable_x(ind):
        #     return "x" in str(ind)  # Fast check that 'x' appears in the string representation

        # def generate_valid_individual():
        #     while True:
        #         ind = tools.initIterate(creator.Individual, toolbox.expr)
        #         if contains_variable_x(ind):
        #             logger.info("VALID:", ind)
        #             return ind
        #         else:
        #             logger.info("INVALID:", ind)

        # toolbox.register("individual", generate_valid_individual)
        # TODO create a custom individual initializer. Taking into consideration the initial expression
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", utils.eval_requirement,
                         traces=self.traces, # because is fixed
                         compile_func=toolbox.compile, # because is fixed
        )
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("mate", gp.cxOnePoint)
        toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
        toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=self.pset)
        toolbox.decorate("mate", gp.staticLimit(key=len, max_value=10))
        toolbox.decorate("mutate", gp.staticLimit(key=len, max_value=10))
        return toolbox

    def repair(self, requirement):
        # TODO add support for the requirement parameter, (1) for the initialization, also (2) for the fitness

        # Create an initial population of random individuals (formulas)
        pop = self.toolbox.population(n=10)

        # Create a Hall of Fame to keep the best individual found
        hof = tools.HallOfFame(1)

        # Evolutionary loop: run for a fixed number of generations
        # TODO review this loop entirely
        for gen in range(2):
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

