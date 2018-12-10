import os
import sys
from argparse import ArgumentParser

from agent import RandomAgent
from agent import HumanAgent
from driver import GameDriver
from agentrogue import AgentRogue
from kbagent import KBAgentRogue
from util_functions import MAP_TYPES


def main(args):
    parser = ArgumentParser(description='')

    parser.add_argument('--height', type=int, required=True,
                        help='Heigth of the map')
    parser.add_argument('--width', type=int, required=True,
                        help='Width of the map')
    parser.add_argument('--num-powerups', type=int, required=True,
                        help='Number of powerups to put in the game map')
    parser.add_argument('--num-monsters', type=int, required=True,
                        help='Number of monsters to put in the game map')
    parser.add_argument('--initial-strength', default=100, type=int,
                        help='Initial strength of each agent')
    parser.add_argument('--save-dir', type=str,
                        help='Save directory for saving the map')
    parser.add_argument('--map-file', type=str,
                        help='Path to the map JSON file')
    parser.add_argument('--play-against-human', action='store_true',
                        help='Whether to have a Human player as one of the '
                        'agents in the game')
    parser.add_argument('--show-map', action='store_true',
                        help='Whether to display the map in the terminal')
    parser.add_argument('--map-type', choices=MAP_TYPES, default='ascii',
                        help='Select map type. Choices are {' +
                        ', '.join(MAP_TYPES) + '}')
    parser.add_argument('--verbose', action='store_true',
                        help='Whether to be verbose when playing game')

    args = parser.parse_args(args)

    # TODO: Change how agents are populated
    agent = KBAgentRogue(args.height, args.width, args.initial_strength)

    agents = [agent]
    if args.play_against_human:
        human = HumanAgent(args.height, args.width, args.initial_strength)
        agents.append(human)

    results = []
    mapresults = []
    for i in range(1):
        game_driver = GameDriver(
            height=args.height, width=args.width,
            num_powerups=args.num_powerups,
            num_monsters=args.num_monsters,
            agents=agents,
            initial_strength=args.initial_strength,
            show_map=args.show_map, map_type=args.map_type,
            save_dir=args.save_dir, map_file=args.map_file)

        print('Starting game')
        result = game_driver.play(verbose=args.verbose)
        results.append(result[0])
        mapresult = agent.evaluateAgentExploration(result[1])
        mapresults.append(mapresult)
    
    won = sum([1 for x in results if x == True])
    lose = sum([1 for x in results if x == False])
    print('Rate:', (won / float(won + lose)))
    print("Max:", max(mapresults), "Min:", min(mapresults), "Median:", mapresults[len(mapresults)//2], "Avg:", sum(mapresults)/len(mapresults))


if __name__ == '__main__':
    main(sys.argv[1:])
