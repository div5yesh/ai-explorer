"""
CMSC 671 Fall 2018 – Project - AI-Explorer
Team Name: Agent Rogue
Team Members: Anushree Desai, Hakju Oh, Shree Hari, Divyesh Chitroda
References:
1. Line[181-210] - Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 84. Prentice Hall, 2009.
2. heapq module for beam priority queue - Adapted from Documentation, The Python Standard Library, https://docs.python.org/3/library/heapq.html
3. Line[144] - operator overloading for membership testing - Adapted from Stackoverflow, Check if heapq contains value, https://stackoverflow.com/questions/25316694/check-if-heapq-contains-value
Libraries:
1. heapq - to store beam nodes as priority queue and perform membership testing.
2. random - to generate random size problems with random start and goal state.
3. time - to calculate time taken for the algorithm to solve the problem.
---------------------------------------------------------------------------------
"""
from heapq import *
import random
import time
import sys

# path cost for traversing various terrains.
# Mountain = 100calories, Sand = 30calories, Path = 10calories
problemPathCost = {'p': 10, 's': 30, 'm': 100, 'w': 1000, 'u': -300}

BEAM_SIZE = 4

def findActions(problem, state):
    """
    Find all legal actions allowed on the state.
    Args:
        size: int. Size of the problem terrain.
        state: tuple - (x,y). State of the agent on which to perform actions.
    Returns: [] -> list of actions.
    """
    size = len(problem) - 1
    legalActions = []
    if state[0] > 0 and problem[state[0] - 1][state[1]] != 'w':
        legalActions.append('N')
    if state[0] < size and problem[state[0] + 1][state[1]] != 'w':
        legalActions.append('S')
    if state[1] > 0 and problem[state[0]][state[1] - 1] != 'w':
        legalActions.append('W')
    if state[1] < size and problem[state[0]][state[1] + 1] != 'w':
        legalActions.append('E')
    return legalActions

def applyAction(state, action):
    """
    Generate next state by performing the action on the state.
    Args:
        state: tuple - (x,y). State of the agent.
        action: character - 'N'. Action to perform.
    Returns: tuple -> (x,y). Next state of the agent.
    """
    if action == 'N':
        return (state[0] - 1, state[1])

    if action == 'E':
        return (state[0], state[1] + 1)

    if action == 'W':
        return (state[0], state[1] - 1)

    if action == 'S':
        return (state[0] + 1, state[1])

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
    # calculate hueristic cost
    estimateCost = evaluateCurrentPosition(problem, state)
    return Node(estimateCost, 0, state, node, action)

def generateBacktrackNode(problem, goal, node, action):
    state = applyAction(node.state, action)
    estimateCost = node.actualCost + problemPathCost[problem[state[0]][state[1]]]
    return Node(estimateCost, 0, state, node, action)

def neighbours(state, size):
    # topleft
    # if(state[0] > 0 and state[1] > 0):
    #     yield (state[0] - 1, state[1] - 1)
    # else:
    #     yield None
    # top
    if state[0] > 0:
        yield (state[0] - 1, state[1])
    else:
        yield None
    # topright
    # if state[0] > 0 and state[1] < size:
    #     yield (state[0] - 1, state[1] + 1)
    # else:
    #     yield None
    # right
    if state[1] < size:
        yield (state[0], state[1] + 1)
    else:
        yield None
    # bottomright
    # if state[0] < size and state[1] > size:
    #     yield (state[0] + 1, state[1] + 1)
    # else:
    #     yield None
    # bottom
    if state[0] < size:
        yield (state[0] + 1, state[1])
    else:
        yield None
    # bottomleft
    # if state[0] < size and state[1] > 0:
    #     yield (state[0] + 1, state[1] - 1)
    # else:
    #     yield None
    # left
    if state[1] > 0:
        yield (state[0], state[1] - 1)
    else:
        yield None

def evaluateCurrentPosition(problem, state):
    value = problemPathCost[problem[state[0]][state[1]]]
    for neighbour in neighbours(state, len(problem) - 1):
        if neighbour == None:
            value += 1000
        else:
            value += problemPathCost[problem[neighbour[0]][neighbour[1]]]

    return value

def getExploredStates(node):
    """
    Print the solution path by backtracking to the root node
    following throught all the parent nodes.
    Args:
        node: Object - Node. The node containing goal state at the end of the search.
    Returns: string. String of actions performed on root node
    to reach the goal node.
    """
    path = []
    while node.parent:
        path.insert(0, node.state)
        node = node.parent

    return path

