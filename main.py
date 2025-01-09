from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from genetics import Evaluator

def main(filename: str = 'lagerstatus.csv', vocal: bool = True) -> None:
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
    #         population_size = 100,
    #         repetition_limit = 500,
    #         minimum_growth = 0.1,
    #         vocal = vocal
    #     )
    # evaluator.population.append(evaluator._random_genome()) # TODO: REMOVE
    from collections import defaultdict
    first_positive = defaultdict(int)
    for iteration in range(1000):
        if iteration % 50 == 0:
            print(iteration)
        first_positive[evaluator.evaluate(
            population_size = 100,
            repetition_limit = 500,
            minimum_growth = 0.1,
            vocal = vocal
        )] += 1
    
    vocal = False
    first_positives = [(key, value) for key, value in first_positive.items()]
    for key, value in sorted(first_positives, key=lambda x:x[0]):
        print(f'Gen {key}: {value}')
        

    statistics = [
        {'name': 'weights', 'data': data_array[:, 1]},
        {'name': 'earnings', 'data': data_array[:, 2]}
    ]

    _, ax = plt.subplots(1, 2)
    ax: list[Axes]
    for index, stat in enumerate(statistics):
        mean = np.nanmean(stat['data'])
        std = np.std(stat['data'])
        var = np.var(stat['data'])
        ax[index].hist(stat['data'])
        ax[index].set_title(stat['name'].capitalize())
        ax[index].axvline(x=mean, color='k', label=f'Mean')
        ax[index].axvline(x=mean-std, color='k', linestyle='dotted', label=f'Standard deviation')
        ax[index].axvline(x=mean+std, color='k', linestyle='dotted')
        ax[index].plot([], [], ' ', label=f'Variance: {var:.2f}')
        ax[index].legend(loc='upper left')
    
    if vocal:
        best_load = evaluator.population[0]
        load_array = np.array(best_load).reshape(len(best_load), -1)
        merged_array = np.hstack((evaluator.data, load_array))

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
    
    # plt.show()


if __name__ == '__main__':
    main()