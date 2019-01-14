import copy
import math
import random
import sys

from base import Action, PathCost
from utils import MapTiles, Directions


class DepthLimitedSearch(object):

    def __init__(self, problem, depth_limit):
        self.problem = problem
        self.depth_limit = depth_limit

    def search(self, start, goal):
        paths = self._search([], start, goal, 0)
        path_costs = [PathCost(path=path, cost=self.cost(path)) for path in paths]
        sorted(path_costs, key=lambda x: x.cost)
        return path_costs[0] if len(path_costs) > 0 else None

    def _search(self, past_path, current_location, goal, depth):
        children = self.expand(current_location, goal)
        if len(children) == 0 or depth > self.depth_limit:
            return [past_path, ]

        past_locations = [l for l, _ in past_path]
        results = []
        for child in children:
            if child.location in past_locations:
                continue

            path = copy.deepcopy(past_path)
            path.append(child)

            if self.is_unknown(child.location):
                results.append(path)
            else:
                for p in self._search(path, child.location, goal, depth + 1):
                    results.append(p)

        return results if len(results) > 0 else [past_path, ]

    def cost(self, path):
        costs = 0
        for location, direction in path:
            tile = self.problem[location.y][location.x]
            if tile == MapTiles.U:
                costs = costs - 1
                break

            costs = costs + tile.value

        return costs

    def expand(self, cur_loc, goal):
        children = []

        if cur_loc.x != goal.x:
            children.append(Action(location=cur_loc.move(Directions.WEST), direction=Directions.WEST))
            children.append(Action(location=cur_loc.move(Directions.EAST), direction=Directions.EAST))
        if cur_loc.y != goal.y:
            children.append(Action(location=cur_loc.move(Directions.NORTH), direction=Directions.NORTH))
            children.append(Action(location=cur_loc.move(Directions.SOUTH), direction=Directions.SOUTH))

        return [child for child in children if self.is_available(child.location)]

    def is_available(self, location):
        shape = self.problem.shape
        if location.x < 0 or location.x >= shape[0]:
            return False
        if location.y < 0 or location.y >= shape[1]:
            return False
        if self.is_wall(location):
            return False
        return True

    def is_wall(self, location):
        tile = self.problem[location.x][location.y]
        return tile == MapTiles.W

    def is_unknown(self, location):
        tile = self.problem[location.x][location.y]
        return tile == MapTiles.U


def depth_limited_search(start, goals, problem):
    shape = problem.shape
    depth_limit = int(math.sqrt(shape[0] * shape[1]) / 2)

    if len(goals) > depth_limit:
        goals = random.choices(list(goals), k=depth_limit)

    searcher = DepthLimitedSearch(problem, depth_limit=depth_limit)
    path_costs = [x for x in [searcher.search(start, goal) for goal in goals if goal is not None] if x is not None]
    sorted(path_costs, key=lambda x: x[1], reverse=True)
    if len(path_costs) == 0:
        return [], sys.maxsize

    best_decision = path_costs[0]
    return best_decision.path, best_decision.cost
