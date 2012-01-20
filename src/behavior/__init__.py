from blargh import Blargh
import time

class State:
    def __init__( self, arduinoInterface, time ):
        self.arduinoInterface = arduinoInterface
        self.startTime = time
        self.lastTime = time
    def step( self, time ):
        self.lastTime = time
        return self

class DodgeWallState( State ):
    def step( self, time ):

	BACKUP_TIME = 2
	TURN_TIME = 2

        if ( time - self.startTime < BACKUP_TIME ):
            self.arduinoInterface.setMotorSpeed( 0, -50 )
            self.arduinoInterface.setMotorSpeed( 1, -50 )
        else:
            self.arduinoInterface.setMotorSpeed( 0, 50 )
            self.arduinoInterface.setMotorSpeed( 0, -50 )

        #Update the state.
        if ( time - self.startTime > BACKUP_TIME + TURN_TIME ):
	    return GoStraightState( arduinoInterface, time )
	else:
	    self.lastTime = time
	    return self)

class GoStraightState( State ):
    def step( self, time ):
	
        self.arduinoInterface.setMotorSpeed(0, 50)
        self.arduinoInterface.setMotorSpeed(1, 50)
	
	#Update the state.
        frontBumperHit = False #TODO get from arduinoInterface
        if ( frontBumperHit ):
            return DodgeWallState( arduinoInterface, time )
	else:
            self.lastTime = time
            return self

class StateMachine:
    def __init__( firstState ):
        self.state = firstState
    def step( time ):
        self.state = self.state.step( time )
        
# Takes in the state of the world and puts out some behavior based on
# previous state (BehaviorBlargh is also a state machine :P)
class BehaviorBlargh(Blargh):

    def __init__(self, arduinoInterfaceOutputWrapper):
        # We use the arduinoInterfaceOutputWrapper to interact with the
        # arduino interface process
        self.arduinoInterface = arduinoInterfaceOutputWrapper
	# Set up the State Machine.
        self.StateMachine = StateMachine( GoStraightState( self.arduinoInterface, time.time() ) )

    def step(self, bumpSensorHit):
        self.StateMachine.step( time.time() )
