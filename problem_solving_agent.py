import copy
import math
import random

import numpy as np

from agent import BaseAgent
from utils import Directions, MapTiles, tile_cost


class Location(object):
    """
    Location class. It indicates (x, y) location.
    """

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], tuple):
                self._x = args[0][1]
                self._y = args[0][0]
            if isinstance(args[0], Location):
                self._x = args[0].x
                self._y = args[0].y
        elif len(args) == 2:
            self._x = args[0]
            self._y = args[1]

    @property
    def x(self):
        """
        Returns x-coordinate.

        :return: x-coordinate
        """

        return self._x

    @property
    def y(self):
        """
        Returns y-coordinate.

        :return: y-coordinate
        """

        return self._y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.x == other.x and self.y == other.y

    def north(self):
        return Location(self.x, self.y - 1)

    def south(self):
        return Location(self.x, self.y + 1)

    def west(self):
        return Location(self.x - 1, self.y)

    def east(self):
        return Location(self.x + 1, self.y)

    def __str__(self):
        return '(%d, %d)' % (self.x, self.y)


class GameMap(object):
    """
    Game map class.
    """

    def __init__(self, agent, game_map, map_objects):
        if isinstance(game_map, np.ndarray):
            self._game_map = game_map
        elif isinstance(game_map, GameMap):
            self._game_map = game_map._game_map

        self._agent = agent
        self._map_objects = {Location(x): obj for x, obj in map_objects.items()}

        shape = self._game_map.shape
        self._tmp_goal = Location(random.randint(0, shape[1] - 1), random.randint(0, shape[0] - 1))

    def __iter__(self):
        shape = self._game_map.shape
        for y in range(shape[0]):
            for x in range(shape[1]):
                yield Location(x, y), self._game_map[y][x]

    def __getitem__(self, item):
        if isinstance(item, Location):
            loc = item
            if loc.x < 0 or loc.y < 0 or loc.x >= self._game_map.shape[1] or loc.y >= self._game_map.shape[0]:
                return None
            return self._game_map[loc.y][loc.x]

    def update_goal(self, location, probs):
        """
        Updates the goal in priority order; 'medkit', 'skeleton', 'boss', and unexplored tile.
        """

        for location, obj in self._map_objects.items():
            if obj.label == 'medkit':
                self._tmp_goal = location
                return

            if obj.label == 'skeleton':
                self._tmp_goal = location
                return

            if obj.label == 'boss':
                self._tmp_goal = location
                return

        shape = self._game_map.shape
        while self._tmp_goal is None or location == self._tmp_goal or probs[self._tmp_goal.y][self._tmp_goal.x] == 0.0:
            self._tmp_goal = Location(random.randint(0, shape[1] - 1), random.randint(0, shape[0] - 1))

    def size(self):
        shape = self._game_map.shape
        return shape[0] * shape[1]

    def goal(self):
        return self._tmp_goal

    def available_directions(self, location):
        north = self._game_map[location.north()]
        south = self._game_map[location.south()]
        west = self._game_map[location.west()]
        east = self._game_map[location.east()]

        directions = [(Directions.NORTH, north), (Directions.SOUTH, south),
                      (Directions.WEST, west), (Directions.EAST, east)]

        return [x for x in directions if x[1] is not None and x[1] is not MapTiles.W]


class Path(object):
    """
    Path object.
    """

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], Path):
                self._start = copy.deepcopy(args[0]._start)
                self._directions = copy.deepcopy(args[0]._directions)
                self._locations = copy.deepcopy(args[0]._locations)
                self._tiles = copy.deepcopy(args[0]._tiles)
            else:
                self._start = args[0]
                self._directions = []
                self._locations = []
                self._tiles = []

    def append(self, direction, location, tile):
        copy = Path(self)

        copy._directions.append(direction)
        copy._locations.append(location)
        copy._tiles.append(tile)

        return copy

    def has(self, location):
        return location == self._start or location in self._locations

    def cost(self, game_map):
        _cost = 0
        for location, tile in zip(self._locations, self._tiles):
            if tile is not MapTiles.U:
                _cost = _cost + tile_cost[tile]
        return _cost

    def __iter__(self):
        for (direction, location) in zip(self._directions, self._locations):
            yield direction, location


