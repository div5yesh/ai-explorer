"""
CMSC 671 Fall 2018 – Project - AI-Explorer
Team Name: Agent Rogue
Team Members: Anushree Desai, Hakju Oh, Shree Hari, Divyesh Chitroda
Libraries: GameDriver - https://github.com/erfannoury/cmsc671-fall2018 - 0.0.5

Test Command: 
python play.py --height 10 --width 10  --num-powerups 2 --num-monsters 1  --initial-strength 100 --save-dir map1/ --show-map --map-type=emoji --verbose
"""
import sys
from heapq import *

from agent import BaseAgent
from utils import Directions, MapTiles


class State:

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], tuple):
                self._state = args[0]
            elif isinstance(args[0], State):
                self._state = (args[0].x, args[0].y)

        elif len(args) == 2:
            self._state = (int(args[0]), int(args[1]))

        else:
            raise ValueError

    @property
    def x(self):
        return self._state[0]

    @property
    def y(self):
        return self._state[1]

    def move(self, direction):
        if direction == Directions.NORTH:
            return State(self.x - 1, self.y)

        if direction == Directions.EAST:
            return State(self.x, self.y + 1)

        if direction == Directions.WEST:
            return State(self.x, self.y - 1)

        if direction == Directions.SOUTH:
            return State(self.x + 1, self.y)

    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def neighbours(self, map_size):
        """
        Return N,E,W,S neighbours one at a time on each iteration.

        :param map_size:
        :return:
        """

        if self.x > 0:
            yield State(self.x - 1, self.y)
        else:
            yield None

        if self.y < map_size:
            yield State(self.x, self.y + 1)
        else:
            yield None

        if self.x < map_size:
            yield State(self.x + 1, self.y)
        else:
            yield None

        if self.y > 0:
            yield State(self.x, self.y - 1)
        else:
            yield None

    def __eq__(self, other):
        if other:
            if self.x == other.x and self.y == other.y:
                return True
        return False

    def __getitem__(self, item):
        return self._state[item]

    def __hash__(self):
        return self._state.__hash__()

    def __str__(self):
        return str(self._state)


class Node:
    """
    Node object for bookkeeping of the current state, parent node for backtracking,
    action performed to generate the node, actual cost and estimated cost.
    """

    def __init__(self, estimateCost, actualCost, state, parent, action):
        """
        Constructor
        """

        self.estimateCost = estimateCost
        self.actualCost = actualCost
        self.state = State(state)
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
        return False

    def __lt__(self, other):
        """
        Less than operator overload to compare estimated costs for heapify
        comparisons in heapq, using the priority as estimated cost.
        """

        return self.estimateCost < other.estimateCost

    def __str__(self):
        return str(self.state)


