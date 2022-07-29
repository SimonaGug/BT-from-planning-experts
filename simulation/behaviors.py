# pylint: disable=duplicate-code
"""
Implementing various py trees behaviors
For duplo brick handling in a state machine env
"""
import re
import py_trees as pt

import simulation.conveyor_kitting as sm

def get_node_from_string(string, world_interface, verbose=False):
    # pylint: disable=too-many-branches
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False

    if 'not at station ' in string:
        node = NotAtStation(string, world_interface, string[15:])
    elif 'at station ' in string:
        node = AtStation(string, world_interface, string[11:])
    elif 'battery level ' in string:
        node = BatteryLevel(string, world_interface, re.findall(r'\d+', string))
    elif 'carried weight ' in string:
        node = CarriedWeight(string, world_interface, re.findall(r'\d+', string))
    elif 'carried light ' in string:
        node = CarriedLight(string, world_interface, re.findall(r'\d+', string))
    elif 'carried heavy ' in string:
        node = CarriedHeavy(string, world_interface, re.findall(r'\d+', string))
    elif 'conveyor light ' in string:
        node = ConveyorLight(string, world_interface, re.findall(r'\d+', string))
    elif 'conveyor heavy ' in string:
        node = ConveyorHeavy(string, world_interface, re.findall(r'\d+', string))


    elif 'idle' in string:
        node = Idle(string, world_interface, verbose)
    elif 'charge' in string:
        node = Charge(string, world_interface, verbose)
    elif 'move to' in string:
        node = MoveTo(string, world_interface, string[7:], verbose)
    elif 'pick' in string:
        node = Pick(string, world_interface, verbose)
    elif 'place' in string:
        node = Place(string, world_interface, verbose=verbose)

    elif string == 'f(':
        node = pt.composites.Selector('Fallback', memory=False)
        has_children = True
    elif string == 'fm(':
        node = pt.composites.Selector('Fallback', memory=True)
        has_children = True
    elif string == 's(':
        node = pt.composites.Sequence('Sequence', memory=False)
        has_children = True
    elif string == 'sm(':
        node = pt.composites.Sequence('Sequence', memory=True)
        has_children = True
    elif string == 'p(':
        node = pt.composites.Parallel(
            name="Parallel",
            policy=pt.common.ParallelPolicy.SuccessOnAll(synchronise=False))
        has_children = True
    elif string == 'nonpytreesbehavior':
        return False
    else:
        raise Exception("Unexpected character", string)
    return node, has_children

def is_lower_than(string):
    """
    Returns true if string contains '<', false otherwise
    """
    if '<' in string:
        return True
    return False

def is_lower_equal_than(string):
    """
    Returns true if string contains '<', false otherwise
    """
    if '<=' in string:
        return True
    return False

class AtStation(pt.behaviour.Behaviour):
    """
    Check if robot is at given station
    """
    def __init__(self, name, world_interface, station):
        self.world_interface = world_interface
        self.station = sm.get_station_from_string(station)
        super(AtStation, self).__init__(name)

    def update(self):
        if self.world_interface.at_station(self.station):
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class NotAtStation(pt.behaviour.Behaviour):
    """
    Check if robot is at given station
    """
    def __init__(self, name, world_interface, station):
        self.world_interface = world_interface
        self.station = sm.get_station_from_string(station)
        super(NotAtStation, self).__init__(name)

    def update(self):
        if self.world_interface.not_at_station(self.station):
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class ComparisonCondition(pt.behaviour.Behaviour):
    """
    Class template for conditions comparing against constants
    """
    def __init__(self, name, world_interface, value):
        self.world_interface = world_interface
        self.lower_equal = is_lower_equal_than(name)
        self.value = int(value[0])
        super(ComparisonCondition, self).__init__(name)

    def compare(self, variable):
        """ Compares input variable to stored value """
        if (not self.lower_equal and variable > self.value) or \
           (self.lower_equal and variable <= self.value):
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class BatteryLevel(ComparisonCondition):
    """
    Checks battery level
    """
    def update(self):
        return self.compare(self.world_interface.state.battery_level)

class CarriedWeight(ComparisonCondition):
    """
    Check the currently carried weight
    """
    def update(self):
        return self.compare(self.world_interface.state.carried_weight)

class CarriedLight(ComparisonCondition):
    """
    Check the currently carried number of light objects
    """
    def update(self):
        return self.compare(self.world_interface.state.carried_light)

