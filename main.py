from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from genetics import Evaluator


def main(filename: str = 'lagerstatus.csv',
         vocal: bool = True, plot: bool = True) -> None:
    N_TRUCKS = 10
    TRUCK_CAPACITY = 800
    POPULATION_SIZE = 100
    REPETITION_LIMIT = 500
    MINIMUM_GROWTH = 0.1
    MAX_MINUTES = 60

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
    evaluator.evaluate(
            population_size = POPULATION_SIZE,
            repetition_limit = REPETITION_LIMIT,
            minimum_growth = MINIMUM_GROWTH,
            vocal = vocal,
            max_minutes= MAX_MINUTES
        )
        
    result = evaluator.population[0]
    
    delivery_mask = [position != 0 for position in result]
    warehouse_mask = [position == 0 for position in result]
    overdue_mask = (data_array[:, 3] < 0)
    
    if vocal:
        print('==================================================')
        delivery_packages = 0
        for truck_id in range(1, evaluator.n_positions + 1):
            truck_mask = [position == truck_id for position in result]
            truck_packages = len(data_array[truck_mask])
            truck_weight = sum(data_array[truck_mask, 1])
            delivery_packages += truck_packages

            message = f'Truck #{truck_id}: '
            message += f'{truck_weight:.2f}/{TRUCK_CAPACITY} loaded weight, '
            message += f'{truck_packages} packages.'
            print(message)
        print('==================================================')
    
    delivery_earnings = sum(data_array[delivery_mask, 2])
    warehouse_penalty = sum(deadline ** 2 for deadline in
                            data_array[overdue_mask & warehouse_mask, 3]
                            if deadline < 0)
    warehouse_packages = len(data_array[warehouse_mask])
    warehouse_earnings = sum(data_array[warehouse_mask, 2])
                
    print(f'Earnings in delivery: {delivery_earnings:.2f}')
    print(f'Penalty in warehouse: {warehouse_penalty:.2f}')
    print(f'Packages in warehouse: {warehouse_packages:.2f}')
    print(f'Earnings in warehouse: {warehouse_earnings:.2f}')
    
    if plot:
        statistics = [
            {'name': 'Weights', 'data': data_array[:, 1]},
            {'name': 'Earnings', 'data': data_array[:, 2]}
        ]

        _, ax = plt.subplots(1, 2)
        ax: list[Axes]
        for index, stat in enumerate(statistics):
            mean = np.nanmean(stat['data'])
            std = np.std(stat['data'])
            var = np.var(stat['data'])
            ax[index].hist(stat['data'])
            ax[index].set_title(stat['name'])
            ax[index].axvline(x=mean, color='k', label=f'Mean: {mean:.2f}')
            ax[index].axvline(x=mean-std, color='k', linestyle='dotted', label=f'Standard deviation: {std:.2f}')
            ax[index].axvline(x=mean+std, color='k', linestyle='dotted')
            ax[index].plot([], [], ' ', label=f'Variance: {var:.2f}')
            ax[index].legend(loc='upper left')
        plt.show()


if __name__ == '__main__':
    filename = 'lagerstatus.csv'
    main(filename)