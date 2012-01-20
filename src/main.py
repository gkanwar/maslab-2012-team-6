import sys
sys.path.append("../lib")

import time

from blargh.blargh_process import BlarghProcessStarter, cascadeBlarghProcesses, killAllBlarghProcesses
from vision import VisionBlargh
from pid import PIDBlargh
from arduino import createArduinoInterface, ArduinoInterfaceInputWrapper, ArduinoInterfaceOutputWrapper

# This is the master process, it should control everything. It's also
# what should get called to run this whole thing.

if __name__ == "__main__":

    # Create the arduino interface
    masterConn, inputConn, outputConn = createArduinoInterface()
    arduinoInterfaceInputWrapper = ArduinoInterfaceInputWrapper(inputConn)
    arduinoInterfaceOutputWrapper = ArduinoInterfaceOutputWrapper(outputConn)

    # Example for creating blargh structure:
    # b1 = ExampleBlargh1()
    # b2 = ExampleBlargh2()
    # b12 = CascadeBlargh(b1, b2)
    # b3 = ExampleBlargh3()
    # b3proc = createBlarghProcess(b12, False)
    # b12proc = createBlarghProcess(b12, True)
    # cascadeBlarghProcesses(b12proc, b3proc)
    # In this, the b12proc is asynchronous, so it will constantly step
    # b12 with "NONE" inputs every time. The b3proc is synchronous,
    # so it will wait for actual inputs coming in through the pipe to
    # step b3.
    

    # Create the blargh structure that we need
    vision = VisionBlargh()
    pid = PIDBlargh(arduinoInterfaceOutputWrapper)

    visionProcStarter = BlarghProcessStarter(vision, True)
    pidProcStarter = BlarghProcessStarter(pid, False)

    cascadeBlarghProcesses(visionProcStarter, pidProcStarter)

    visionProc = visionProcStarter.start()
    pidProc = pidProcStarter.start()

    timer = time.time()

    # TODO: Main timer loop, kill all processes when time runs out
    while time.time() - timer < 5:
        time.sleep(1)

    print "Killing!"

    killAllBlarghProcesses([visionProc, pidProc])
    masterConn.send("KILL")
