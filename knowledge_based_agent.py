# References:
# 1. Algorithm Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 270. Prentice Hall, 2009.
import sys
from itertools import product

from a_star import a_star_search
from agent import BaseAgent
from base import State
from depth_limited import depth_limited_search
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

        for loc in map_objects:
            if isinstance(map_objects[loc], PowerUp):
                self.power_ups.add(loc)
            if isinstance(map_objects[loc], Boss):
                self.boss = loc
            elif isinstance(map_objects[loc], StaticMonster) or isinstance(map_objects[loc], DynamicMonster):
                self.monsters.add(loc)
            if isinstance(map_objects[loc], AgentPlaceholder):
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

        # TELL the KB the temporal “physics” sentences for time 't'

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

        while len(self.frontiers) == 0:
            # if self.kb.ask(query): ask strength to kb
            #     # plan ← [Grab] + PLAN-ROUTE(current,{[1,1]}, safe) + [Climb]
            #     actions = plan(current, {monsters, powerups}, safeStates)
            # decision is a tuple, where, decision[0] is path and decision[1] is the cost required to explore that path

            # ASK KB if the strength is greater than skeleton and the dynamic monster
            if len(self.monsters) > 0 and self.kb.has_enough_strength_for_monster(strength):
                # then fight the monster
                decision = plan(location, self.monsters, game_map, safe, algorithm='a-star')
                self.frontiers = decision[0]

            # if plan is empty and ASK(KB, HaveArrow t) = true then
            # query = Query("powerup",{getStates(), strength})
            if len(self.frontiers) == 0 and self.kb.has_not_enough_strength(strength):
                # possible wumpus ← {[x, y] : ASK(KB,¬ Wx,y) = false}
                # plan ← PLAN-SHOT(current, possible wumpus, safe)
                decision = plan(location, self.power_ups, game_map, safe, algorithm='a-star')
                self.frontiers = decision[0]
            
            # if plan is empty and ASK(KB, agentNearMe) = true then
            if len(self.frontiers) == 0:
                # possible wumpus ← {[x, y] : ASK(KB,¬ Wx,y) = false}
                # plan ← PLAN-SHOT(current, possible wumpus, safe)
                decision = plan(location, self.agents, game_map, safe, algorithm='a-star')
                self.frontiers = decision[0]

            if len(self.frontiers) == 0 and self.boss is not None:
                decision = plan(location, [self.boss, ], game_map, safe, algorithm='a-star')
                if self.kb.has_enough_strength_for_boss(strength - decision[1]):
                    self.frontiers = decision[0]

            # if plan is empty then
            if len(self.frontiers) == 0:
                # unvisited ← {[x, y] : ASK(KB, Lt x,y  ) = false for all t ≤ t}
                # query = Query("unknown", getStates())
                # plan ← PLAN-ROUTE(current, unvisited ∩ safe, safe)
                decision = plan(location, self.unvisited.intersection(safe), game_map, safe, algorithm='a-star')
                self.frontiers = decision[0]

            # if plan is empty then // no choice but to take a risk
            if len(self.frontiers) == 0:
                # not unsafe ← {[x, y] : ASK(KB,¬ OK t x,y) = false}
                # plan ← PLAN-ROUTE(current, unvisited, safe)
                decision = plan(location, self.unvisited, game_map, [], algorithm='depth-limited')
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

# conditioning on the algorithm 
def plan(start, goals, problem, states, algorithm='a-star'):
    if goals is None or len(goals) == 0:
        return [], sys.maxsize
    # if a-star search is used 
    if algorithm == 'a-star':
        results = [a_star_search(start, State(goal), problem, states) for goal in goals if goal is not None]
        results = sorted(results, key=lambda x: x[1])
        return results[0]
    # if depth-limited is used
    if algorithm == 'depth-limited':
        return depth_limited_search(start, goals, problem)

    raise ValueError

    # agent = KBAgentRogue(10,10, 100)
# agent.step((3,2), 100, [
#     [MapTiles.U,MapTiles.U,MapTiles.U,MapTiles.U],
#     [MapTiles.U,MapTiles.U,MapTiles.U,MapTiles.U],
#     [MapTiles.U,MapTiles.S,MapTiles.P,MapTiles.S],
#     [MapTiles.U,MapTiles.W,MapTiles.M,MapTiles.S]], {(2,2): StaticMonster() })
