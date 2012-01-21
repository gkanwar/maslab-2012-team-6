from exceptions import ValueError
from multiprocessing import Process, Pipe
import time

# Function that wraps a Blargh and is run in its own process. It keeps track
# of the input pipes and output pipes to interface with other blargh processes.

def blarghProcess(BlarghClass, args, masterConn, inPipes, outPipes, async):

    # Initialize the blargh
    blargh = BlarghClass(*args)

    # Handle a tuple input from the master process
    def handleMasterInput(inp):
        # Unpack the tuple
        cmd, arg = inp
        # Handle the arg based on the cmd
        if (cmd == "KILL"):
            return 0
        else:
            raise ValueError

    # Send out an output to all the outPipes
    def sendOut(output):
        for pipe in outPipes:
            pipe.send(output)
        for pipe in outPipes:
            pipe.recv()

    # Main polling loop
    while True:
        inp = None
        # Poll the master pipe
        if (masterConn.poll()):
            # If there was something, receive it
            cmd = pipe.recv()
            # Process the command
            if (cmd == "KILL"):
                return 0
            else:
                raise ValueError
        # Poll all the other inPipes
        for pipe in inPipes:
            if (pipe.poll()):
                # If there's something waiting, receive it
                inp = pipe.recv()
                # Tell the other end of the pipe we got it
                pipe.send("RECVD")
                sendOut(blargh.step(inp))

        # If there was no input, step with no input if we're running
        # async, otherwise don't step at all
        if (inp == None and async):
            sendOut(blargh.step(None))


# Called from the master process to send the kill signal and join the
# blargh process
def killBlarghProcess(blarghMaster):
    blarghMaster.conn.send(("KILL", None))
    blarghMaster.proc.join()

# Called from the master process to kill all blargh processes in the list
def killAllBlarghProcesses(blarghMasters):
    # Send all the KILL's first, then join them all for efficiency
    for blarghMaster in blarghMasters:
        blarghMaster.conn.send(("KILL", None))
    for blarghMaster in blarghMasters:
        blarghMaster.proc.join()

# Called from the master process to send the correct signals to cascade
# two blargh processes together. Accepts two BlarghProcessStarters and
# sets up their inPipes and outPipes so that they are connected
def cascadeBlarghProcesses(bps1, bps2):
    inPipe, outPipe = Pipe()
    bps1.addOutPipe(outPipe)
    bps2.addInPipe(inPipe)

# The master process's class to set up and then start a blargh process.
# It keeps track of the blargh, inPipes and outPipes. Use this to set up
# all the connections, then call start on all the BlarghProcessStarters
# to actaully start them.
class BlarghProcessStarter():
    def __init__(self, BlarghClass, args, async):
        self.BlarghClass = BlarghClass
        self.args = args
        self.async = async
        self.inPipes = []
        self.outPipes = []

    # Use these functions to set up all the inPipes and outPipes before
    # starting the blarghProcess
    def addInPipe(self, inPipe):
        self.inPipes.append(inPipe)
    def addOutPipe(self, outPipe):
        self.outPipes.append(outPipe)

    # Create the process and return a BlarghMaster wrapper object that
    # contains the process and pipe to it
    def start(self):
        parentMasterConn, childMasterConn = Pipe()
        proc = Process(target = blarghProcess, args = (self.BlarghClass, self.args, childMasterConn, self.inPipes, self.outPipes, self.async))
        proc.start()
        return BlarghMaster(proc, parentMasterConn)

# The master process's wrapper for the blargh process, storing both the
# process and the pipe connecting to it
class BlarghMaster():
    def __init__(self, proc, masterConn):
        self.proc = proc
        self.conn = masterConn
