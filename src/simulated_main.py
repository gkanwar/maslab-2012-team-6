import sys
sys.path.append("../lib")

import time

from blargh.blargh_process import BlarghProcessStarter, cascadeBlarghProcesses, joinAllBlarghProcesses
from world import WorldBlargh
from behavior import BehaviorBlargh
from control import ControlBlargh
from input import InputBlargh

from simulator import *

# This is the master process, it should control everything. It's also
# what should get called to run this whole thing.

if __name__ == "__main__":
    # Create the simulator interface, and wrappers
    masterConn, visionConn, controlConn = createSimulatorInterface(3)
    visionSimulatorInterface = SimulatorInterfaceWrapper(visionConn)
    controlSimulatorInterface = SimulatorInterfaceWrapper(controlConn)

    # Create the structure for checkpoint 4
    input = BlarghProcessStarter(InputBlargh, [visionSimulatorInterface], True)
    vision = BlarghProcessStarter(VisionBlargh, [visionSimulatorInterface], True)
    world = BlarghProcessStarter(WorldBlargh, [], True)
    behavior = BlarghProcessStarter(BehaviorBlargh, [], False)
    control = BlarghProcessStarter(ControlBlargh, [controlSimulatorInterface], True)

    cascadeBlarghProcesses(input, world)
    cascadeBlarghProcesses(vision, world)
    cascadeBlarghProcesses(world, behavior)
    cascadeBlarghProcesses(behavior, control)

    # Start Everything, and store it in a list.
    processes = [input.start(), vision.start(), world.start(), behavior.start(), control.start()]

    joinAllBlarghProcesses(processes)
