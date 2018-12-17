# References:
# 1. Algorithm Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 270. Prentice Hall, 2009.
import copy
import math
import random
import sys
from collections import namedtuple
from itertools import product

from agent import BaseAgent
from base import State
from propositional_kb import PropositionalKB
from utils import *


class KBAgentRogue(BaseAgent):

    def __init__(self, height, width, initial_strength, name='KB_agent_rogue'):
        super().__init__(height=height, width=width, initial_strength=initial_strength, name=name)
        # persistent: KB, a knowledge base, initially the atemporal “wumpus physics”
        self.kb = PropositionalKB()

        self.visited = set()
        self.unvisited = {State(x) for x in product(range(width), range(height))}

        self.len_of_map_objects = 0

        self.frontiers = []
        self.power_ups = set()
        self.monsters = set()
        self.boss = None
        self.agents = set()

    def on_change_map_objects(self, map_objects):
        self.power_ups.clear()
        self.monsters.clear()
        self.boss = None
        self.agents.clear()
        self.frontiers.clear()

        for (loc, item) in map_objects:
            if isinstance(item, PowerUp):
                self.power_ups.add(loc)
            if isinstance(item, Boss):
                self.boss = loc
            elif isinstance(item, StaticMonster) or isinstance(item, DynamicMonster):
                self.monsters.add(loc)
            if isinstance(item, AgentPlaceholder):
                self.agents.add(loc)

        self.len_of_map_objects = len(map_objects)

    def step(self, location, strength, game_map, map_objects):
        location = State(location)
        self.visited.add(location)
        if location in self.unvisited:
            self.unvisited.remove(location)

        # TELL(KB, MAKE-PERCEPT-SENTENCE(percept, t))
        # self.kb.tell(self.makeSentence(game_map, map_objects))
        self.kb.tell_percepts(game_map, map_objects)

        # TELL the KB the temporal “physics” sentences for time t

        # safe ← {[x, y] : ASK(KB, OK t x,y) = true}
        # query = Query("ok", getStates())
        safe, unsafe = set(), set()
        for x in [State(x) for x in product(range(self.width), range(self.height))]:
            if self.kb.is_safe(x):
                safe.add(x)
            else:
                unsafe.add(x)

        # # if ASK(KB, Glitter t) = true then
        # query = Query("fight", monster, strength)
        if len(map_objects) != self.len_of_map_objects:
            self.on_change_map_objects(map_objects)

        if len(self.frontiers) == 0:
            # if self.kb.ask(query): ask strength to kb
            #     # plan ← [Grab] + PLAN-ROUTE(current,{[1,1]}, safe) + [Climb]
            #     actions = plan(current, {monsters, powerups}, safeStates)
            # decision is a tuple, where, decision[0] is path and decision[1] is the cost required to explore that path

            # ASK KB if the strength is greater than skeleton and the dynamic monster
            if len(self.monsters) > 0 and self.kb.has_enough_strength_for_monster(strength):
                # then fight the monster
                decision = plan(location, self.monsters, game_map, safe)
                self.frontiers = decision[0]

            # if plan is empty and ASK(KB, HaveArrow t) = true then
            # query = Query("powerup",{getStates(), strength})
            if len(self.frontiers) == 0 and self.kb.has_not_enough_strength(strength):
                # possible wumpus ← {[x, y] : ASK(KB,¬ Wx,y) = false}
                # plan ← PLAN-SHOT(current, possible wumpus, safe)
                decision = plan(location, self.power_ups, game_map, safe)
                self.frontiers = decision[0]

            if len(self.frontiers) == 0 and self.boss is not None:
                decision = plan(location, [self.boss, ], game_map, safe)
                if self.kb.has_enough_strength_for_boss(strength - decision[1]):
                    self.frontiers = decision[0]

            # if plan is empty then
            if len(self.frontiers) == 0:
                # unvisited ← {[x, y] : ASK(KB, Lt x,y  ) = false for all t ≤ t}
                # query = Query("unknown", getStates())
                # plan ← PLAN-ROUTE(current, unvisited ∩ safe, safe)
                decision = plan(location, self.unvisited.intersection(safe), game_map, safe)
                self.frontiers = decision[0]

            # if plan is empty then // no choice but to take a risk
            if len(self.frontiers) == 0:
                # not unsafe ← {[x, y] : ASK(KB,¬ OK t x,y) = false}
                # plan ← PLAN-ROUTE(current, unvisited, safe)
                decision = plan(location, self.unvisited, game_map, [])
                self.frontiers = decision[0]

            # # if plan is empty then
            # if len(actions) == 0:
            #     # plan ← PLAN-ROUTE(current,{[1, 1]}, safe) + [Climb]
            #     actions = plan(location, [self.boss], game_map, self.safe)

            # # TELL(KB, MAKE-ACTION-SENTENCE(action, t))
            # self.kb.tell(self.makeSentence(action))

        action = self.frontiers.pop(0)
        if game_map[action.location.x][action.location.y] == MapTiles.W:
            self.frontiers.clear()
            return self.step(location, strength, game_map, map_objects)
        else:
            return action.direction


def plan(start, goals, problem, states):
    if goals is None or len(goals) == 0:
        return [], sys.maxsize

    shape = problem.shape
    depth_limit = int(math.sqrt(shape[0] * shape[1]) / 2)

    if len(goals) > depth_limit:
        goals = random.choices(list(goals), k=depth_limit)

    searcher = DepthLimitedSearch(problem, states, depth_limit=depth_limit)
    path_costs = [x for x in [searcher.search(start, goal) for goal in goals if goal is not None] if x is not None]
    sorted(path_costs, key=lambda x: x[1], reverse=True)
    if len(path_costs) == 0:
        return [], sys.maxsize

    best_decision = path_costs[0]
    return best_decision.path, best_decision.cost


Action = namedtuple('Action', ['location', 'direction'])
PathCost = namedtuple('PathCost', ['path', 'cost'])


class DepthLimitedSearch(object):

    def __init__(self, problem, states, depth_limit):
        self.problem = problem
        self.states = states
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

    # agent = KBAgentRogue(10,10, 100)
# agent.step((3,2), 100, [
#     [MapTiles.U,MapTiles.U,MapTiles.U,MapTiles.U],
#     [MapTiles.U,MapTiles.U,MapTiles.U,MapTiles.U],
#     [MapTiles.U,MapTiles.S,MapTiles.P,MapTiles.S],
#     [MapTiles.U,MapTiles.W,MapTiles.M,MapTiles.S]], {(2,2): StaticMonster() })
