import random
from functools import cache, lru_cache
from pathlib import Path

import numpy as np

TRUCK_CAPACITY = 800


class Evaluator:
    def __init__(self, source: Path, n_trucks: int = 10) -> None:
        file_data = np.genfromtxt(
            fname = source,
            delimiter = ',',
            names = ['package_id', 'weight', 'profit', 'deadline'],
            skip_header = 1
        )
        self.data = np.array(file_data.tolist())
        self._total_weight = sum(self.data[:,1])
        self._total_capacity = TRUCK_CAPACITY * n_trucks
        self.n_trucks = n_trucks
        self.loads: list[tuple[int]] = []
    
    def evaluate(
            self, population_size: int = 100,
            repetition_limit: int = 5000,
            minimum_growth: float = 0.01,
            vocal: bool = True
    ) -> list[int]:
        
        self.loads = [self._random_load()
                      for _ in range(population_size)]
        generation = 1
        best_score = self._score_load(self.loads[0])
        repeated_scores = 0

        while True:
            if repeated_scores > repetition_limit:
                break

            generation += 1

            self.loads.sort(key = self._score_load, reverse=True)

            legacy_size = len(self.loads) // 10
            new_loads = self.loads[:legacy_size]

            random_size = len(self.loads) // 10
            new_loads.extend([self._random_load() for _ in range(random_size)])

            donor_size = len(self.loads) // 2
            while len(new_loads) < len(self.loads):
                load_1 = random.choice(self.loads[:donor_size])
                load_2 = random.choice(self.loads[:donor_size])
                new_load = self._merge_loads(load_1, load_2)
                new_loads.append(tuple(new_load))
            
            self.loads = new_loads

            new_score = self._score_load(self.loads[0])
            if best_score < new_score:
                if repeated_scores != 0 and (new_score - best_score) / repeated_scores < minimum_growth:
                    break
                best_score = new_score
                repeated_scores = 0
            else:
                repeated_scores += 1
            
            if generation % (repetition_limit // 20) == 0 and vocal:
                message = f'Generation: {generation}, '
                message += f'Best Score: {new_score}'
                print(message)
        
        message = 'Final result: '
        message += f'Generation: {generation}, '
        message += f'Best Score: {self._score_load(self.loads[0])}'
        print(message)

    def _random_load(self) -> tuple[int]:
        load = [self._random_placement() for _ in range(len(self.data))]
        return tuple(load)
    
    def _random_placement(self) -> int:
        probability = random.random()
        if probability < 0.1:
        # if probability < self._total_capacity / self._total_weight:
            return random.randint(1, self.n_trucks)
        return 0

    @cache
    def _verify_load(self, load: tuple[int]) -> bool:
        load_array = np.array(load).reshape(len(load), -1)
        merged_array = np.hstack((self.data, load_array))
        for truck_id in range(1, self.n_trucks + 1):
            mask = (merged_array[:, 4] == truck_id)
            weight = sum(merged_array[mask, 1])
            if weight > TRUCK_CAPACITY:
                return False
        return True
    
    @cache
    def _score_load(self, load: tuple[int]) -> int:
        load_array = np.array(load).reshape(len(load), -1)
        merged_array = np.hstack((self.data, load_array))

        loaded_mask = (merged_array[:, 4] != 0)
        remaining_mask = (merged_array[:, 4] == 0)
        overdue_mask = (merged_array[:, 3] < 0)

        # loaded_packages = merged_array[loaded_mask]
        # remaining_packages = merged_array[remaining_mask]

        score = sum([
            sum(merged_array[loaded_mask, 2]),
            sum(deadline ** 2 for deadline
                in merged_array[loaded_mask & overdue_mask, 3]),
            # -sum(deadline ** 2 for deadline 
            #      in merged_array[remaining_mask & overdue_mask, 3])
        ])

        # loaded_profit = sum(merged_array[loaded_mask, 2]) \
        #     - sum([val ** 2 for val
        #            in merged_array[loaded_mask & overdue_mask, 3]])
        
        # remaining_penalty = sum(
        #     [val ** 2 for val
        #      in merged_array[remaining_mask & overdue_mask, 3]])
        
        # remaining_packages = len(merged_array[remaining_mask])

        # remaining_profit = sum(merged_array[remaining_mask, 2])

        # score = sum([loaded_profit, -remaining_penalty])
        if not self._verify_load(load):
            score = -abs(score * 10_000)
        
        return score

    def _merge_loads(self, parent_1: tuple[int], parent_2: tuple[int]) -> tuple[int]:
        new_load = []
        for package_1, package_2 in zip(parent_1, parent_2):
            probability = random.random()
            if probability < 0.5:
                new_load.append(package_1)
            elif probability < 1:
                new_load.append(package_2)
            else:
                new_load.append(self._random_placement())
        return new_load


if __name__ == '__main__':
    evaluator = Evaluator(Path('lagerstatus4.csv'))
    evaluator.evaluate(repetition_limit=1000)

    best_five_loads = evaluator.loads[:5]
    best_load = evaluator.loads[0]

    load_array = np.array(best_load).reshape(len(best_load), -1)
    merged_array = np.hstack((evaluator.data, load_array))

    loaded_mask = (merged_array[:, 4] != 0)
    remaining_mask = (merged_array[:, 4] == 0)
    overdue_mask = (merged_array[:, 3] < 0)

    total_packages = 0
    for truck_id in range(1,  evaluator.n_trucks + 1):
        truck_mask = (merged_array[:, 4] == truck_id)
        truck_packages = merged_array[truck_mask, 1]
        truck_weight = sum(truck_packages)
        total_packages += len(truck_packages)

        message = f'Truck #{truck_id}: '
        message += f'{truck_weight:.2f}/{TRUCK_CAPACITY} kgs loaded, '
        message += f'{len(truck_packages)} packages.'
        print(message)
    
    remaining_overdue = len(merged_array[overdue_mask & remaining_mask])
    total_profit = sum(merged_array[loaded_mask, 2]) \
            # - sum([val ** 2 for val
            #        in merged_array[loaded_mask & overdue_mask, 3]])
        
    print(f'{remaining_overdue} overdue packages remaining.')
    print(f'{total_profit:.2f} total daily profit.')
    print(f'{total_packages} packages loaded.')