from Astar import *
import sys

def plan(start, goals, problem, states):
    best = tuple(None, sys.maxsize)
    for goal in range(len(goals)):
        nodeResult = AstarSearch(start, goal, problem, states)
        if best[1] > nodeResult[1]:
            best = nodeResult

    return best[0]