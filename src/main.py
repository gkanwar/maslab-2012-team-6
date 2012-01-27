import sys
sys.path.append("../lib")

import time

from blargh.blargh_process import *
from vision import VisionBlargh
from world import WorldBlargh
from behavior import BehaviorBlargh
from control import ControlBlargh
from input import InputBlargh

from arduino import createArduinoInterface, ArduinoInterfaceWrapper

# This is the master process, it should control everything. It's also
# what should get called to run this whole thing.

if __name__ == "__main__":

    # Create the arduino interface
    masterConn, inputConn, controlConn = createArduinoInterface(3)
    arduinoInputWrapper = ArduinoInterfaceWrapper(inputConn)
    arduinoControlWrapper = ArduinoInterfaceWrapper(controlConn)

    '''
    Example for creating blargh structure:
    b1 = ExampleBlargh1()
    b2 = ExampleBlargh2()
    b12 = CascadeBlargh(b1, b2)
    b3 = ExampleBlargh3()
    b3proc = createBlarghProcess(b12, False)
    b12proc = createBlarghProcess(b12, True)
    cascadeBlarghProcesses(b12proc, b3proc)
    In this, the b12proc is asynchronous, so it will constantly step
    b12 with "NONE" inputs every time. The b3proc is synchronous,
    so it will wait for actual inputs coming in through the pipe to
    step b3.
    '''
    #Create the structure for checkpoint 4.
    input = BlarghProcessStarter( InputBlargh, [arduinoInputWrapper], True )
    vision = BlarghProcessStarter( VisionBlargh, [], True )
    world = BlarghProcessStarter( WorldBlargh, [], True) #Async for Odometry purposes.
    behavior = BlarghProcessStarter( BehaviorBlargh, [], False) #Async because this has timeouts, etc.
    control = BlarghProcessStarter( ControlBlargh, [arduinoControlWrapper], True )

    cascadeBlarghProcesses(input, world);
    cascadeBlarghProcesses(vision, world)
    cascadeBlarghProcesses(world, behavior)
    cascadeBlarghProcesses(behavior, control)
    #Start Everything, and store it in a ist.
    processes = [input.start(), vision.start(), world.start(), behavior.start(), control.start()]

    # Wait for everything else to die before quitting
    joinAllBlarghProcesses(processes)
