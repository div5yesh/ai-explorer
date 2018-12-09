from utils import *
from agent import BaseAgent
from sympy import *
from sympy.logic.boolalg import And, Not, conjuncts, to_cnf

class PropKB:
    def __init__(self, sentence = None):
        self.clauses = []
        if sentence:
            self.tell(sentence)
    
    def tell(self, sentence):
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def tellPhysics(self, game_map, map_objects):
        self.game_map = game_map
        self.map_objects = map_objects

    # def ask(self, query):
    #     checkClause = KBentailsAlpha(self.clauses, query)
    #     if (checkClause == {}): return True
    #     else: return False