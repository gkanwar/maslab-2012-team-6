from blargh import Blargh
from vision import Vision

# Eventually should take in vision data and process it
class VisionBlargh(Blargh):
    def __init__(self):
        # Initialize the Vision wrapper class for the vision library
        self.vision = Vision()

    def step(self, inp):
        # TODO: Handle more than one ball; handle walls
        # Update the frame
        self.vision.bar()
        # If there is more than 0 balls, then return the location of the first
        # ball-blob
        if (self.vision.getNumBalls() > 0):
            return (self.vision.getR(0), self.vision.getTheta(0))
        else:
            return None
