from multiprocessing import Pipe, Process
from simulator import *

# The process in which the simulator runs
def simulatorInterface(pipes):

    # Create a simulator object
    simulator = Simulator()

    # Handle the input from the pipe
    def handleCommand(conn):
        # Input from the pipe should be a (cmd, arg) tuple
        cmd, arg = conn.recv()
        if (cmd == "IR"):
            # Send back the IR distance
            conn.send(simulator.robot.getIRSensorDist(arg))
        elif (cmd == "BUMP"):
            # Send back whether the bump sensor was hit or not
            conn.send(simulator.robot.getBumpSensorHit(arg))
        elif (cmd == "VISION"):
            # Send back ball locations
            conn.send(simulator.robot.camera.detectBalls( simulator.balls ) )
        elif (cmd == "MOTOR"):
            motorNum, speed = arg
            # Set the motor speed via the wrapper
            simulator.robot.setMotorSpeed(motorNum, speed)
            conn.send("DONE")
        elif (cmd == "SERVO"):
            servoNum, angle = arg
            # Set the servo angle via the wrapper
            simulator.robot.setServoAngle(servoNum, angle)
            conn.send("DONE")
        elif (cmd == "KILL"):
            simulator.robot.setMotorSpeed(0, 0)
            simulator.robot.setMotorSpeed(1, 0)
            return "KILL"
        else:
            # Raise a value error, because none of the possible inputs
            # were matched
            raise ValueError

    # Constantly poll pipes, then step the simulator
    while True:
        for pipe in pipes:
            if (pipe.poll()):
                if (handleCommand(pipe) == "KILL"):
                    return 0
        simulator.step()
        simulator.draw()


# Called by simulated_main.py to create a simulator interface, which is
# analogous to the arduino interface, providing pipes to any blarghs that need
# to make use of input or output
def createSimulatorInterface(numPipesRequested):
    # Initialize the lists of pipes
    childPipes = []
    parentPipes = []
    # Create the pipes
    for i in range(numPipesRequested):
        childConn, parentConn = Pipe()
        childPipes.append(childConn)
        parentPipes.append(parentConn)

    # Create the process and start it, passing in the child ends of the pipes
    simProc = Process(target = simulatorInterface, args = [childPipes])
    simProc.start()

    # Return the parent ends of the pipes
    return parentPipes

# A wrapper for the connection to the simulator, so that blarghs don't have to
# directly send and recv from the pipe
class SimulatorInterfaceWrapper():
    def __init__(self, conn):
        self.conn = conn

    def getIRDist(self, irNum):
        self.conn.send(("IR", irNum))
        return self.conn.recv()

    def getBumpHit(self, bumpNum):
        self.conn.send(("BUMP", bumpNum))
        return self.conn.recv()

    def getBallsDetected(self):
        self.conn.send(("VISION", None))
        return self.conn.recv()

    def setMotorSpeed(self, motorNum, speed):
        self.conn.send(("MOTOR", (motorNum, speed)))
        return self.conn.recv()

    def setServoAngle(self, servoNum, angle):
        self.conn.send(("SERVO", (servoNum, angle)))
        return self.conn.recv()

if __name__ == "__main__":
    S = Simulator()
    robot = S.robot
    robot.leftMotorSaturation = 1
    robot.rightMotorSaturation = 0.3
    while True:
        S.step()
        S.draw()
