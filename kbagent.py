# References:
# 1. Algorithm Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 270. Prentice Hall, 2009.

from agent import BaseAgent
from PropositionalKB import PropsitionalKB
from sympy.logic.boolalg import And, Not
from Predicates import isSafe, isMonster, isSkeleton, isBoss
from plan import plan
from utils import *

class KBAgentRogue(BaseAgent):

    def __init__(self, height, width, initial_strength, name='KB_agent_rogue'):
        super().__init__(height=height, width=width, initial_strength=initial_strength, name=name)
        # persistent: KB, a knowledge base, initially the atemporal “wumpus physics”
        self.kb = PropsitionalKB()
        # self.kb.tell(Not(monster) | Not(boss) >> safe)
        self.visited = set()
        self.unvisited = set()
        self.powerups = set()
        self.monsters = set()
        self.boss = None
        self.agents = set()
        self.safe = set()
        self.unsafe = set()
        # self.kb.tell(Not(monster) | Not(skeleton) >> safe)

    # def makeSentence(self, game_map, map_objects):
    #     self.kb.tellPercepts(game_map, map_objects)

    def step(self, location, strength, game_map, map_objects):
        input()
        actions = []    
        location = State(location)
        self.visited.add(location)
        self.unvisited.remove(location)
        # TELL(KB, MAKE-PERCEPT-SENTENCE(percept, t))
        # self.kb.tell(self.makeSentence(game_map, map_objects))
        self.kb.tellPercepts(game_map, map_objects)

        # TELL the KB the temporal “physics” sentences for time t
        
        # safe ← {[x, y] : ASK(KB, OK t x,y) = true}
        # query = Query("ok", getStates())
        for neighbour in location.neighbours(len(game_map)):
            if neighbour:
                if neighbour not in self.visited:
                    self.unvisited.add(neighbour)
                if self.kb.isSafe(neighbour):
                    self.safe.add(neighbour)
                else:
                    self.unsafe.add(neighbour)

        print(self.safe)

        # # if ASK(KB, Glitter t) = true then
        # query = Query("fight", monster, strength)
        for (loc, item) in map_objects:
            # self.agents = set() == ??????
            if isinstance(item, PowerUp):
                self.powerups.add(loc)
            if isinstance(item, Boss):
                self.boss = loc
            elif isinstance(item, StaticMonster):
                self.monsters.add(loc)
            if isinstance(item, BaseAgent):
                self.agents.add(loc)

        # if self.kb.ask(query): ask strength to kb
        #     # plan ← [Grab] + PLAN-ROUTE(current,{[1,1]}, safe) + [Climb]
        #     actions = plan(current, {monsters, powerups}, safeStates)
        actions = plan(location, [self.boss], game_map, self.safe) # strenght ??????????
        
        # if plan is empty then
        if len(actions) == 0:
            # unvisited ← {[x, y] : ASK(KB, Lt x,y  ) = false for all t ≤ t}
            # query = Query("unknown", getStates())

            # plan ← PLAN-ROUTE(current, unvisited ∩safe, safe)
            actions = plan(location, self.unvisited.intersection(self.safe), game_map, self.safe)

        # if plan is empty and ASK(KB, HaveArrow t) = true then
        # query = Query("powerup",{getStates(), strength})
        if len(actions) == 0 and self.kb.hasStrength(strength):
            # possible wumpus ← {[x, y] : ASK(KB,¬ Wx,y) = false}
            # plan ← PLAN-SHOT(current, possible wumpus, safe)
            actions = plan(location, self.powerups, game_map, self.safe)

        # if plan is empty then // no choice but to take a risk
        if len(actions) == 0:
            # not unsafe ← {[x, y] : ASK(KB,¬ OK t x,y) = false}
            # plan ← PLAN-ROUTE(current, unvisited ∩not unsafe, safe)
            actions = plan(location, self.unsafe.intersection(self.unvisited), game_map, self.safe)

        # if plan is empty then
        if len(actions) == 0:
            # plan ← PLAN-ROUTE(current,{[1, 1]}, safe) + [Climb]
            actions = plan(location, [self.boss], game_map, self.safe)

        action = actions.pop()
        # # TELL(KB, MAKE-ACTION-SENTENCE(action, t))
        # self.kb.tell(self.makeSentence(action))

        return action


# agent = KBAgentRogue(10,10, 100)
# agent.step((3,2), 100, [
#     [MapTiles.U,MapTiles.U,MapTiles.U,MapTiles.U], 
#     [MapTiles.U,MapTiles.U,MapTiles.U,MapTiles.U], 
#     [MapTiles.U,MapTiles.S,MapTiles.P,MapTiles.S], 
#     [MapTiles.U,MapTiles.W,MapTiles.M,MapTiles.S]], {(2,2): StaticMonster() })