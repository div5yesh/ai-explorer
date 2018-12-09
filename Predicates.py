from utils import *
from agent import BaseAgent
    
def isMonster(self, state):
    if (isinstance(self.map_objects[state], StaticMonster)): return True
    else: return False

def isSkeleton(self, state):
    if (isinstance(self.map_objects[state], BaseAgent)): return True
    else: return False

def isBoss(self, state):
    if (isinstance(self.map_objects[state], Boss)): return True
    else: return False

def isPowerUp(self, state):
    if (isinstance(self.map_objects[state], PowerUp)): return True
    else: return False