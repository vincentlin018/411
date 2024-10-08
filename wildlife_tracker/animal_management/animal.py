from typing import Any, List, Optional

class Animal:
    def __init__(self,
                 animal_id: int,
                 species: str,
                 age: Optional[int] = None,
                 health_status: Optional[str] = None) -> None:
        self.animal_id = animal_id
        self.species = species
        self.age: Optional[int] = age
        self.health_status = health_status

    def update_animal_details(self, **kwargs: dict[str, Any]) -> None:
        pass

    def get_animal_details(self) -> dict[str, Any]:
        pass