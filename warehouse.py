from pathlib import Path

import numpy as np

from models import Truck


class Warehouse:
    def __init__(self, inventory_path: Path) -> None:
        self.inventory_path = inventory_path
        self.trucks = [Truck(f'bil_{num}') for num in range(1, 11)]
    
    def get_summary(self) -> dict[str, int|float]:
        inventory = self._read_inventory()
        loaded_ids = self._get_loaded_ids()
        
        current_profit = sum(
            [row['profit'] for row in inventory
             if row['package_id'] in loaded_ids]
        )
        current_profit -= sum(
            [row['deadline'] ** 2 for row in inventory
             if row['package_id'] in loaded_ids and row['deadline'] < 0]
        )
        
        remaining_penalty = -sum(
            [row['deadline'] ** 2 for row in inventory
             if row['package_id'] not in loaded_ids]
        )

        remaining_packages = len(
            [row for row in inventory
             if row['package_id'] not in loaded_ids]
        )

        remaining_profit = sum(
            [row['profit'] for row in inventory
             if row['package_id'] not in loaded_ids]
        )

        summary_output = {
            'profit_today': int(current_profit),
            'penalty_remaining': int(remaining_penalty),
            'packages_remaining': int(remaining_packages),
            'profit_remaining': int(remaining_profit)
        }

        return summary_output

    def _read_inventory(self) -> np.ndarray:
        names = ['package_id', 'weight', 'profit', 'deadline']
        return np.genfromtxt(
            fname = self.inventory_path,
            delimiter = ',',
            names = names,
            skip_header = 1
        )
    
    def _get_loaded_ids(self) -> list[int]:
        loaded_ids = []
        [loaded_ids.extend(truck.get_loaded_ids()) for truck in self.trucks]
        return loaded_ids

if __name__ == '__main__':
    wares = Warehouse(Path('lagerstatus.csv'))
    print(wares.get_summary())