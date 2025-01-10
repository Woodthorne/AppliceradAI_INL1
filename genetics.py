import random
from datetime import datetime
from functools import cache
from pathlib import Path
from statistics import mean

import numpy as np

TRUCK_CAPACITY = 800


class Evaluator:
    def __init__(self, data_array: np.ndarray,
                 n_positions: int = 10, position_capacity: int = 800) -> None:
        '''Class handling a genetic algorithm for finding the optimal
        distribution of a set of packages 

        Parameters
        ----------
        data_array: numpy.ndarray
            Numpy array containing package information with columns _, weight, earnings, deadline.
        n_positions: int, default: 10
            Number of trucks to pack into.
        position_capacity: int, default: 100
            Maximum weight allowed per truck.
        file_path: Path
            Path-object pointing to file to be read.
        '''

        self.data = data_array
        self.n_positions = n_positions
        self.position_capacity = position_capacity

        self._total_weight = sum(self.data[:,1])
        self._total_capacity = n_positions * position_capacity

        self.population: list[tuple[int]] = []
        self.best_fitness_scores: list[float] = []
    
    def evaluate(
            self,
            population_size: int = 100,
            repetition_limit: int = 1000,
            minimum_growth: float = 0.01,
            max_minutes: int = 60,
            vocal: bool = True
    ) -> None:
        '''Attempts to find the best distribution of packages.

        Parameters
        ----------
        population_size: int, default: 100
            Number of genomes per generation
        repetition_limit: int, default: 1000
            Number of repeated best fitness before the method
            self-terminates.
        minimum_growth: float, default: 0.01
            Minimum increase in fitness per generation spent for the
            method to continue after increase in best fitness.
        max_minutes: int, default: 60
            Upper time limit in minutes before the method
            self-terminates
        '''
        
        generation = 0
        self.population = [self._random_genome()
                           for _ in range(population_size)]
        
        self.best_fitness_scores = []
        best_fitness = self._score_fitness(self.population[0])
        repeated_scores = 0

        stability = 1
        
        time_start = datetime.now()
        cycle_times: list[float] = []
        while repeated_scores < repetition_limit:
            cycle_start = datetime.now()
            generation += 1

            self.population.sort(key = self._score_fitness, reverse=True)

            legacy_size = len(self.population) // 10
            new_population = self.population[:legacy_size]

            random_size = len(self.population) // 10
            new_population.extend([self._random_genome() for _ in range(random_size)])

            donor_size = len(self.population) // 2
            stability = 1 - repeated_scores / repetition_limit
            # stability = max(stability - decay_rate, decay_rate)
            while len(new_population) < len(self.population):
                donors = random.sample(self.population[:donor_size], 2)
                # donors = (random.choice(self.population[:legacy_size // 2]),
                #           random.choice(self.population[legacy_size:donor_size]))
                new_genome = self._combine_donors(donors, stability)
                new_population.append(new_genome)
            
            self.population = new_population

            new_fitness = round(self._score_fitness(self.population[0]), 2)
            self.best_fitness_scores.append(new_fitness)
            if best_fitness < new_fitness:
                growth = new_fitness - best_fitness
                if repeated_scores != 0 \
                and growth / repeated_scores < minimum_growth:
                    if vocal:
                        print('INTERRUPTED: Slow growth.')
                    break
                best_fitness = new_fitness
                stability = 1
                repeated_scores = 0
            else:
                repeated_scores += 1
            
            cycle_times.append((datetime.now() - cycle_start).total_seconds())
            next_cycle_estimate = ((datetime.now() - time_start).total_seconds()
                                   + mean(cycle_times)) / 60
            if next_cycle_estimate > max_minutes:
                if vocal:
                    if vocal:
                        print('INTERRUPTED: Time limit reached.')
                break
            
            if generation % (repetition_limit // 20) == 0 and vocal:
                message = f'Generation: {generation}, '
                message += f'Best Score: {best_fitness}, '
                message += f'Stability: {stability:.2f}'
                print(message)
        
        message = 'Final result: '
        message += f'Generation: {generation}, '
        message += f'Best Score: {self._score_fitness(self.population[0])}'
        print(message)
    
    def save_results_to_file(self) -> None:
        '''Saves best result in population to /deliveries/'''

        if len(self.population) == 0:
            return
        
        best_genome = self.population[0]
        load_array = np.array(best_genome).reshape(len(best_genome), -1)
        merged_array = np.hstack((self.data, load_array))
        delivery_folder = Path('deliveries/')
        if not delivery_folder.exists():
            delivery_folder.mkdir()

        for position in range(1, self.n_positions + 1):
            mask = (merged_array[:, 4] == position)
            package_ids = [int(package_id) for package_id in merged_array[mask, 0]]
            
            distribution_path = delivery_folder / f'delivery_{position}.txt'
            with distribution_path.open('w') as f:
                for package_id in package_ids:
                    f.write(f'{package_id}\n')
    
    def _random_genome(self) -> tuple[int]:
        '''Generates genome
        
        Returns
        -------
        tuple[int]
        '''
        
        genome = [self._random_gene() for _ in range(len(self.data))]
        return tuple(genome)
    
    def _random_gene(self) -> int:
        '''Generates random gene
        
        Returns
        -------
        int
        '''
        
        probability = random.random()
        if probability < self._total_capacity / self._total_weight:
            return random.randint(1, self.n_positions)
        return 0

    def _combine_donors(
            self,
            donors: tuple[tuple[int], tuple[int]],
            stability: float = 1
    ) -> tuple[int]:
        '''Combines genes of two donors
        
        Parameters
        ----------
        donors: tuple[tuple[int], tuple[int]]
            Tuple of genomes to combine.
        stability: float, default: 1
            Probability of individual gene not mutating.
        '''

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
    
    @cache
    def _score_fitness(self, genome: tuple[int]) -> int:
        '''Evaluates the fitness of a genome.
        
        Parameters
        ----------
        genome: tuple[int]
            Genome to be evauluated
        
        Returns
        -------
        int
        '''
        load_array = np.array(genome).reshape(len(genome), -1)
        merged_array = np.hstack((self.data, load_array))

        score = 0
        for position in range(1, self.n_positions + 1):
            position_mask = (merged_array[:, 4] == position)
            overload = sum(merged_array[position_mask, 1]) - self.position_capacity
            if overload > 0:
                return 0
        
        loaded_mask = (merged_array[:, 4] != 0)
        overdue_mask = (merged_array[:, 3] < 0)

        score += sum(merged_array[loaded_mask, 2])
        score += sum(deadline ** 2 for deadline
                     in merged_array[loaded_mask & overdue_mask, 3])
        
        return int(score)
