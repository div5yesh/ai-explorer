"""
CMSC 671 Fall 2018 – Project - AI-Explorer
Team Name: Agent Rogue
Team Members: Anushree Desai, Hakju Oh, Shree Hari, Divyesh Chitroda
"""
from agent import BaseAgent
from utils import Directions, MapTiles
import util_functions as uf
from heapq import *
import random
import time
import sys

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

class AgentRogue(BaseAgent):

    backtrack = False
    backtrackNodes = []
    tileCost = {MapTiles.P: 1, MapTiles.S: 3, MapTiles.M: 10, MapTiles.W: 100, MapTiles.U: -30}

    def __init__(self, height, width, initial_strength, name='agent_rogue'):
        super().__init__(height=height, width=width, initial_strength=initial_strength, name=name)
    
    def neighbours(self, state, size):
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

    def evaluateHeuristic(self, problem, state):
        value = self.tileCost[problem[state[0]][state[1]]]
        for neighbour in self.neighbours(state, len(problem) - 1):
            if neighbour == None:
                value += self.tileCost[MapTiles.W]
            else:
                value += self.tileCost[problem[neighbour[0]][neighbour[1]]]

        return value


    def applyAction(self, state, action):
        """
        Generate next state by performing the action on the state.
        Args:
            state: tuple - (x,y). State of the agent.
            action: character - 'N'. Action to perform.
        Returns: tuple -> (x,y). Next state of the agent.
        """
        if action == Directions.NORTH:
            return (state[0] - 1, state[1])

        if action == Directions.EAST:
            return (state[0], state[1] + 1)

        if action == Directions.WEST:
            return (state[0], state[1] - 1)

        if action == Directions.SOUTH:
            return (state[0] + 1, state[1])

    def generateChild(self, problem, node, action):
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
        state = self.applyAction(node.state, action)
        # calculate hueristic cost
        estimateCost = self.evaluateHeuristic(problem, state)
        return Node(estimateCost, 0, state, node, action)
    
    def findActions(self, problem, state):
        """
        Find all legal actions allowed on the state.
        Args:
            size: int. Size of the problem terrain.
            state: tuple - (x,y). State of the agent on which to perform actions.
        Returns: [] -> list of actions.
        """
        # print("problem.maptiles: ", MapTiles.W)
        # print("problem: ", problem[0][0])
        size = len(problem) - 1
        legalActions = []
        if state[0] > 0 and problem[state[0] - 1][state[1]] != MapTiles.W:
            legalActions.append(Directions.NORTH)
        if state[0] < size and problem[state[0] + 1][state[1]] != MapTiles.W:
            legalActions.append(Directions.SOUTH)
        if state[1] > 0 and problem[state[0]][state[1] - 1] != MapTiles.W:
            legalActions.append(Directions.WEST)
        if state[1] < size and problem[state[0]][state[1] + 1] != MapTiles.W:
            legalActions.append(Directions.EAST)
        return legalActions
    
    def getDistance(self, current, other):
        return (abs(current[0] - other[0]) + abs(current[1] - other[1]))

    def goalTest(self, node, goal):
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

    def getExploredStates(self, node):
        """
        Print the solution path by backtracking to the root node
        following throught all the parent nodes.
        Args:
            node: Object - Node. The node containing goal state at the end of the search.
        Returns: string. String of actions performed on root node
        to reach the goal node.
        """
        nodes = []
        while node.parent:
            nodes.insert(0, node)
            node = node.parent

        return nodes

    def generateBacktrackNode(self, problem, goal, node, action):
        state = self.applyAction(node.state, action)
        estimateCost = node.actualCost + self.tileCost[problem[state[0]][state[1]]]
        return Node(estimateCost, 0, state, node, action)

    def backtrackSearch(self, start, goal, problem):

        explored = set()
        frontier = []
        node = Node(0, 0, start.state, None, None)
        heappush(frontier, node)
        while (True):
            if len(frontier) == 0:
                return []

            node = heappop(frontier)
            if self.goalTest(node, goal.state):
                return self.getExploredStates(node)

            explored.add(node.state)
            Actions = self.findActions(problem, node.state)
            for action in Actions:
                neighbour = self.generateBacktrackNode(problem, goal, node, action)
                if neighbour != None:
                    if neighbour not in frontier and neighbour.state not in explored:
                        heappush(frontier, neighbour)

    def solve(self, start, strength, problem):
        explored = set()
        frontier = []

        if self.backtrack:
            if len(self.backtrackNodes):
                bNode = self.backtrackNodes.pop()
                return bNode.action
            else:
                self.backtrack = False

        node = Node(0, 0, start, None, None)
        explored.add(node.state)

        # get the list of all possible actions on the state
        Actions = self.findActions(problem, node.state)
        for action in Actions:
            # generate a child node by applying actions to the current state
            neighbour = self.generateChild(problem, node, action)
            # check if child is already explored or present in beam
            if neighbour not in frontier and neighbour.state not in explored:
                #add node to frontier only if it can contain within best k nodes
                heappush(frontier, neighbour)

        current = node
        for i in frontier:
            print(i.state, i.estimateCost)
        node = heappop(frontier)

        if self.getDistance(current.state, node.state) > 1:
            self.backtrack = True
            self.backtrackNodes = self.backtrackSearch(current, node, problem)
            if len(self.backtrackNodes):
                bNode = self.backtrackNodes.pop()
                return bNode.action
        print(node.estimateCost)
        return node.action

    def step(self, location, strength, game_map, map_objects):
        uf.print_map(game_map, 'e')
        action = self.solve(location, strength, game_map)
        input()
        print("Action::",action)
        return action
