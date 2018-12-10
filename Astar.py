from heapq import *
import random
import time
from utils import *
import sys

# path cost for traversing various terrains.
# Mountain = 100calories, Sand = 30calories, Path = 10calories
tileCost = {MapTiles.P: 1, MapTiles.S: 3, MapTiles.M: 10, MapTiles.W: sys.maxsize, MapTiles.U: sys.maxsize}

# cost of acceptable but not optimal path(calories)
# satisficity = 300

def findActions(size, state, problem):
    """
    Find all legal actions allowed on the state.
    Args:
        size: int. Size of the problem terrain.
        state: tuple - (x,y). State of the agent on which to perform actions.
    Returns: [] -> list of actions.
    """
    legalActions = []
    if state.x > 0 and (problem[state.x - 1][state.y] != MapTiles.W and problem[state.x - 1][state.y] != MapTiles.U):
        legalActions.append(Directions.NORTH)
    if state.x < size and (problem[state.x + 1][state.y] != MapTiles.W and problem[state.x + 1][state.y] != MapTiles.U):
        legalActions.append(Directions.SOUTH)
    if state.y > 0 and (problem[state.x][state.y - 1] != MapTiles.W and problem[state.x][state.y - 1] != MapTiles.U):
        legalActions.append(Directions.WEST)
    if state.y < size and (problem[state.x][state.y + 1] != MapTiles.W and problem[state.x][state.y + 1] != MapTiles.U):
        legalActions.append(Directions.EAST)
    return legalActions

def applyAction(state, action):
    """
    Generate next state by performing the action on the state.
    Args:
        state: tuple - (x,y). State of the agent.
        action: character - 'N'. Action to perform.
    Returns: tuple -> (x,y). Next state of the agent.
    """
    return state.move(action)

def generateChild(problem, goal, node, action):
    """
    Generate the child node by performing the legal action on the current state
    and calculating the estimated cost to reach to the goal state and actual cost to
    reach to the current state from the start state.
    Args:
        problem: 2d list of characters - [['m','p'],['s','p']]. Problem with terrain as characters.
        goal: tuple - (x,y). Goal state to reach.
        node: Object - Node. Node object representing current state.
        action: character - 'S'. Action to perform on the state.
    Returns: Object - Node. The Child node.
    """
    # get the next state
    state = applyAction(node.state, action)
    # calculate actual cost
    actualCost = node.actualCost + tileCost[problem[state.x][state.y]]
    # calculate hueristic cost
    heuristic = heuristicCost(state, goal)
    # calculate F(n) = estimated cost to reach the goal state
    estimateCost = actualCost + heuristic
    return Node(estimateCost, actualCost, state, node, action)

def heuristicCost(state, goal):
    """
    Calculate the heuristic cost i.e. the Manhattan distance, to reach the goal
    from current state. This is the estimation of how far the goal state is from
    current state.
    Args:
        state: tuple(x,y). The current state.
        goal: tuple(x,y). The goal state.
    Returns: int. Estimated cost to reach the goal
    """
    return (abs(goal.x - state.x) + abs(goal.y - state.y)) * tileCost[MapTiles.PATH]

def getSolution(node):
    """
    Print the solution path by backtracking to the root node
    following throught all the parent nodes.
    Args:
        node: Object - Node. The node containing goal state at the end of the search.
    Returns: string. String of actions performed on root node
    to reach the goal node.
    """
    nodeCost = node.actualCost
    path = []
    while node.parent:
        path.insert(0, node.action)
        node = node.parent

    return (path, nodeCost)

def AstarSearch(start, goal, Problem, safeStates):
    """
    Find the list of actions to perform on the start state to reach the goal
    state through optimal path with least cost.
    Args:
        start: tuple - (x,y). Start state of the agent
        goal: tuple - (x,y). Goal state to reach.
        problem: 2d list of characters - [['m','p'],['s','p']]. Problem with terrain as characters.
    Returns: string. Sequence of actions to take on start state to reach
    the goal state.
    """
    explored = set()
    frontier = []

    # push the start node to the frontier
    heappush(frontier, Node(heuristicCost(start, goal), 0, start, None, None))

    while (1):
        # if all nodes in the frontier are explored and path is not found, then
        # there exists no path.
        if len(frontier) == 0:
            return ([], sys.maxsize)

        # select state with least cost from frontier
        node = heappop(frontier)
        # print(node.state)
        # goal test the current node
        goalNode = goalTest(node, goal, frontier)
        if goalNode:
            # get the solution(seq. of actions)
            return getSolution(goalNode)

        # add state to explored set
        explored.add(node.state)

        # get the list of all possible actions on the state
        Actions = findActions(len(Problem) - 1, node.state, Problem)
        # expand a node and generate children
        for action in Actions:
            # generate a child node by applying actions to the current state
            child = generateChild(Problem, goal, node, action)
            if child != None:
                # check if child is already explored or present in frontier and
                # (Ref: Line 144)replace the frontier node with child if the child has lower cost
                if child.state not in explored and child not in frontier:
                    # add node with current state and path cost to reach the node from
                    # the start state to the frontier
                    # if the safeStates passed from the plan is in the frontier then only it will consider it
                    if len(safeStates) == 0 or child.state in safeStates:
                        heappush(frontier, child)


