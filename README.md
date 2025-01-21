# AppliceradAI_INL1

## genetics.py
### Evaluator
Class handling a genetic algorithm for finding the optimal
distribution of a set of packages 

#### Parameters
    data_array: numpy.ndarray
        Numpy array containing package information with columns _, weight, earnings, deadline.
    n_positions: int, default: 10
        Number of trucks to pack into.
    position_capacity: int, default: 100
        Maximum weight allowed per truck.
    file_path: Path
        Path-object pointing to file to be read.
    
#### Properties
    data: numpy.ndarray
        Numpy array containing package information with columns _, weight, earnings, deadline.
    n_positions: int
        Number of trucks to pack into.
    position_capacity: int
        Maximum weight allowed per truck.
    population: list[tuple[int]]
        List of genomes of the most recent generation. Start empty.
    best_fitness_scores: list[float]
        List of best fitness scores found over evaluation generations. Starts empty.
    _total_weight: int
        Total summed weight of all packages.
    _total_capacity: int
        Total summed capacity of all trucks.

### Evaluator.evaluate
Attempts to find the best distribution of packages.

#### Parameters
    population_size: int, default: 100
        Number of genomes per generation
    repetition_limit: int, default: 1000
        Number of repeated best fitness before the method self-terminates.
    minimum_growth: float, default: 0.01
        Minimum increase in fitness per generation spent for the method to continue after increase in best fitness.
    max_minutes: int, default: 60
        Upper time limit in minutes before the method self-terminates

### Evaluator.save_results_to_file
Saves best result in population to /deliveries/

### Evaluator._random_genome
Generates genome

#### Returns
    tuple[int]

### Evaluator._random_gene
Generates random gene

#### Returns
    int

### Evaluator._combine_donors
Combines genes of two donors

#### Parameters
    donors: tuple[tuple[int], tuple[int]]
        Tuple of genomes to combine.
    stability: float, default: 1
        Probability of individual gene not mutating.

### Evaluator._score_fitness
Evaluates the fitness of a genome.

#### Parameters
    genome: tuple[int]
        Genome to be evauluated

#### Returns
    int

## main.py
### main
Example use of the genetics.Evaluator class. Does not show off the Evaluator.save_results_to_file method.

## seeder.py
### seed_packages
#### Parameters
    n_iter: int, default 100
        Number of packages to generate.
    target_path: pathlib.Path, default Path('lagerstatus.csv')
        Path of csv-file to save to. Note that if file already exists it will be overwritten.
    