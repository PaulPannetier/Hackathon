from enum import Enum
import json

class WasteType(Enum):
    ball="ball"
    bottle="bottle"
    branch="branch"
    grass="grass"
    leaf="leaf"
    milk_box="milk_box"
    plastic_bag="plastic_bag"
    plastic_garbage="plastic_garbage"

class Coordinate:
    x:float
    y:float

    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y

class TiltedWasteData: 
    coord:Coordinate
    type:WasteType

    def __init__(self, coord:Coordinate, type:WasteType):
        self.coord = coord
        self.type = type

class BottleMapsData:
    
    wastes:list[TiltedWasteData]

    def __init__(self):
        self.wastes = []

    def add_waste(self, waste:TiltedWasteData) -> None:
        self.wastes.append(waste)

    def json(self) -> str:
            return json.dumps({'wastes': [waste.to_dict() for waste in self.wastes]}, indent=4)
