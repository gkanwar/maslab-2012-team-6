import sys
sys.path.append("../lib")

from blargh.blargh_process import BlarghProcessStarter, cascadeBlarghProcesses
from input import InputBlargh
from behavior import BehaviorBlargh
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
    input = InputBlargh(arduinoInterfaceInputWrapper)
    behavior = BehaviorBlargh(arduinoInterfaceOutputWrapper)

    inputProcStarter = BlarghProcessStarter(input, True)
    behaviorProcStarter = BlarghProcessStarter(behavior, False)

    cascadeBlarghProcesses(inputProcStarter, behaviorProcStarter)

    inputProc = inputProcStarter.start()
    behaviorProc = behaviorProcStarter.start()

    # TODO: Main timer loop, kill all processes when time runs out
    while True:
        pass
