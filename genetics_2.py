import csv
import random
from functools import cache
from pathlib import Path
from typing import Any, Generator

# import numpy as np


class GeneticEvaluator:
    def __init__(self, source: Path, n_positions: int = 10, capacity: int = 800):
        self._source = source
        self._n_positions = n_positions
        self._capacity = capacity

        self._positions = [n + 1 for n in range(n_positions)]
        self._genome_size = sum(1 for _ in self._read_data())

        self.population: list[tuple[int]] = []
    
    def evaluate(
            self, population_size: int = 100,
            repetition_limit: int = 1000, improvement_req: bool = 0.01,
            vocal: bool = True) -> list[int]:
        
        best_fitness = None
        repeated_results = 0

        self.population = [self._random_genome()
                           for _ in range(population_size)]
        generation = 1
        
        while True:
            if repeated_results > repetition_limit:
                break
            
            generation += 1

            self.population.sort(key = self._score_fitness, reverse = True)

            legacy_size = population_size // 10
            new_population = self.population[:legacy_size]

            random_size = population_size // 10
            new_population.extend(self._random_genome() for _ in range(random_size))

            donor_size = population_size // 2
            while len(new_population) < population_size:
                donors = random.sample(self.population[:donor_size], 2)
                new_genome = self._merge_donors(donors)
                new_population.append(new_genome)
            
            self.population = new_population

            if not best_fitness or best_fitness < self._score_fitness(self.population[0]):
                best_fitness = self._score_fitness(self.population[0])
                repeated_results = 0
            else:
                repeated_results += 1
            
            if generation % (repetition_limit // 20) == 0 and vocal:
                message = f'Generation: {generation}, '
                message += f'Best Fitness: {best_fitness}'
                print(message)

    def print_summary(self) -> None:
        best_genome = self.population[0]
        total_assigned_count = 0
        total_profit = 0
        for position in self._positions:
            assigned_indeces = [index for index, gene
                                in enumerate(best_genome)
                                if gene == position]
            assigned_packages = self._filter_data(assigned_indeces)

            local_count = 0
            local_weight = 0
            for package in assigned_packages:
                local_count += 1
                total_assigned_count += 1
                local_weight += float(package['Vikt'])
                total_profit += float(package['Förtjänst'])
                if float(package['Deadline']) < 0:
                    total_profit -= float(package['Deadline']) ** 2
            

            message = f'Truck #{position}: '
            message += f'{local_weight}/{self._capacity} kgs loaded, '
            message += f'{local_count} packages.'
        
        unassigned_indeces = [index for index, gene
                              in enumerate(best_genome)
                              if gene == 0]
        
        unassigned_overdue_count = 0
        for package in self._filter_data(unassigned_indeces):
            if float(package['Deadline']) < 0:
                total_profit -= float(package['Deadline']) ** 2
                unassigned_overdue_count += 1
        
        print(f'{unassigned_overdue_count} overdue packages remaining.')
        print(f'{total_profit:2} total daily profit.')
        print(f'{total_assigned_count} packages loaded.')

    def _read_data(self):
        with self._source.open('r', encoding='utf-8') as file:
            dict_reader = csv.DictReader(file)
            for row in dict_reader:
                yield row

    def _filter_data(self, indeces: list[int]):
        index = -1
        for index, row in enumerate(self._read_data()):
            if index in indeces:
                yield row
    
    def _get_data_row(self, row: int):
        for index, row in enumerate(self._read_data()):
            if index == index:
                return row

    def _random_genome(self) -> tuple[int]:
        genome = [self._random_gene() for _ in range(self._genome_size)]
        return tuple(genome)
    
    def _random_gene(self) -> int:
        probability = random.random()
        if probability < 0.4:
            return random.choice(self._positions)
        return 0
    
    @cache
    def _score_fitness(self, genome: tuple[int]) -> float:
        score = 0
        for index, gene in enumerate(genome):
            data = self._get_data_row(index)
            if gene != 0:
                score += float(data['Förtjänst'])
            if float(data['Deadline']) < 0:
                score -= float(data['Deadline']) ** 2
        
        for position in self._positions:
            indeces = [index for index, gene in enumerate(genome) if gene == position]
            if not self._verify_capacity(indeces):
                score = -abs(score * 10_000)
                break
        
        return score
        
    def _verify_capacity(self, indeces: tuple[int]) -> bool:
        total = 0
        for data in self._filter_data(indeces):
            total += float(data['Vikt'])
        if total > self._capacity:
            return False
        return True
    
    def _merge_donors(self, donors: tuple[tuple[int], tuple[int]], stability: float = 1) -> tuple[int]:
        new_genome = []
        for gene_a, gene_b in zip(*donors):
            probability = random.random()
            if probability < stability / 2:
                new_genome.append(gene_a)
            elif probability < stability:
                new_genome.append(gene_b)
            else:
                new_genome.append(self._random_gene())
        return tuple(new_genome)
                

if __name__ == '__main__':
    evaluator = GeneticEvaluator(Path('lagerstatus.csv'))
    evaluator.evaluate(repetition_limit=500)
    evaluator.print_summary()