from utils import *
from agent import BaseAgent
from sympy import symbols

safe = symbols('safe')
monster = symbols('monster')
skeleton = symbols('skeleton')
boss = symbols('boss')
powerup = symbols('powerup')

def isMonster( state):
    if (isinstance(map_objects[state], StaticMonster)): return True
    else: return False

def isSkeleton( state):
    if (isinstance(map_objects[state], BaseAgent)): return True
    else: return False

def isBoss( state):
    if (isinstance(map_objects[state], Boss)): return True
    else: return False

def isPowerUp( state):
    if (isinstance(map_objects[state], PowerUp)): return True
    else: return False

def isSafe( state):
    pass