class Node:
    """
    Node object for bookeeping of the current state, parent node for backtracking,
    action performed to generate the node, actual cost and estimated cost.
    """
    def __init__(self, estimateCost, actualCost, state, parent, action):
        """
        Constructor
        """
        self.estimateCost = estimateCost
        self.actualCost = actualCost
        self.state = state
        self.parent = parent
        self.action = action

    def __eq__(self, other):
        """
        Equal operator overload for membership testing of states in heapq
        and replace the node having state with higher estimated cost if
        node already present.
        """
        if other:
            if self.state == other.state:
                return True

    def __lt__(self, other):
        """
        Less than operator overload to compare estimated costs for heapify
        comparisions in heapq, using the priority as estimated cost.
        """
        return self.estimateCost < other.estimateCost

    def __str__(self):
        return str(self.state)

def getBestNodeDistance(current, best):
    return (abs(current[0] - best[0]) + abs(current[1] - best[1]))

def backtrackSearch(start, goal, problem):

    explored = set()
    frontier = []
    node = Node(0, 0, start.state, None, None)
    heappush(frontier, node)
    while (True):
        if len(frontier) == 0:
            return "Path does not exists."

        node = heappop(frontier)
        if goalTest(node, goal.state):
            return getExploredStates(node)

        explored.add(node.state)
        Actions = findActions(problem, node.state)
        for action in Actions:
            neighbour = generateBacktrackNode(problem, goal, node, action)
            if neighbour != None:
                if neighbour not in frontier and neighbour.state not in explored:
                    heappush(frontier, neighbour)

def solve(start, goal, problem):
    """
    Find the list of actions to perform on the start state to reach the goal
    state throug optimal path with least cost.
    Args:
        start: tuple - (x,y). Start state of the agent
        goal: tuple - (x,y). Goal state to reach.
        problem: 2d list of characters - [['m','p'],['s','p']]. Problem with terrain as characters.
    Returns: string. Sequence of actions to take on start state to reach
    the goal state.
    """
    explored = set()
    frontier = []
    node = Node(0, 0, start, None, None)
    # push the start node to the beam
    heappush(frontier, node)
    explorationPath = []

    while (True):
        # if all nodes in the beam are explored and path is not found, then
        # there exists no path.
        if len(frontier) == 0:
            return "Path does not exists."

        prevnode = node
        node = heappop(frontier)

        if getBestNodeDistance(prevnode.state, node.state) > 1:
            explorationPath.extend(backtrackSearch(prevnode, node, problem))
        else:
            explorationPath.append(node.state)

        explored.add(node.state)
        # get the list of all possible actions on the state
        Actions = findActions(problem, node.state)
        # expand a node and generate children
        for action in Actions:
            # generate a child node by applying actions to the current state
            neighbour = generateChild(problem, goal, node, action)

            if neighbour != None:
                # goal test the current node
                if goalTest(neighbour, goal):
                    explorationPath.append(goal)
                    # get the solution(seq. of actions)
                    return getExploredPath(explorationPath)

                # check if child is already explored or present in beam
                if neighbour not in frontier and neighbour.state not in explored:
                    #add node to frontier only if it can contain within best k nodes
                    heappush(frontier, neighbour)
                    if(len(frontier) > BEAM_SIZE):
                        del frontier[-1]

def getExploredPath(path):
    directionalPath = ""
    for i in range(len(path)-1):
        if path[i][0] > path[i + 1][0]:
            directionalPath = directionalPath + "N"
        elif path[i][0] < path[i + 1][0]:
            directionalPath = directionalPath + "S"
        elif path[i][1] > path[i+1][1]:
            directionalPath = directionalPath + "W"
        elif path[i][1] < path[i+1][1]:
            directionalPath = directionalPath + "E"
        else:
            directionalPath = directionalPath + "*"

    return directionalPath

def goalTest(node, goal):
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

def generateTestProblem(printTerrain = False):
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
    terrain = [[random.choice(['m', 'p', 's', 'w']) for i in range(0, size)] for j in range(0, size)]

    # print the terrain matrix if required
    if printTerrain:
        for i in range(0, size):
            print(terrain[i])

    return (start, goal, terrain)

def test(random = False):
    """
    Known Test Examples
    """

    print(solve((6, 7), (6, 2), [
        ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['m', 'm', 's', 's', 's', 'p', 'p', 'w'],
        ['s', 's', 'p', 's', 'p', 's', 'm', 'w'],
        ['p', 'w', 'm', 's', 's', 's', 'w', 'w'],
        ['w', 'w', 'm', 'w', 'w', 'm', 'p', 'p'],
        ['w', 'p', 'w', 'w', 's', 'p', 'w', 'm'],
        ['m', 's', 's', 'w', 'w', 'p', 'p', 'p'],
        ['s', 's', 'p', 'm', 'm', 'p', 'w', 'w']
    ]))

    """
    Testing randomly generated problems
    """
    if random:
        randomTest1 = generateTestProblem()
        # log the start time before solving
        start = time.time()
        print(solve(randomTest1[0], randomTest1[1], randomTest1[2]))
        # log the end time after solving
        end = time.time()
        # print total time required to solve the problem
        print(end - start)

test()