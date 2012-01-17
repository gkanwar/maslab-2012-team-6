from blargh import Blargh
from vision import Vision
# Eventually should take in vision data and process it
class VisionBlargh(Blargh):
    def __init__(self):
        self.vision = Vision()

    def step(self, inp):
        self.vision.bar()
        if (self.vision.getNumBalls() > 0):
            return (self.vision.getR(0), self.vision.getTheta(0))
        else:
            return None
