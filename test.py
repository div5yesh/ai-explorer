from driver import GameDriver
from knowledge_based_agent import KBAgentRogue

if __name__ == '__main__':
    height, width = 10, 10
    num_powerups = 2
    num_monsters = 1
    num_dynamic_monsters = 1
    initial_strength = 100
    map_type = 'ascii'
    save_dir = 'map1/'
    map_file = None
    show_map = False
    verbose = False

    results = []
    for _ in range(100):
        agent = KBAgentRogue(height, width, initial_strength)
        agents = [agent, ]

        game_driver = GameDriver(
            height=height, width=width,
            num_powerups=num_powerups,
            num_monsters=num_monsters,
            num_dynamic_monsters=num_dynamic_monsters,
            agents=agents,
            initial_strength=initial_strength,
            show_map=show_map, map_type=map_type,
            save_dir=save_dir, map_file=map_file)

        print('Starting game')
        try:
            game_driver.play(verbose=verbose)
        except StopIteration as e:
            if 'won' in e.value:
                results.append(True)
            else:
                results.append(False)

    won_count = sum([1 for x in results if x == True])
    die_count = sum([1 for x in results if x == False])

    print('Winning props: %.8f' % (won_count / float(won_count + die_count)))
