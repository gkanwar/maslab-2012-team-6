from util import STATE_CHANGE_FLAG

class StateMachine:
    def __init__( self, firstState ):
        # Initialize the state and goal
        self.state = firstState
        self.goal = STATE_CHANGE_FLAG

    def step(self, worldWrapper):
        # Step the state and get the next state and goal
        newState, goal = self.state.step(worldWrapper)
        # Debugging print
        if newState != self.state:
            print "State is", newState
        # Update our state and goal based on our step
        self.state, self.goal = newState, goal
