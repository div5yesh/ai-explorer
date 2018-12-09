# References:
# 1. Algorithm Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 270. Prentice Hall, 2009.

from agentrogue import AgentRogue
from kb import KB

def KBAgentRogue(AgentRogue):

    def __init__(self, height, width, initial_strength, name='KB_agent_rogue'):
        super().__init__(height=height, width=width, initial_strength=initial_strength, name=name)
        # persistent: KB, a knowledge base, initially the atemporal “wumpus physics”
        self.kb = KB()

    def makeSentence(self, terrain, objects):
        pass

    def step(self, current, strength, game_map, map_objects):
        # TELL(KB, MAKE-PERCEPT-SENTENCE(percept, t))
        self.kb.tell(self.makeSentence(game_map, map_objects))

        # TELL the KB the temporal “physics” sentences for time t
        self.kb.tellPysics(game_map, map_objects)
        # safe ← {[x, y] : ASK(KB, OK t x,y) = true}
        query = Query("ok", getStates())
        safeStates = self.kb.ask(query)

        # if ASK(KB, Glitter t) = true then
        query = Query("fight", monster, strength)
        if self.kb.ask(query):
            # plan ← [Grab] + PLAN-ROUTE(current,{[1,1]}, safe) + [Climb]
            actions = planRoute(current, {monsters, powerups}, safe)
        
        # if plan is empty then
        if len(actions) == 0:
            # unvisited ← {[x, y] : ASK(KB, Lt x,y  ) = false for all t ≤ t}
            query = Query("unknown", getStates())
            unvisitedStates = self.kb.ask(query)

            # plan ← PLAN-ROUTE(current, unvisited ∩safe, safe)
            actions = planRoute(current, unvisitedStates + safeStates, safe)

        # if plan is empty and ASK(KB, HaveArrow t) = true then
        query = Query("powerup",{getStates(), strength})
        if len(actions) == 0 and self.kb.ask(query):
            # possible wumpus ← {[x, y] : ASK(KB,¬ Wx,y) = false}
            query = Query("powerup", {getStates(), strength})
            powerups = self.kb.ask(query)

            # plan ← PLAN-SHOT(current, possible wumpus, safe)
            actions = planPowerup(current, {powerups, strength}, safe)

        # if plan is empty then // no choice but to take a risk
        if len(actions) == 0:
            # not unsafe ← {[x, y] : ASK(KB,¬ OK t x,y) = false}
            query = Query("notok", getStates())
            unsafeStates = self.kb.ask(query)

            # plan ← PLAN-ROUTE(current, unvisited ∩not unsafe, safe)
            actions = planRoute(current, unsafeStates + unvisitedStates, safe)

        # if plan is empty then
        if len(actions) == 0:
            # plan ← PLAN-ROUTE(current,{[1, 1]}, safe) + [Climb]
            actions = planRoute(current, {boss}, safe)

        action ← POP(actions)
        # TELL(KB, MAKE-ACTION-SENTENCE(action, t))
        self.kb.tell(self.makeSentence(action))

        return action