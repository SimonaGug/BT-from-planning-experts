"""
Task dependent fitness function
"""

from dataclasses import dataclass

@dataclass
class Coefficients:
    """
    Coefficients for tuning the fitness function
    """
    delivered_heavy: float = 2.0
    delivered_light: float = 1.0
    blocked_heavy: float = -0.5
    blocked_light: float = -0.25
    depth: float = 0.0
    length: float = -0.2
    ticks: float = 0.0
    failed: float = 0.0
    timeout: float = 0.0

def compute_fitness(world_interface, behavior_tree, ticks, coeff=None, verbose=False):
    # pylint: disable=too-many-arguments
    """ Retrieve values and compute fitness """

    if coeff is None:
        coeff = Coefficients()

    depth = behavior_tree.depth
    length = behavior_tree.length

    #fitness = coeff.length * length + \
    #          coeff.depth * depth + \
    #          coeff.ticks * ticks
    
    fitness = coeff.ticks * ticks

    if verbose:
        print("Fitness from length, depth, ticks:", fitness)

    fitness += coeff.delivered_heavy * world_interface.state.delivered_heavy
    fitness += coeff.delivered_light * world_interface.state.delivered_light
    if verbose:
        print("world_interface" , world_interface.state)
        print("Delivered Heavy" , world_interface.state.delivered_heavy)
        print("Delivered Light" , world_interface.state.delivered_light)
        print("Fitness after deliveries:", fitness)

    fitness += coeff.blocked_heavy * world_interface.state.blocked_heavy
    fitness += coeff.blocked_light * world_interface.state.blocked_light
    if verbose:
        print("Fitness after blocked:", fitness)

    if behavior_tree.failed:
        fitness += coeff.failed
        if verbose:
            print("Failed: ", fitness)
    if behavior_tree.timeout:
        fitness += coeff.timeout
        if verbose:
            print("Timed out: ", fitness)

    return fitness, int(world_interface.state.delivered_heavy), int(world_interface.state.delivered_light)
