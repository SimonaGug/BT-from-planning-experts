"""
Simulation of a robot performing kitting from two conveyors
"""
import random
from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum

MAX_BATTERY = 100
MAX_WEIGHT = 10
MAX_HEAVY = 10
MAX_LIGHT = 10
HEAVY_WEIGHT = 4
LIGHT_WEIGHT = 2
ROBOT_SPEED = 5

@dataclass
class Pos:
    """
    Position
    """
    x: float = 12.0
    y: float = 7.0

@dataclass
class WorldState:
    """
    The complete world state:
    """
    tick: int = 0
    robot_pos: Pos = field(default_factory=Pos)
    battery_level: int = MAX_BATTERY
    carried_weight: int = 0
    carried_light: int = 0
    carried_heavy: int = 0
    cnv_n_light: int = 0 #Number of light objects currently on conveyor
    cnv_n_heavy: int = 0 #Number of heavy objects currently on conveyor
    delivered_heavy: int = 0
    delivered_light: int = 0
    blocked_heavy: int = 0
    blocked_light: int = 0

class Stations(IntEnum):
    """ Indices for robot stations """
    CHARGE1 = 0
    CHARGE2 = 1
    CONVEYOR_HEAVY = 2
    CONVEYOR_LIGHT = 3
    DELIVERY = 4
    OTHER = 5

def get_station_from_string(string):
    """ Returns station index from string """
    if 'CHARGE1' in string:
        return Stations.CHARGE1
    if 'CHARGE2' in string:
        return Stations.CHARGE2
    if 'CONVEYOR_HEAVY' in string:
        return Stations.CONVEYOR_HEAVY
    if 'CONVEYOR_LIGHT' in string:
        return Stations.CONVEYOR_LIGHT
    if 'DELIVERY' in string:
        return Stations.DELIVERY
    if 'OTHER' in string:
        return Stations.OTHER
    return -1

def get_pos(station):
    """
    Returns pose of given station
    """
    if station == Stations.CHARGE1:
        return Pos(2, 7.5)
    if station == Stations.CHARGE2:
        return Pos(23, 12)
    if station == Stations.CONVEYOR_HEAVY:
        return Pos(12, 12)
    if station == Stations.CONVEYOR_LIGHT:
        return Pos(12, 3)
    if station == Stations.DELIVERY:
        return Pos(21, 7.5)
    return Pos(0, 0)

def move_towards(station, state):
    """
    Moves towards given station
    with super simple silly path planning
    """
    station_pos = get_pos(station)
    if state.robot_pos != station_pos:
        if state.robot_pos.y != station_pos.y:
            if state.robot_pos.x != station_pos.x and \
               (state.robot_pos.x < 12 or state.robot_pos.x > 21):
                move_towards_x(state.robot_pos, station_pos)
            else:
                move_towards_y(state.robot_pos, station_pos)
        elif state.robot_pos.x != station_pos.x:
            move_towards_x(state.robot_pos, station_pos)
        state.battery_level -= 1

def move_towards_x(robot_pos, station_pos):
    """
    Move towards station in x direction
    """
    if robot_pos.x < station_pos.x:
        robot_pos.x = min(robot_pos.x + ROBOT_SPEED, station_pos.x)
    else:
        robot_pos.x = max(robot_pos.x - ROBOT_SPEED, station_pos.x)

def move_towards_y(robot_pos, station_pos):
    """
    Move towards station in y direction
    """
    if robot_pos.y < station_pos.y:
        robot_pos.y = min(robot_pos.y + ROBOT_SPEED, station_pos.y)
    else:
        robot_pos.y = max(robot_pos.y - ROBOT_SPEED, station_pos.y)

