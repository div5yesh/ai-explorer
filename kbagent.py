# References:
# 1. Algorithm Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 270. Prentice Hall, 2009.

from agent import BaseAgent
from PropositionalKB import PropKB
from sympy.logic.boolalg import And, Not
from Predicates import isSafe, isMonster, isSkeleton, isBoss
from plan import plan

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

        if self.y < map_size - 1:
            yield State(self.x, self.y + 1)
        else:
            yield None

        if self.x < map_size - 1:
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

class KBAgentRogue(BaseAgent):

    def __init__(self, height, width, initial_strength, name='KB_agent_rogue'):
        super().__init__(height=height, width=width, initial_strength=initial_strength, name=name)
        # persistent: KB, a knowledge base, initially the atemporal “wumpus physics”
        self.kb = PropKB()
        # self.kb.tell(Not(monster) | Not(boss) >> safe)
        # self.kb.tell(Not(monster) | Not(skeleton) >> safe)

    # def makeSentence(self, game_map, map_objects):
    #     self.kb.tellPercepts(game_map, map_objects)

    def step(self, current, strength, game_map, map_objects):

        actions = []    
        current = State(current)
        # TELL(KB, MAKE-PERCEPT-SENTENCE(percept, t))
        # self.kb.tell(self.makeSentence(game_map, map_objects))
        self.kb.tellPercepts(game_map, map_objects)

        # TELL the KB the temporal “physics” sentences for time t
        
        # safe ← {[x, y] : ASK(KB, OK t x,y) = true}
        # query = Query("ok", getStates())
        safeStates = set()
        for neighbour in current.neighbours(len(game_map)):
            if self.kb.isSafe(neighbour):
                safeStates.add(neighbour)

        # # if ASK(KB, Glitter t) = true then
        # query = Query("fight", monster, strength)
        # if self.kb.ask(query):
        #     # plan ← [Grab] + PLAN-ROUTE(current,{[1,1]}, safe) + [Climb]
        #     actions = plan(current, {monsters, powerups}, safeStates)
        
        # if plan is empty then
        if len(actions) == 0:
            # unvisited ← {[x, y] : ASK(KB, Lt x,y  ) = false for all t ≤ t}
            # query = Query("unknown", getStates())
            query = ~visited
            unvisitedStates = self.kb.ask(query)

            # plan ← PLAN-ROUTE(current, unvisited ∩safe, safe)
            actions = plan(current, unvisitedStates.union(safeStates), safeStates)

        # if plan is empty and ASK(KB, HaveArrow t) = true then
        # query = Query("powerup",{getStates(), strength})
        query = powerup
        if len(actions) == 0 and self.kb.ask(query):
            # possible wumpus ← {[x, y] : ASK(KB,¬ Wx,y) = false}
            query = Query("powerup", {getStates(), strength})
            powerups = self.kb.ask(query)

            # plan ← PLAN-SHOT(current, possible wumpus, safe)
            actions = plan(current, {powerups, strength}, safeStates)

        # if plan is empty then // no choice but to take a risk
        if len(actions) == 0:
            # not unsafe ← {[x, y] : ASK(KB,¬ OK t x,y) = false}
            query = Query("notok", getStates())
            unsafeStates = self.kb.ask(query)

            # plan ← PLAN-ROUTE(current, unvisited ∩not unsafe, safe)
            actions = plan(current, unsafeStates.union(unvisitedStates), safeStates)

        # if plan is empty then
        if len(actions) == 0:
            # plan ← PLAN-ROUTE(current,{[1, 1]}, safe) + [Climb]
            actions = plan(current, {boss}, safeStates)

        action = actions.pop()
        # TELL(KB, MAKE-ACTION-SENTENCE(action, t))
        self.kb.tell(self.makeSentence(action))

        return action


agent = KBAgentRogue(10,10, 100)
agent.step((3,2), 100, [
    ['u','u','u','u'], 
    ['u','u','u','u'], 
    ['u','s','p','s'], 
    ['u','w','m','s']], {(2,2):"skeleton"})