class Package:
    def __init__(
            self,
            package_id: int,
            weight: float,
            profit: int,
            deadline: int
    ) -> None:
        self.id = package_id
        self.weight = weight
        self.profit = profit
        self.deadline = deadline

class Truck:
    def __init__(self, truck_id: str, capacity: int = 800) -> None:
        self.id = truck_id
        self.capacity = capacity
        self._freight: list[Package] = []

    @property
    def freight(self) -> list[Package]:
        return self._freight
    
    def used_capacity(self) -> float:
        return sum([package.weight for package in self.freight])

    def free_capacity(self) -> float:
        return self.capacity - self.used_capacity()

    def load(self, package: Package) -> bool:
        if package.weight <= self.free_capacity():
            self._freight.append(package)
            return True
        return False
    
    def get_loaded_ids(self) -> list[int]:
        return [package.id for package in self.freight]