class Simulation:
    """
    Main simulation class
    """
    def __init__(self, seed=None):
        self.state = WorldState()
        if seed is not None:
            random.seed(seed)
        self.ready_for_action = False #At most one action each tick

    def get_feedback(self):
        # pylint: disable=no-self-use
        """ Dummy to fit template """
        self.ready_for_action = True
        return True

    def get_sensor_data(self):
         # pylint: disable=no-self-use
        """ Dummy to fit template """
        return True

    def send_references(self):
         # pylint: disable=no-self-use
        """ Dummy to fit template """
        if self.ready_for_action:
            self.ready_for_action = False
            self.step() #Step simulation even if no action taken

    def step(self):
        """
        Step the simulation one timestep
        """

        #Randomly add objects on conveyor
        if random.random() < 0.06:
            if self.state.cnv_n_heavy < MAX_HEAVY:
                self.state.cnv_n_heavy += 1
            else:
                self.state.blocked_heavy += 1
        if random.random() < 0.12:
            if self.state.cnv_n_light < MAX_LIGHT:
                self.state.cnv_n_light += 1
            else:
                self.state.blocked_light += 1

        #Deplete battery
        self.state.battery_level -= 1
        if self.state.battery_level < 0:
            self.state.battery_level = 0

        #Only one action per tick
        self.ready_for_action = False
        self.state.tick += 1

    def at_station(self, station):
        """ Checks if robot is currently at given station """
        if station==Stations.OTHER:
            if self.state.robot_pos != get_pos(Stations.CHARGE1) and self.state.robot_pos != get_pos(Stations.CHARGE2) and self.state.robot_pos != get_pos(Stations.CONVEYOR_HEAVY) and self.state.robot_pos != get_pos(Stations.CONVEYOR_LIGHT) and self.state.robot_pos != get_pos(Stations.DELIVERY):
                return True
        return self.state.robot_pos == get_pos(station)
    
    def not_at_station(self, station):
        """ Checks if robot is currently NOT at given station """
        if station==Stations.OTHER:
            if self.state.robot_pos == get_pos(Stations.CHARGE1) or self.state.robot_pos == get_pos(Stations.CHARGE2) or self.state.robot_pos == get_pos(Stations.CONVEYOR_HEAVY) or self.state.robot_pos == get_pos(Stations.CONVEYOR_LIGHT) or self.state.robot_pos == get_pos(Stations.DELIVERY):
                return True
        if station==Stations.CHARGE1:
            if self.state.robot_pos != get_pos(station):
                return True
        if station==Stations.CHARGE2:
            if self.state.robot_pos != get_pos(station):
                return True
        if station==Stations.CONVEYOR_HEAVY:
            if self.state.robot_pos != get_pos(station):
                return True
        if station==Stations.CONVEYOR_LIGHT:
            if self.state.robot_pos != get_pos(station):
                return True
        if station==Stations.DELIVERY:
            if self.state.robot_pos != get_pos(station):
                return True
        return False

    def idle(self):
        """
        Robot does nothing
        """
        self.step()

    def charge(self):
        """
        Robot attemps to charge at station
        """
        if self.state.robot_pos == get_pos(Stations.CHARGE1) or \
           self.state.robot_pos == get_pos(Stations.CHARGE2):
            self.state.battery_level += 10
            self.step()
            self.state.battery_level = min(MAX_BATTERY, self.state.battery_level)
            return True
        return False

    def moveto(self, station):
        """
        Moves robot towards given position
        """
        if self.state.battery_level > 0:
            move_towards(station, self.state)
            self.step()
            return True
        return False

    def pick(self):
        """
        Picks up an object if possible
        """
        if self.state.battery_level > 0:
            if self.state.robot_pos == get_pos(Stations.CONVEYOR_HEAVY) and \
                self.state.cnv_n_heavy > 0 and \
                self.state.carried_weight + HEAVY_WEIGHT <= MAX_WEIGHT:

                self.state.carried_weight += HEAVY_WEIGHT
                self.state.carried_heavy += 1
                self.state.cnv_n_heavy -= 1
                self.state.battery_level -= 1
                self.step()
                return True
            if self.state.robot_pos == get_pos(Stations.CONVEYOR_LIGHT) and \
                self.state.cnv_n_light > 0 and \
                self.state.carried_weight + LIGHT_WEIGHT <= MAX_WEIGHT:

                self.state.carried_weight += LIGHT_WEIGHT
                self.state.carried_light += 1
                self.state.cnv_n_light -= 1
                self.state.battery_level -= 1
                self.step()
                return True
        return False

    def place(self):
        """
        Places objects if possible
        """
        if self.state.battery_level > 0:
            if self.state.robot_pos == get_pos(Stations.DELIVERY):
                for _ in range(self.state.carried_light):
                    self.state.carried_light -= 1
                    self.state.carried_weight -= LIGHT_WEIGHT
                    self.state.delivered_light += 1

                for _ in range(self.state.carried_heavy):
                    self.state.carried_heavy -= 1
                    self.state.carried_weight -= HEAVY_WEIGHT
                    self.state.delivered_heavy += 1
                self.state.battery_level -= 1
                self.step()
                return True
        return False
