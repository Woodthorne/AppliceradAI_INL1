from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from genetics import Evaluator

def main(filename: str = 'lagerstatus.csv') -> None:
    N_TRUCKS = 10
    TRUCK_CAPACITY = 800

    data_path = Path(filename)
    data_array = np.genfromtxt(
        fname = data_path,
        delimiter = ',',
        skip_header = 1
    )

    evaluator = Evaluator(
        data_array = data_array,
        n_positions = N_TRUCKS,
        position_capacity = TRUCK_CAPACITY
    )
    # evaluator.evaluate(
    #     population_size = 100,
    #     repetition_limit = 500,
    #     minimum_growth = 0.1,
    #     vocal = True
    # )

    # best_load = evaluator.population[0]
    best_load = evaluator._random_genome() # TODO: REMOVE
    print(f'Fitness: {evaluator._score_fitness(best_load)}')
    load_array = np.array(best_load).reshape(len(best_load), -1)
    merged_array = np.hstack((evaluator.data, load_array))
    
    positions = [num for num in range(N_TRUCKS + 1)]
    total_weights = np.array([sum(merged_array[merged_array[:, 4] == position, 1])
                              for position in positions])
    total_earnings = np.array([sum(merged_array[merged_array[:, 4] == position, 2])
                               for position in positions])
    
    xbins = np.array(positions)
    
    # n, bins = np.histogram(total_weights)
    fig, ax = plt.subplots()
    ax.hist(total_weights)
    ax.hist(total_earnings)
    plt.show()



    # histogram
    # average
    # variance
    # standard deviation

    plt.show()

    ############################

    loaded_mask = (merged_array[:, 4] != 0)
    remaining_mask = (merged_array[:, 4] == 0)
    overdue_mask = (merged_array[:, 3] < 0)

    total_packages = 0
    for truck_id in range(1, evaluator.n_positions + 1):
        truck_mask = (merged_array[:, 4] == truck_id)
        truck_packages = merged_array[truck_mask, 1]
        truck_weight = sum(truck_packages)
        total_packages += len(truck_packages)

        message = f'Truck #{truck_id}: '
        message += f'{truck_weight:.2f}/{TRUCK_CAPACITY} kgs loaded, '
        message += f'{len(truck_packages)} packages.'
        print(message)
    
    remaining_overdue = len(merged_array[overdue_mask & remaining_mask])
    daily_earnings = sum(merged_array[loaded_mask, 2])
        
    print(f'{remaining_overdue} overdue packages remaining.')
    print(f'{daily_earnings:.2f} daily earnings.')
    print(f'{total_packages} packages loaded.')


if __name__ == '__main__':
    main()