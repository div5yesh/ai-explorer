from Astar import *

def plan(start, goals, problem, states):
    best = ()
    for goal in range(len(goals)):
        nodeResult = solve(start, goal, problem, states)
        best(nodeResult)
        if best(1) > nodeResult(1):
            best = nodeResult

    return best(0)

