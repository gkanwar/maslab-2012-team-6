from blargh import Blargh
from vision import Vision

# Eventually should take in vision data and process it
class VisionBlargh(Blargh):
    def __init__(self):
        # Initialize the Vision object
        self.vision = Vision()

    def step(self, inp):
        # TODO: Handle walls
        # Update the frame
        self.vision.processBalls()
        # If there is more than 0 balls, then return the location of the first
        # ball-blob
        ballList = []
        for i in range(self.vision.getNumBalls()):
            ballList.append((self.vision.getR(i), self.vision.getTheta(i)))
        return (0,(ballList,self.vision.getYellowCenterT))
