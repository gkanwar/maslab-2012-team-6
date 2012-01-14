# Blarghs are classes that define a step function as seen below. They are
# designed to be able to chain together so that they can start with some input
# and have it cascade through all of them to have some final processed output.
class Blargh():
    # step() gets called by whatever is running the Blargh
    # Subclasses should override this to do whatever needs to be done
    # each step
    def step(self, inp):
        # If this is not overriden we should raise an exception
        raise NotImplementedError

# A Blargh that actually contains two blarghs cascaded together.
class CascadeBlargh(Blargh):
    def __init__(self, b1, b2):
        # Keep track of the two Blarghs we're cascading
        self.b1 = b1
        self.b2 = b2

    def step(self, inp):
        # Cascade the input through the two Blarghs
        out1 = self.b1.step(inp)
        out2 = self.b2.step(out1)
        return out2
