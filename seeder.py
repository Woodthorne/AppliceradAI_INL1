import csv
import random
from pathlib import Path

def seed_packages(
        n_iter: int = 100,
        target_path: Path = Path('lagerstatus.csv')
) -> None:
    '''Seeds random packages to file
    
    Parameters
    ----------
    n_iter: int, default 100
        Number of packages to generate.
    target_path: pathlib.Path, default Path('lagerstatus.csv')
        Path of csv-file to save to. Note that if file already exists
        it will be overwritten.
    '''
    assert 0 < n_iter, 'n_iter needs to be a positive integer'
    assert n_iter < 9_000_000_000, 'n_iter needs to be less than 9 billion'
    assert target_path.suffix == '.csv', f'[{target_path.suffix}] target path needs to be csv-file'

    entries = []
    id_num = random.randint(1_000_000_000, 9_999_999_999 - n_iter)
    for _ in range(n_iter):
        id_num += 1
        weight = round((random.randint(10, 150) + random.randint(10, 80)) / 20, 1)
        profit = int((random.randint(1, 10) + random.randint(1, 10)) / 2)
        deadline = int((random.randint(-1, 7) + random.randint(-3, 3)) / 2)
        entries.append(
            {
                'Paket_id': id_num,
                'Vikt': weight,
                'Förtjänst': profit,
                'Deadline': deadline
            }
        )

    fieldnames = 'Paket_id','Vikt','Förtjänst','Deadline'
    with target_path.open('w', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(entries)

if __name__ == '__main__':
    seed_packages()