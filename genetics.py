import random
from pathlib import Path
from collections import defaultdict

import numpy as np

TRUCK_CAPACITY = 800

class Evaluator:
    def __init__(self, source: Path, n_trucks: int = 10, population_size: int = 100) -> None:
        file_data = np.genfromtxt(
            fname = source,
            delimiter = ',',
            names = ['package_id', 'weight', 'profit', 'deadline'],
            skip_header = 1
        )
        self.data = np.array(file_data.tolist())
        self.n_trucks = n_trucks
        self.loads = [self._random_load() for _ in range(population_size)]
    
    def evaluate(self, generation_limit: int = 5000, vocal: bool = True) -> list[int]:
        current_fitness_score = 0
        generations_since_change = 0
        generation = 1

        while True:
            if generations_since_change > generation_limit:
                break

            generation += 1

            self.loads.sort(key = self._score_load, reverse=True)

            survivor_size = len(self.loads) // 10
            new_loads = self.loads[:survivor_size]

            parent_size = len(self.loads) // 2
            while len(new_loads) < len(self.loads):
                load_1 = random.choice(self.loads[:parent_size])
                load_2 = random.choice(self.loads[:parent_size])
                new_load = self._merge_loads(load_1, load_2)
                new_loads.append(new_load)
            
            self.loads = new_loads

            if current_fitness_score < self._score_load(self.loads[0]):
                current_fitness_score = self._score_load(self.loads[0])
                generations_since_change = 0
            else:
                generations_since_change += 1
            
            if generation % (generation_limit // 20) == 0 and vocal:
                message = f'Generation: {generation}, '
                message += f'Best Score: {self._score_load(self.loads[0])}'
                print(message)
        
        message = 'Final result: '
        message += f'Generation: {generation}, '
        message += f'Best Score: {self._score_load(self.loads[0])}'
        print(message)


    def _random_load(self) -> list[int]:
        load = [self._random_placement() for _ in range(len(self.data))]
        return load
        # if self._verify_load(load):
        #     return load
        # return self._random_load()
    
    def _random_placement(self) -> int:
        probability = random.random()
        if probability < 0.4:
            return random.randint(1, self.n_trucks)
        return 0

    def _verify_load(self, load: list[int]) -> bool:
        load_array = np.array(load).reshape(len(load), -1)
        merged_array = np.hstack((self.data, load_array))
        for truck_id in range(1, self.n_trucks + 1):
            mask = (merged_array[:, 4] == truck_id)
            weight = sum(merged_array[mask, 1])
            if weight > TRUCK_CAPACITY:
                return False
        return True
    
    def _score_load(self, load: list[int]) -> int:
        load_array = np.array(load).reshape(len(load), -1)
        merged_array = np.hstack((self.data, load_array))

        loaded_mask = (merged_array[:, 4] != 0)
        remaining_mask = (merged_array[:, 4] == 0)
        overdue_mask = (merged_array[:, 3] < 0)

        loaded_profit = sum(merged_array[loaded_mask, 2]) \
            - sum([val ** 2 for val
                   in merged_array[loaded_mask & overdue_mask, 3]])
        
        remaining_penalty = sum(
            [val ** 2 for val
             in merged_array[remaining_mask & overdue_mask, 3]])
        
        remaining_packages = len(merged_array[remaining_mask])

        remaining_profit = sum(merged_array[remaining_mask, 2])

        score = sum([loaded_profit, -remaining_penalty])
        if not self._verify_load(load):
            score *= 0.01
        
        return score

    def _merge_loads(self, parent_1: list[int], parent_2: list[int]) -> list[int]:
        new_load = []
        for package_1, package_2 in zip(parent_1, parent_2):
            probability = random.random()
            if probability < 0.45:
                new_load.append(package_1)
            elif probability < 0.9:
                new_load.append(package_2)
            else:
                new_load.append(self._random_placement())
        return new_load
        # if self._verify_load(new_load):
        #     return new_load
        # return self._merge_loads(parent_1, parent_2)


if __name__ == '__main__':
    evaluator = Evaluator(Path('lagerstatus.csv'))
    evaluator.evaluate()