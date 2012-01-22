import sys
sys.path.append("../lib")

import time

from blargh.blargh_process import BlarghProcessStarter, cascadeBlarghProcesses, killAllBlarghProcesses
from world import WorldBlargh
from behavior import BehaviorBlargh
from controls import ControlBlargh

from simulator import *

# This is the master process, it should control everything. It's also
# what should get called to run this whole thing.

if __name__ == "__main__":
    #Create the simulator
    simulator = Simulator()
    robotOutputInterface = simulator.robot

    #Create the structure for checkpoint 4.
    vision = BlarghProcessStarter( VisionBlargh, [ simulator ], True )
    world = BlarghProcessStarter( WorldBlargh, (), True) #Async for Odometry purposes.
    behavior = BlarghProcessStarter( BehaviorBlargh, (), True) #Async because this has timeouts, etc.
    control = BlarghProcessStarter( ControlBlargh, [ robotOutputInterface ], True )

    sim = BlarghProcessStarter( SimulatorBlargh, [ simulator ], True )

    cascadeBlarghProcesses(vision, world)
    cascadeBlarghProcesses(world, behavior)
    cascadeBlarghProcesses(behavior, control)
    cascadeBlarghProcesses(control, sim)

    #Start Everything, and store it in a list.
    processes = [ vision.start(), world.start(), behavior.start(), control.start(), sim.start() ]

    # TODO: Main timer loop, kill all processes when time runs out
    startTime = time.time()
    while time.time() - startTime < 3 * 60:
        time.sleep(1)

    print "Killing Everything!"
    killAllBlarghProcesses( processes )
    masterConn.send("KILL")
