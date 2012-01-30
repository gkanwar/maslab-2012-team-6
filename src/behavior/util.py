# Utility functions and constants

STATE_CHANGE_FLAG = 0

def timeEqualizedRandom(lastTime, curTime, probPerSec):
    return 1 - (1 - probPerSec)**(curTime - lastTime)
