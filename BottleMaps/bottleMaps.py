from ui_mainwindow import ui_MainWindow
from PySide6.QtGui import QPixmap
from singleton import singleton
from bottleMapsData import BottleMapsData, TiltedWasteData, Coordinate, WasteType
from PIL import Image, ImageDraw
import json

@singleton
class BottleMaps:

    data:BottleMapsData

    def __init__(self):
        json_file_path = "BottleMaps\\TiltedWasteData.json"
        with open(json_file_path, 'r') as file:
            if file == None:
                self.data = BottleMapsData()
            else:
                data = json.load(file)

    def add_waste(self, waste:TiltedWasteData) -> None:
        self.data.add_waste(waste)
        self.save_map()

    def save_map(self):

        self.add_waste(TiltedWasteData(Coordinate(0, 0), WasteType.ball))
        json_string = self.data.json()
        file_name = "BottleMaps\\TiltedWasteData.json"

        with open(file_name, 'w') as file:
            file.write(json_string)

        image = Image.open("BottleMaps\\baseMaps.png")
        draw = ImageDraw.Draw(image)
        for tiltedWasteData in self.data.wastes:
            x = tiltedWasteData.coord.x
            y = tiltedWasteData.coord.y
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill='red', outline='red')
            pass

        ui_MainWindow.label_2.setPixmap(QPixmap(u"BottleMaps/maps2.jpg"))


bottleMaps = BottleMaps()
