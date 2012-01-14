import sys, time
sys.path.append("./Libraries/")
import arduino

if __name__=="__main__":
    try:
        ard = arduino.Arduino()
        motor0 = arduino.Motor(ard,0) #0 is the "Qik" number
        motor1 = arduino.Motor(ard,1) #1 is the other number of awesome

        ard.start()
        while not ard.portOpened: True #Wait for the arduino to be ready, before sending commands

        for i in range(30):
            #print "Motor"
            motor0.setVal(i*5)
            motor1.setVal(i*5)
            time.sleep(1)
        ard.close()
    #This is so that when you hit ctrl-C in the terminal, all the arduino threads close. You can do something similar with threads in your program.
    except KeyboardInterrupt:
        print "Ending Program"
        ard.killReceived=True
        