class DepthLimitedPathSearcher(object):
    """
    Path Searcher using depth-limited search for the performance.
    """

    def __init__(self, agent, game_map, depth_limit=None):
        self._agent = agent
        self._game_map = game_map
        self._depth_limit = depth_limit if depth_limit else math.sqrt(game_map.size()) / 2

    def search(self, location, path=None, depth=0):
        if path is None:
            path = Path(location)

        paths = []
        goal = self._game_map.goal()
        for (direction, next_location, tile) in self.expand(location):
            if path.has(next_location):
                continue

            tile = self._game_map[next_location]
            p = path.append(direction, next_location, tile)
            if tile != MapTiles.U and depth < self._depth_limit:
                p = self.search(next_location, p, depth + 1)

            if p is not None:
                if next_location == goal:
                    return p

                paths.append(p)

        if len(paths) == 0:
            if depth == 0:
                raise ValueError('No available paths')
            return None

        lowest_cost_path = sorted(paths, key=lambda x: x.cost(self._game_map))[0] if len(paths) > 1 else paths[0]
        return lowest_cost_path

    def expand(self, location):
        directions = [(Directions.NORTH, location.north(), self._game_map[location.north()]),
                      (Directions.SOUTH, location.south(), self._game_map[location.south()]),
                      (Directions.WEST, location.west(), self._game_map[location.west()]),
                      (Directions.EAST, location.east(), self._game_map[location.east()])]

        return [x for x in directions if x[2] is not None and x[2] is not MapTiles.W]


class ProblemSolvingAgent(BaseAgent):

    def __init__(self, height, width, initial_strength, name='rogue_agent'):
        super().__init__(height=height, width=width,
                         initial_strength=initial_strength, name=name)

        self._probs = np.ones(shape=(width, height))
        self._frontiers = []
        self._map_objects_size = 0

    def step(self, location, strength, game_map, map_objects):
        location, game_map = Location(location), GameMap(self, game_map, map_objects)
        self.update(location, strength, game_map, map_objects)

        if len(self._frontiers) == 0:
            path = self.best_path(location, game_map)
            if path is None:
                raise ValueError('Reach to dead-end')

            for (direction, loc) in path:
                self._frontiers.append(direction)

        return self._frontiers.pop(0)

    def best_path(self, location, game_map):
        path_searcher = DepthLimitedPathSearcher(self, game_map)
        return path_searcher.search(location)

    def update(self, location, strength, game_map, map_objects):
        if self._map_objects_size != len(map_objects):
            self._map_objects_size = len(map_objects)

            self._probs[location.y][location.x] = 0.0

            for (loc, tile) in game_map:
                if tile == MapTiles.W:
                    self._probs[loc.y][loc.x] = 0.0

            p = 1.0 / np.count_nonzero(self._probs)
            self._probs[np.where(self._probs != 0.0)] = p

            game_map.update_goal(location, self._probs)
            self._frontiers.clear()


if __name__ == '__main__':
    from driver import GameDriver

    height, width = 10, 10
    initial_strength = 100
    num_powerups = 2
    num_monsters = 1
    num_dynamic_monsters = 1
    save_dir = 'map1/'
    verbose = False
    show_map = False
    map_type = 'emoji'
    map_file = None

    results = []
    count = 1
    for _ in range(count):
        agent = ProblemSolvingAgent(height, width, initial_strength)
        agents = [agent]

        game_driver = GameDriver(
            height=height, width=width,
            num_powerups=num_powerups,
            num_monsters=num_monsters,
            num_dynamic_monsters=num_dynamic_monsters,
            agents=agents,
            initial_strength=initial_strength,
            show_map=show_map, map_type=map_type,
            save_dir=save_dir, map_file=map_file)

        print('Starting game')
        try:
            res = game_driver.play(verbose=verbose)
        except:
            continue

        results.append(res)

    print(sum([1 for x in results if x]) / float(len(results)))
