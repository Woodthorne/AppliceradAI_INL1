import random
from functools import cache

import numpy as np

TRUCK_CAPACITY = 800


class Evaluator:
    def __init__(self, data_array: np.ndarray, n_positions: int = 10, position_capacity: int = 800) -> None:
        self.data = data_array
        self._total_weight = sum(self.data[:,1])
        self._total_capacity = n_positions * position_capacity
        self.n_positions = n_positions
        self.population: list[tuple[int]] = []
    
    def evaluate(
            self, population_size: int = 100,
            repetition_limit: int = 5000,
            minimum_growth: float = 0.01,
            vocal: bool = True
    ) -> list[int]:
        
        self.population = [self._random_genome()
                           for _ in range(population_size)]
        generation = 1
        best_fitness = self._score_fitness(self.population[0])
        repeated_scores = 0

        while repeated_scores < repetition_limit:
            generation += 1

            self.population.sort(key = self._score_fitness, reverse=True)

            legacy_size = len(self.population) // 10
            new_population = self.population[:legacy_size]

            random_size = len(self.population) // 10
            new_population.extend([self._random_genome() for _ in range(random_size)])

            donor_size = len(self.population) // 2
            stability = 1 - repeated_scores / repetition_limit
            while len(new_population) < len(self.population):
                donors = random.sample(self.population[:donor_size], 2)
                new_genome = self._combine_donors(donors, stability)
                new_population.append(new_genome)
            
            self.population = new_population

            new_fitness = self._score_fitness(self.population[0])
            if new_fitness > 0:
                return generation
            if best_fitness < new_fitness:
                if repeated_scores != 0 and (new_fitness - best_fitness) / repeated_scores < minimum_growth:
                    break
                best_fitness = new_fitness
                repeated_scores = 0
            else:
                repeated_scores += 1
            
            if generation % (repetition_limit // 20) == 0 and vocal:
                message = f'Generation: {generation}, '
                message += f'Best Score: {best_fitness}, '
                message += f'Stability: {stability:.2f}'
                print(message)
        
        message = 'Final result: '
        message += f'Generation: {generation}, '
        message += f'Best Score: {self._score_fitness(self.population[0])}'
        print(message)

    def _combine_donors(self, donors: tuple[tuple[int], tuple[int]], stability: float = 1) -> tuple[int]:
        new_genome = []
        for gene_1, gene_2 in zip(*donors):
            probability = random.random()
            if probability < stability / 2:
                new_genome.append(gene_1)
            elif probability < stability:
                new_genome.append(gene_2)
            else:
                new_genome.append(self._random_gene())
        return tuple(new_genome)
    
    def _random_genome(self) -> tuple[int]:
        genome = [self._random_gene() for _ in range(len(self.data))]
        return tuple(genome)
    
    def _random_gene(self) -> int:
        probability = random.random()
        # if probability < 0.1:
        if probability < self._total_capacity / self._total_weight:
            return random.randint(1, self.n_positions)
        return 0

    @cache
    def _score_fitness(self, genome: tuple[int]) -> int:
        load_array = np.array(genome).reshape(len(genome), -1)
        merged_array = np.hstack((self.data, load_array))

        loaded_mask = (merged_array[:, 4] != 0)
        # remaining_mask = (merged_array[:, 4] == 0)
        overdue_mask = (merged_array[:, 3] < 0)

        # loaded_packages = merged_array[loaded_mask]
        # remaining_packages = merged_array[remaining_mask]

        score = sum([
            sum(merged_array[loaded_mask, 2]),                      # column "Förtjänst"
            sum(deadline ** 2 for deadline                          # column "Deadline" squared
                in merged_array[loaded_mask & overdue_mask, 3]),    #   if < 0
        ])

            # -sum(deadline ** 2 for deadline 
            #      in merged_array[remaining_mask & overdue_mask, 3])

        # loaded_profit = sum(merged_array[loaded_mask, 2]) \
        #     - sum([val ** 2 for val
        #            in merged_array[loaded_mask & overdue_mask, 3]])
        
        # remaining_penalty = sum(
        #     [val ** 2 for val
        #      in merged_array[remaining_mask & overdue_mask, 3]])
        
        # remaining_packages = len(merged_array[remaining_mask])

        # remaining_profit = sum(merged_array[remaining_mask, 2])

        # score = sum([loaded_profit, -remaining_penalty])
        if not self._verify_genome(genome):
            score = -abs(score * 10_000)
        
        return score

    @cache
    def _verify_genome(self, genome: tuple[int]) -> bool:
        load_array = np.array(genome).reshape(len(genome), -1)
        merged_array = np.hstack((self.data, load_array))
        for truck_id in range(1, self.n_positions + 1):
            mask = (merged_array[:, 4] == truck_id)
            weight = sum(merged_array[mask, 1])
            if weight > TRUCK_CAPACITY:
                return False
        return True
