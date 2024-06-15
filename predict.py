from roboflow import Roboflow
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class ImageDetector:
    def __init__(self):
        rf = Roboflow(api_key="uMUVjvL3wu5Jz1Y3sq4J")
        project = rf.workspace("bao-bao-3gkoq").project("vocimgs")
        version = project.version(1)
        self.model = version.model

def predict(self, image_path:str):
    img = mpimg.imread(image_path)
    result = self.model.predict(img, confidence=40, overlap=30).json()
    for i in range(0, len(result["predictions"])):
        result["predictions"][i].pop("image_path")
    return result["predictions"]