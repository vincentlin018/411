from typing import Optional, List

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_management.animal import Animal


class HabitatManager:
    def __init__(self) -> None:
        self.habitats: dict[int, Habitat] = {}

    def get_habitat_by_id(self, habitat_id: int) -> Optional[Habitat]:
        pass

    def create_habitat(self, habitat: Habitat) -> None:
        pass

    def remove_habitat(self, habitat_id: int) -> None:
        pass

    def update_habitat_details(self, habitat_id: int, **kwargs) -> None:
        pass

    def get_habitats_by_environment_type(self, environment_type: str) -> List[Habitat]:
        pass

    def assign_animals_to_habitat(self, habitat_id: int, animals: List[Animal]) -> None:
        pass