def goalTest(node, goal, frontier):
    """
    Test whether the goal state has been reached, if not find a goal state
    in frontier that is satisfiable(<= 300 calories), but not optimal.
    Args:
        node: Object - Node. The node to test for goal.
        goal: tuple(x,y). The goal state.
        frontier: []. list of frontier nodes prioritized by estimated cost
        to reach the goal.
    Returns: Object- Node. The goal node that is either satisfiable or optimal.
    """
    if node.state == goal:
        return node

def generateTestProblem():
    """
    Generates random problem with m, p & s terrain of size from 5x5 to 100x100.
    Selects random size of the terrain, random start and goal state.
    Returns: tuple(start, goal, terrain). The random problem with random terrain and states.
    """
    size = random.randint(5, 100)
    print(size)
    start = (random.randint(0, size - 1), random.randint(0, size - 1))
    print(start)
    goal = (random.randint(0, size - 1), random.randint(0, size - 1))
    print(goal)
    terrain = [[random.choice(['m', 'p', 's']) for i in range(0, size)] for j in range(0, size)]
    # print the terrain matrix if required
    # for i in range(0, size):
    #     print(terrain[i])

    return (start, goal, terrain)

def test():
    """
    Known Test Examples
    1. (3x3)matrix, start = (1, 0), goal = (2, 2), path = NEESS
    2. (4x4)matrix, start = (0, 0), goal = (2, 2), path = SSSEEN
    3. (5x5)matrix, start = (0, 1), goal = (2, 1), path = SS
    """
    print(AstarSearch((1, 0), (2, 2), [['p', 'p', 'p'], ['p', 'm', 'p'], ['s', 's', 's']]))
    print(AstarSearch((0, 0), (2, 2),
                [['m', 'm', 'm', 's'], ['m', 'm', 'm', 's'], ['m', 'm', 'm', 's'], ['p', 'p', 'p', 'p']]))
    print(
        AstarSearch((0, 1), (2, 1), [['m', 'p', 'p', 'p', 'p'], ['m', 'm', 'm', 'm', 'p'], ['m', 'p', 'm', 'm', 'p'],
                               ['m', 'p', 'm', 'm', 'p'], ['m', 'p', 'p', 'p', 'p']]))

    """
    Testing randomly generated problems
    """
    randomTest1 = generateTestProblem()
    # log the start time before solving
    start = time.time()
    print(AstarSearch(randomTest1[0], randomTest1[1], randomTest1[2]))
    # log the end time after solving
    end = time.time()
    # print total time required to solve the problem
    print(end - start)

"""
Randomly Generated Test Examples:
1. (8x8)matrix, start = (0, 6), goal = (5, 0), path = SSSSSWWWWWW
[['s', 'm', 'p', 's', 'p', 'p', 'p', 'm'],
 ['m', 's', 'm', 'm', 'm', 'p', 'p', 's'],
 ['p', 's', 's', 'p', 's', 'm', 'p', 'm'],
 ['m', 'p', 'm', 'm', 'p', 'm', 'p', 'p'],
 ['m', 'm', 'p', 'm', 's', 'm', 's', 's'],
 ['p', 'm', 'p', 'm', 'p', 's', 's', 's'],
 ['m', 'p', 's', 'p', 'm', 'p', 'm', 's'],
 ['m', 'p', 's', 'p', 's', 's', 's', 'm']]
2. (1000x1000)matrix, time = 490seconds, start = (218, 794), goal = (299, 503), path = WWWSSWWWWWWNWWSWWWSWWWW
SSWWWWWNWWWWWSSSSSWSWWWWWSWWWWWWSWWWWWWWWSWWWWSSSWWWWWWWSWWSSSWSWSWWWWWSWWWSWSWWSWWWSWWWNWWSSWSSWSWSWWWNWWWWWN
WWWNNWNWWWWSSWWWNWWSWWWWWNWWWWWNWWWWWWWSSWSWWWSWWNWNNNNWWWNWWWNWWWWNWWWWWWWWSWWSWWSWWWSSWWWWWWWWNWWWSWSWSSSWWW
SSSWWWSSWWSWSSWWWWWNNWWWWWWWWWWWWSSWWSWWSSWSSSWSSWWSWSWWWNWWWWWWWWSWWWSWWSSWSSSSWWWWSWWSWWWWWWWSSSSSSWWWWWSSWW
WWNWWNWWWWWSWWNWWWWWWWSSWWWSWSSWSSSWWSWSWWWWWWWWWWSWWWSSSWWSWSWWWWWWWWW
"""

# test()



