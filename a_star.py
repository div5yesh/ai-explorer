import random
import sys
import time
from heapq import *

from base import Node, Action
from utils import *

# path cost for traversing various terrains.
# Mountain = 100calories, Sand = 30calories, Path = 10calories
tile_cost = {MapTiles.P: 1, MapTiles.S: 3, MapTiles.M: 10, MapTiles.W: sys.maxsize, MapTiles.U: sys.maxsize}


# cost of acceptable but not optimal path(calories)
# satisficity = 300

def find_actions(size, state, problem):
    """
    Find all legal actions allowed on the state.
    Args:
        size: int. Size of the problem terrain.
        state: tuple - (x,y). State of the agent on which to perform actions.
    Returns: [] -> list of actions.
    """
    legal_actions = []
    if state.x > 0 and (problem[state.x - 1][state.y] != MapTiles.W and problem[state.x - 1][state.y] != MapTiles.U):
        legal_actions.append(Directions.NORTH)
    if state.x < size and (problem[state.x + 1][state.y] != MapTiles.W and problem[state.x + 1][state.y] != MapTiles.U):
        legal_actions.append(Directions.SOUTH)
    if state.y > 0 and (problem[state.x][state.y - 1] != MapTiles.W and problem[state.x][state.y - 1] != MapTiles.U):
        legal_actions.append(Directions.WEST)
    if state.y < size and (problem[state.x][state.y + 1] != MapTiles.W and problem[state.x][state.y + 1] != MapTiles.U):
        legal_actions.append(Directions.EAST)
    return legal_actions


def apply_action(state, action):
    """
    Generate next state by performing the action on the state.
    Args:
        state: tuple - (x,y). State of the agent.
        action: character - 'N'. Action to perform.
    Returns: tuple -> (x,y). Next state of the agent.
    """
    return state.move(action)


def generate_child(problem, goal, node, action):
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
    state = apply_action(node.state, action)
    # calculate actual cost
    actual_cost = node.actual_cost + tile_cost[problem[state.x][state.y]]
    # calculate heuristic cost
    heuristic = heuristic_cost(state, goal)
    # calculate F(n) = estimated cost to reach the goal state
    estimate_cost = actual_cost + heuristic
    return Node(estimate_cost, actual_cost, state, node, action)


def heuristic_cost(state, goal):
    """
    Calculate the heuristic cost i.e. the Manhattan distance, to reach the goal
    from current state. This is the estimation of how far the goal state is from
    current state.
    Args:
        state: tuple(x,y). The current state.
        goal: tuple(x,y). The goal state.
    Returns: int. Estimated cost to reach the goal
    """
    return (abs(goal.x - state.x) + abs(goal.y - state.y)) * tile_cost[MapTiles.PATH]


def get_solution(node):
    """
    Print the solution path by backtracking to the root node
    following through all the parent nodes.
    Args:
        node: Object - Node. The node containing goal state at the end of the search.
    Returns: string. String of actions performed on root node
    to reach the goal node.
    """
    node_cost = node.actual_cost
    path = []
    while node.parent:
        path.insert(0, Action(location=node.state, direction=node.action))
        node = node.parent

    return path, node_cost


def a_star_search(start, goal, problem, safe_states):
    """
    Find the list of actions to perform on the start state to reach the goal
    state through optimal path with least cost.
    Args:
        start: tuple - (x,y). Start state of the agent
        goal: tuple - (x,y). Goal state to reach.
        problem: 2d list of characters - [['m','p'],['s','p']]. Problem with terrain as characters.
        safe_states:
    Returns: string. Sequence of actions to take on start state to reach
    the goal state.
    """
    explored = set()
    frontier = []

    # push the start node to the frontier
    heappush(frontier, Node(0, 0, start, None, None))

    while True:
        # if all nodes in the frontier are explored and path is not found, then
        # there exists no path.
        if len(frontier) == 0:
            return [], sys.maxsize

        # select state with least cost from frontier
        node = heappop(frontier)
        # print(node.state)
        # goal test the current node
        goal_node = goal_test(node, goal, frontier)
        if goal_node:
            # get the solution(seq. of actions)
            return get_solution(goal_node)

        # add state to explored set
        explored.add(node.state)

        # get the list of all possible actions on the state
        actions = find_actions(len(problem) - 1, node.state, problem)
        # expand a node and generate children
        for action in actions:
            # generate a child node by applying actions to the current state
            child = generate_child(problem, goal, node, action)
            if child is not None:
                # check if child is already explored or present in frontier and
                # (Ref: Line 144)replace the frontier node with child if the child has lower cost
                if child.state not in explored and child not in frontier:
                    # add node with current state and path cost to reach the node from
                    # the start state to the frontier
                    # if the safeStates passed from the plan is in the frontier then only it will consider it
                    if len(safe_states) == 0 or child.state in safe_states:
                        heappush(frontier, child)


def goal_test(node, goal, frontier):
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


def generate_test_problem():
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
    print(a_star_search((1, 0), (2, 2), [['p', 'p', 'p'], ['p', 'm', 'p'], ['s', 's', 's']]))
    print(a_star_search((0, 0), (2, 2),
                        [['m', 'm', 'm', 's'], ['m', 'm', 'm', 's'], ['m', 'm', 'm', 's'], ['p', 'p', 'p', 'p']]))
    print(
        a_star_search((0, 1), (2, 1), [['m', 'p', 'p', 'p', 'p'], ['m', 'm', 'm', 'm', 'p'], ['m', 'p', 'm', 'm', 'p'],
                                       ['m', 'p', 'm', 'm', 'p'], ['m', 'p', 'p', 'p', 'p']]))

    """
    Testing randomly generated problems
    """
    randomTest1 = generate_test_problem()
    # log the start time before solving
    start = time.time()
    print(a_star_search(randomTest1[0], randomTest1[1], randomTest1[2]))
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