class CarriedHeavy(ComparisonCondition):
    """
    Check the currently carried number of heavy objects
    """
    def update(self):
        return self.compare(self.world_interface.state.carried_heavy)

class ConveyorLight(ComparisonCondition):
    """
    Check the current number of light objects on conveyor
    """
    def update(self):
        return self.compare(self.world_interface.state.cnv_n_light)

class ConveyorHeavy(ComparisonCondition):
    """
    Check the current number of heavy objects on conveyor
    """
    def update(self):
        return self.compare(self.world_interface.state.cnv_n_heavy)

class SmBehavior(pt.behaviour.Behaviour):
    """
    Class template for state machine behaviors
    """
    def __init__(self, name, world_interface, verbose=False):
        self.world_interface = world_interface
        self.state = None
        self.verbose = verbose
        super(SmBehavior, self).__init__(name)

    def update(self):
        if self.verbose and self.state == pt.common.Status.RUNNING:
            print(self.name, ":", self.state)

    def success(self):
        """ Set state success """
        self.state = pt.common.Status.SUCCESS
        if self.verbose:
            print(self.name, ": SUCCESS")

    def failure(self):
        """ Set state failure """
        self.state = pt.common.Status.FAILURE
        if self.verbose:
            print(self.name, ": FAILURE")

class Idle(SmBehavior):
    """
    Do nothing
    """
    def initialise(self):
        self.state = pt.common.Status.RUNNING

    def update(self):
        super(Idle, self).update()
        if self.state is None:
            self.state = pt.common.Status.RUNNING
        if self.state is pt.common.Status.RUNNING and self.world_interface.ready_for_action:
            self.world_interface.idle()

        return self.state

class Charge(SmBehavior):
    """
    Charge robot
    """
    def initialise(self):
        self.state = pt.common.Status.RUNNING

    def check_for_success(self):
        """ Checks if at goal state """
        if self.world_interface.state.battery_level >= sm.MAX_BATTERY:
            self.success()

    def update(self):
        self.check_for_success()
        super(Charge, self).update()

        if self.state is None:
            self.state = pt.common.Status.RUNNING
        if self.state == pt.common.Status.RUNNING and self.world_interface.ready_for_action:
            if not self.world_interface.charge():
                self.failure()
        return self.state

class MoveTo(SmBehavior):
    """
    Move towards station
    """
    def __init__(self, name, world_interface, station, verbose=False):
        self.station = sm.get_station_from_string(station)
        super(MoveTo, self).__init__(name, world_interface, verbose)

    def initialise(self):
        self.state = pt.common.Status.RUNNING

    def check_for_success(self):
        """ Checks if at goal state """
        if self.world_interface.at_station(self.station):
            self.success()

    def update(self):
        self.check_for_success()
        super(MoveTo, self).update()

        if self.state is None:
            self.state = pt.common.Status.RUNNING
        if self.state == pt.common.Status.RUNNING and self.world_interface.ready_for_action:
            if not self.world_interface.moveto(self.station):
                self.failure()
        return self.state

class Pick(SmBehavior):
    """
    Pick up an object
    """
    def __init__(self, name, world_interface, verbose=False):
        self.picked = False
        super(Pick, self).__init__(name, world_interface, verbose)

    def initialise(self):
        self.state = pt.common.Status.RUNNING
        self.picked = False

    def update(self):
        super(Pick, self).update()
        if self.picked:
            self.success()

        if self.state is None:
            self.state = pt.common.Status.RUNNING
        if self.state == pt.common.Status.RUNNING and self.world_interface.ready_for_action:
            if self.world_interface.pick():
                self.picked = True
            else:
                self.failure()
        return self.state

class Place(SmBehavior):
    """
    Places all objects held at current position
    """
    def __init__(self, name, world_interface, verbose=False):
        self.placed = False
        super(Place, self).__init__(name, world_interface, verbose)

    def initialise(self):
        self.state = pt.common.Status.RUNNING
        self.placed = False

    def update(self):
        super(Place, self).update()
        if self.placed:
            self.success()

        if self.state is None:
            self.state = pt.common.Status.RUNNING
        if self.state == pt.common.Status.RUNNING and self.world_interface.ready_for_action:
            if self.world_interface.place():
                self.placed = True
            else:
                self.failure()
        return self.state
