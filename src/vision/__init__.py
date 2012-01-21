from blargh import Blargh
from vision import Vision

# Eventually should take in vision data and process it
class VisionBlargh(Blargh):
    def __init__(self):
        print "VisionBlargh: init"
        # Initialize the Vision wrapper class for the vision library
        self.vision = Vision()

    def step(self, inp):
        print "VisionBlargh stepped"
        # TODO: Handle walls
        # Update the frame
        self.vision.processBalls()
        # If there is more than 0 balls, then return the location of the first
        # ball-blob
        ballList = []
        for i in range(self.vision.getNumBalls()):
            ballList.append((self.vision.getR(i), self.vision.getTheta(i)))
        print "VisionBlargh: ballList", ballList
        return ballList
