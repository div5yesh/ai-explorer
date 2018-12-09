from enum import Enum


class Directions(Enum):
    EAST = 0
    E = 0

    NORTH = 1
    N = 1

    WEST = 2
    W = 2

    SOUTH = 3
    S = 3


class MapTiles(Enum):
    U = -1
    UNKNOWN = -1

    P = 0
    PATH = 0

    S = 1
    SAND = 1

    M = 2
    MOUNTAIN = 2

    W = 3
    WALL = 3


tile_cost = {
    MapTiles.PATH: 1,
    MapTiles.SAND: 3,
    MapTiles.MOUNTAIN: 10}


class MapObject(object):
    def __init__(self):
        self.strength = 0
        self.label = 'mapobject'
        self.delta = 0

    def move(self):
        pass


class StaticMonster(MapObject):
    def __init__(self):
        self.strength = 10
        self.label = 'skeleton'
        self.delta = -10


class PowerUp(MapObject):
    def __init__(self):
        self.label = 'medkit'
        self.delta = 10


class Boss(StaticMonster):
    def __init__(self):
        self.strength = 100
        self.label = 'boss'
        self.delta = -100

class State:
    """
    The object to represent a location of a tile.
    """

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], tuple):
                self._state = args[0]
            elif isinstance(args[0], State):
                self._state = (args[0].x, args[0].y)

        elif len(args) == 2:
            self._state = (int(args[0]), int(args[1]))

        else:
            raise ValueError

    @property
    def x(self):
        return self._state[0]

    @property
    def y(self):
        return self._state[1]

    def move(self, direction):
        if direction == Directions.NORTH:
            return State(self.x - 1, self.y)

        if direction == Directions.EAST:
            return State(self.x, self.y + 1)

        if direction == Directions.WEST:
            return State(self.x, self.y - 1)

        if direction == Directions.SOUTH:
            return State(self.x + 1, self.y)

    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def neighbours(self, map_size):
        """
        Return N,E,W,S neighbours one at a time on each iteration.
        """

        if self.x > 0:
            yield State(self.x - 1, self.y)
        else:
            yield None

        if self.y < map_size:
            yield State(self.x, self.y + 1)
        else:
            yield None

        if self.x < map_size:
            yield State(self.x + 1, self.y)
        else:
            yield None

        if self.y > 0:
            yield State(self.x, self.y - 1)
        else:
            yield None

    def __eq__(self, other):
        if other:
            if self.x == other.x and self.y == other.y:
                return True
        return False

    def __getitem__(self, item):
        return self._state[item]

    def __hash__(self):
        return self._state.__hash__()

    def __str__(self):
        return str(self._state)

class Node:
    """
    Node object for bookkeeping of the current state, parent node for backtracking,
    action performed to generate the node, actual cost and estimated cost.
    """

    def __init__(self, estimateCost, actualCost, state, parent, action):
        """
        Constructor
        """

        self.estimateCost = estimateCost
        self.actualCost = actualCost
        self.state = State(state)
        self.parent = parent
        self.action = action

    def __eq__(self, other):
        """
        Equal operator overload for membership testing of states in heapq
        and replace the node having state with higher estimated cost if
        node already present.
        """

        if other:
            if self.state == other.state:
                return True
        return False

    def __lt__(self, other):
        """
        Less than operator overload to compare estimated costs for heapify
        comparisons in heapq, using the priority as estimated cost.
        """

        return self.estimateCost < other.estimateCost

    def __str__(self):
        return str(self.state)

