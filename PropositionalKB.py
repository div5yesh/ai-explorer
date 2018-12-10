from utils import *
from agent import BaseAgent
from sympy import *
from sympy.logic.boolalg import And, Not, conjuncts, to_cnf
from itertools import chain

class PropsitionalKB:
    def __init__(self, sentence = None):
        self.clauses = []
        if sentence:
            self.tell(sentence)
    
    def tell(self, sentence):
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def tellPercepts(self, game_map, map_objects):
        self.game_map = game_map
        self.map_objects = map_objects

    def entails(self, clauses, query, all_models):
        if len(clauses) > 0:
            first = clauses[0]
            rest = clauses[1:]
            models = chain(satisfiable(first & query, all_models=True))
            return chain(models, self.entails(rest, query, all_models))

    def ask(self, query):
        models = self.entails(self.clauses, query, all_models=True)
        # for i in models:
        #     print(i)
        return models

    def isMonster(self, state):
        if (state.x, state.y) in self.map_objects:
            if (isinstance(self.map_objects[(state.x, state.y)], StaticMonster)): return True
            else: return False

    def isSkeleton(self, state):
        if (state.x, state.y) in self.map_objects:
            if (isinstance(self.map_objects[(state.x, state.y)], BaseAgent)): return True
            else: return False

    def isBoss(self, state):
        if (state.x, state.y) in self.map_objects:
            if (isinstance(self.map_objects[(state.x, state.y)], Boss)): return True
            else: return False

    def isPowerUp(self, state):
        if (isinstance(self.map_objects[state], PowerUp)): return True
        else: return False

    def isSafe(self, state):
        return not(self.isBoss(state) and self.isSkeleton(state) and self.isMonster(state))
    
    def hasStrengthForBoss(self, strength):
        return strength >= 90

    def hasStrengthForDynamicMonster(self, strength):
        return strength > len(self.game_map)/2
    
    def hasStrengthForSkeleton(self, strength):
        return strength > 30

    def getKB(self):
        return self.clauses

    # def ask(self, query):
    #     checkClause = KBentailsAlpha(self.clauses, query)
    #     if (checkClause == {}): return True
    #     else: return False

# propkb = PropsitionalKB()
# a,b = symbols('a,b')
# propkb.tell(Implies(a,b))
# print('here is my KB')
# print(propkb.getKB())

# propkb.tell(symbols('p'))
# print('now my kb is: ')
# print(propkb.getKB())