class AgentRogue(BaseAgent):
    """
    Agent Rogue extends BaseAgent and implements step function.
    """

    backtrack = False
    explored = set()
    backtrackNodes = []
    frontier = []
    tileCost = {MapTiles.P: 1, MapTiles.S: 3, MapTiles.M: 10, MapTiles.W: 100, MapTiles.U: -30}
    backTrackTileCost = {MapTiles.P: 1, MapTiles.S: 3, MapTiles.M: 10, MapTiles.W: 100, MapTiles.U: sys.maxsize}

    def __init__(self, height, width, initial_strength, name='agent_rogue'):
        super().__init__(height=height, width=width, initial_strength=initial_strength, name=name)

    def evaluateHeuristic(self, problem, state):
        value = self.tileCost[problem[state.x][state.y]]
        for neighbour in state.neighbours(len(problem) - 1):
            if neighbour is None:
                value += self.tileCost[MapTiles.W]
            else:
                value += self.tileCost[problem[neighbour.x][neighbour.y]]

        return value

    def applyAction(self, state, action):
        """
        Generate next state by performing the action on the state.
        Args:
            state: tuple - (x,y). State of the agent.
            action: character - 'N'. Action to perform.
        Returns: tuple -> (x,y). Next state of the agent.
        """
        return state.move(action)

    def generateChild(self, problem, node, action):
        """
        Generate the child node by performing the legal action on the current state
        and calculating the estimated cost to reach to the goal state and actual cost to
        reach to the current state from the start state.
        
        :param problem: 2D list of characters - [['m','p'],['s','p']]. Problem with terrain as characters.
        :param node: Object - Node. Node object representing current state.
        :param action: character - 'S'. Action to perform on the state. 
        :return: Object - Node. The Child node.
        """

        # get the next state
        state = self.applyAction(node.state, action)

        # calculate heuristic cost
        estimateCost = self.evaluateHeuristic(problem, state)
        return Node(estimateCost, 0, state, node, action)

    def findActions(self, problem, state):
        """
        Find all legal actions allowed on the state.
        
        :param problem: int. Size of the problem terrain. 
        :param state: tuple - (x,y). State of the agent on which to perform actions. 
        :return: [] -> list of actions.
        """

        size = len(problem) - 1
        legalActions = []
        if state.x > 0 and problem[state.x - 1][state.y] != MapTiles.W:
            legalActions.append(Directions.NORTH)
        if state.x < size and problem[state.x + 1][state.y] != MapTiles.W:
            legalActions.append(Directions.SOUTH)
        if state.y > 0 and problem[state.x][state.y - 1] != MapTiles.W:
            legalActions.append(Directions.WEST)
        if state.y < size and problem[state.x][state.y + 1] != MapTiles.W:
            legalActions.append(Directions.EAST)
        return legalActions

    def getDistance(self, current, other):
        """
        
        :param current: 
        :param other: 
        :return: 
        """

        return current.distance(other)

    def goalTest(self, node, goal):
        """
        Test whether the goal state has been reached, if not find a goal state
        in frontier that is satisfiable(<= 300 calories), but not optimal.

        :param node: Object - Node. The node to test for goal.
        :param goal: tuple(x,y). The goal state.
        :return: Object - Node. The goal node that is either satisfiable or optimal.
        """

        if node.state == goal:
            return node

    def getExploredStates(self, node):
        """
        Print the solution path by backtracking to the root node
        following through all the parent nodes.

        :param node: Object - Node. The node containing goal state at the end of the search.
        :return: string. String of actions performed on root node to reach the goal node.
        """

        nodes = []
        while node.parent:
            nodes.insert(0, node)
            node = node.parent

        return nodes

    def generateBacktrackNode(self, problem, goal, node, action):
        """
        
        :param problem: 
        :param goal: 
        :param node: 
        :param action: 
        :return: 
        """

        state = self.applyAction(node.state, action)
        nodeCost = node.estimateCost + self.backTrackTileCost[problem[state.x][state.y]]
        return Node(nodeCost, 0, state, node, action)

    def backtrackSearch(self, start, goal, problem):
        """
        Uniform-cost search for finding the best from current node
        to the best node
        
        :param start: 
        :param goal: 
        :param problem: 
        :return: 
        """

        explored = set()
        frontier = []
        node = Node(0, 0, start.state, None, None)
        heappush(frontier, node)
        while (True):
            if len(frontier) == 0:
                return []

            node = heappop(frontier)
            if self.goalTest(node, goal.state):
                return (self.getExploredStates(node), node.estimateCost)

            explored.add(node.state)
            Actions = self.findActions(problem, node.state)
            for action in Actions:
                neighbour = self.generateBacktrackNode(problem, goal, node, action)
                if neighbour != None:
                    if neighbour not in frontier and neighbour.state not in explored:
                        heappush(frontier, neighbour)

    def solve(self, current, strength, problem):
        """
        
        :param current: 
        :param strength: 
        :param problem: 
        :return: 
        """
        if self.backtrack:
            if len(self.backtrackNodes):
                bNode = self.backtrackNodes.pop()
                return bNode.action
            else:
                self.backtrack = False

        node = Node(0, 0, current, None, None)
        self.explored.add(node.state)

        # get the list of all possible actions on the state
        Actions = self.findActions(problem, node.state)
        for action in Actions:
            # generate a child node by applying actions to the current state
            neighbour = self.generateChild(problem, node, action)
            # check if child is already explored or present in beam
            if neighbour not in self.frontier and neighbour.state not in self.explored:
                # add node to frontier only if it can contain within best k nodes
                heappush(self.frontier, neighbour)

        current = node

        while len(self.frontier) != 0:
            node = heappop(self.frontier)
            if self.getDistance(current.state, node.state) > 1:
                nodeTuple = self.backtrackSearch(current, node, problem)
                self.backtrackNodes = nodeTuple[0]
                if len(self.backtrackNodes):
                    bNode = self.backtrackNodes.pop()
                    if (strength > nodeTuple[1]):
                        self.backtrack = True
                        return bNode.action
            else:
                return node.action

    def step(self, location, strength, game_map, map_objects):
        """
        
        :param location: 
        :param strength: 
        :param game_map: 
        :param map_objects: 
        :return: 
        """

        action = self.solve(location, strength, game_map)
        return action
