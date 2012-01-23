import sys
sys.path.append("../lib")

import time

from blargh.blargh_process import BlarghProcessStarter, cascadeBlarghProcesses, killAllBlarghProcesses, killBlarghProcess
from world import WorldBlargh
from behavior import BehaviorBlargh
from control import ControlBlargh

from simulator import *

# This is the master process, it should control everything. It's also
# what should get called to run this whole thing.

if __name__ == "__main__":
    # Create the simulator interface, and wrappers
    masterConn, visionConn, controlConn = createSimulatorInterface(3)
    visionSimulatorInterface = SimulatorInterfaceWrapper(visionConn)
    controlSimulatorInterface = SimulatorInterfaceWrapper(controlConn)

    # Create the structure for checkpoint 4
    vision = BlarghProcessStarter(VisionBlargh, [visionSimulatorInterface], True)
    world = BlarghProcessStarter(WorldBlargh, [], True)
    behavior = BlarghProcessStarter(BehaviorBlargh, [], True)
    control = BlarghProcessStarter(ControlBlargh, [controlSimulatorInterface], True)

    cascadeBlarghProcesses(vision, world)
    cascadeBlarghProcesses(world, behavior)
    cascadeBlarghProcesses(behavior, control)

    # Start Everything, and store it in a list.
    processes = [vision.start(), world.start(), behavior.start(), control.start()]

    # Main timer loop, kill all processes when time runs out
    # FIXME
    startTime = time.time()
    while time.time() - startTime < 3 * 30:
        time.sleep(1)

    print "Killing Everything!"
    #killAllBlarghProcesses(processes)
    for proc in processes:
        killBlarghProcess(proc)
    masterConn.send(("KILL", None))
