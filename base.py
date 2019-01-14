from collections import namedtuple

from utils import Directions


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
        return '(%d,%d)' % (self.x, self.y)

    def __repr__(self):
        return self.__str__()


class Node:
    """
    Node object for bookkeeping of the current state, parent node for backtracking,
    action performed to generate the node, actual cost and estimated cost.
    """

    def __init__(self, estimate_cost, actual_cost, state, parent, action):
        """
        Constructor
        """

        self.estimate_cost = estimate_cost
        self.actual_cost = actual_cost
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

        return self.estimate_cost < other.estimate_cost

    def __str__(self):
        return str(self.state)


Action = namedtuple('Action', ['location', 'direction'])
PathCost = namedtuple('PathCost', ['path', 'cost'])
