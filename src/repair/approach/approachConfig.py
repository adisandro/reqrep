from dataclasses import dataclass

@dataclass
class ApproachConfig:
    # Optimization Hyperparams
    pop_size: int = 10
    # num_selected: int = 10 # NOTE This is fixed to be pop_size
    num_offsprings: int = 10 # NOTE currently also fixed to be pop_size. See "Creating POPULATION" part
    random_offsprings: bool = False # for the next population, chose random entries from the current population? or just iterate
    crossover_probability: float = 0.5 # currently set to 0.5 for both pre and post conditions
    mutation_probability: float = 0.3 # currently set to 0.3 for both pre and post conditions

    # Tree size parameters
    pre_tree_min_depth: int = 2
    pre_tree_max_depth: int = 3
    post_tree_min_depth: int = 2
    post_tree_max_depth: int = 3

CONFIG_MAP = {
    "default": ApproachConfig(),
    "alt_1": ApproachConfig(pop_size=20, num_offsprings=10, random_offsprings=True),
    "alt_2": ApproachConfig(pop_size=10, num_offsprings=20, random_offsprings=True),
    "alt_3": ApproachConfig(pop_size=10, num_offsprings=30, random_offsprings=True),
    "alt_4": ApproachConfig(pop_size=20, num_offsprings=20, random_offsprings=True),
    "alt_5": ApproachConfig(pre_tree_max_depth=3, post_tree_max_depth=6),
    "alt_6": ApproachConfig(pre_tree_max_depth=3, post_tree_max_depth=9),
    "alt_7": ApproachConfig(pre_tree_max_depth=6, post_tree_max_depth=3),
    "alt_8": ApproachConfig(pre_tree_max_depth=9, post_tree_max_depth=3),
    "hp_increase_num_offsprings": ApproachConfig(pop_size=10, num_offsprings=20),
    "hp_increase_tree_depth": ApproachConfig(pre_tree_max_depth=6, post_tree_max_depth=6),
}
