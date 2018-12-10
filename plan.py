from Astar import *
import sys

def plan(start, goals, problem, states):
    bestDecision = tuple(([], sys.maxsize))
    if len(goals):
        for goal in goals:
                if goal:
                        nodeResult = AstarSearch(start, goal, problem, states)
                        if bestDecision[1] > nodeResult[1]:
                                bestDecision = nodeResult

    return bestDecision