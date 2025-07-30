from dataclasses import dataclass


@dataclass
class Apartment:
    num_of_rooms: int
    area: int
    living_area: int
    kitchen_area: int
    floor: int
    floors_in_house: int
    year_of_building: int
    price: float