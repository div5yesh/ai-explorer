"""
CMSC 671 Fall 2018 – Homework 2
Divyesh Chitroda

References:
1. Line[181-210] - Adapted from Artificial Intelligence: A Modern Approach, 3rd. Edition, Stuart J. Russell and Peter Norvig, p. 84. Prentice Hall, 2009.
2. heapq module for frontier priority queue - Adapted from Documentation, The Python Standard Library, https://docs.python.org/3/library/heapq.html
3. Line[144] - operator overloading for membership testing - Adapted from Stackoverflow, Check if heapq contains value, https://stackoverflow.com/questions/25316694/check-if-heapq-contains-value

Libraries:
1. heapq - to store frontier nodes as priority queue and perform membership testing.
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
problemPathCost = {'p': 10, 's': 30, 'm': 100, 'w': sys.maxsize}

# cost of acceptable but not optimal path(calories)
# satisficity = 300

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
    # print(action)
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
    # calculate actual cost
    actualCost = node.actualCost + problemPathCost[problem[state[0]][state[1]]]
    # calculate hueristic cost
    heuristic = heuristicCost(state, goal)
    # calculate F(n) = estimated cost to reach the goal state
    estimateCost = actualCost + heuristic
    return Node(actualCost, actualCost, state, node, action)

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
    return (abs(goal[0] - state[0]) + abs(goal[1] - state[1])) * problemPathCost['p']

def getSolution(node):
    """
    Print the solution path by backtracking to the root node
    following throught all the parent nodes.

    Args:
        node: Object - Node. The node containing goal state at the end of the search.

    Returns: string. String of actions performed on root node
    to reach the goal node.
    """
    path = ""
    while node.parent:
        path = node.action + path
        node = node.parent

    return path

class Problem:

    def __init__(self, goal):
        self.goal = goal

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
                # if self.actualCost < other.actualCost:
                #     other = self
                return True

    def __lt__(self, other):
        """
        Less than operator overload to compare estimated costs for heapify
        comparisions in heapq, using the priority as estimated cost.
        """
        return self.actualCost < other.actualCost
    
    def __str__(self):
        return str(self.state)

def solve(start, goal, Problem, k = 10):
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
    beam = []

    startNode = Node(0, 0, start, None, None)
    # push the start node to the frontier
    heappush(frontier, startNode)
    beam.append(startNode)

    while (1):
        # if all nodes in the frontier are explored and path is not found, then
        # there exists no path.
        if len(frontier) == 0:
            return "Path does not exists."

        frontier = nsmallest(k, beam)
        beam = []
        # print("----------------------------------------------")
        # for item in frontier:
        #     print(item)
        
        # select state with least cost from frontier            
        for node in frontier:
            # add state to explored set
            explored.add(node.state)

            # get the list of all possible actions on the state
            Actions = findActions(Problem, node.state)

            # expand a node and generate children
            for action in Actions:            
                # generate a child node by applying actions to the current state
                neighbour = generateChild(Problem, goal, node, action)

                if neighbour != None:
                    # goal test the current node
                    goalNode = goalTest(neighbour, goal, frontier)
                    if goalNode:
                        # get the solution(seq. of actions)
                        return getSolution(goalNode)

                    # check if child is already explored or present in frontier and
                    # (Ref: Line 144)replace the frontier node with child if the child has lower cost
                    if neighbour.state not in explored and neighbour not in frontier:
                        # add node with current state and path cost to reach the node from
                        # the start state to the frontier
                        beam.append(neighbour)

                

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
    # for node in frontier:
    #     if node.state == goal and node.actualCost <= satisficity:
    #         return node

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
    terrain = [[random.choice(['M', 'P', 'S', 'W']) for i in range(0, size)] for j in range(0, size)]
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
    # print(solve((1, 0), (2, 2), [['p', 'p', 'p'], ['p', 'm', 'p'], ['s', 's', 's']]))
    # print(solve((0, 0), (2, 2), [['m','m','m','s'], ['m','m','m','s'], ['m','m','m','s'], ['p','p','p','p']]))
    # print(solve((0, 1), (2, 1), [['m', 'p', 'p', 'p', 'p'], ['m', 'm', 'm', 'm', 'p'], ['m', 'p', 'm', 'm', 'p'],
    #     ['m', 'p', 'm', 'm', 'p'], ['m', 'p', 'p', 'p', 'p']]))
    
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
    # randomTest1 = generateTestProblem()
    # # log the start time before solving
    # start = time.time()
    # print(solve(randomTest1[0], randomTest1[1], randomTest1[2]))
    # # log the end time after solving
    # end = time.time()
    # # print total time required to solve the problem
    # print(end - start)

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

test()