import arduino
import arduino_wrapper


#Class for controlling the motor
class Motor ():
    
    SERVO_START_PORT = 3

    def __init__(self,motorNumber,arduinoWrap,analogSensor = None):
        # Initialize the motor in the wrapper clas, get a reference to the wrapper
        self.number = motorNumber
        self.arduinoWrap = arduinoWrap
        self.motor = arduino.Motor(self.arduinoWrap.ard,motorNumber)
        self.arduinoWrap.motors.append(self.motor)
        self.sensor = analogSensor

    def setVelocity(self, velocity,arduinoWrap):
        # Use the global motor to set the velocity
        self.velocity = velocity
        self.motor.setVal(velocity)

    def getSetVelocity(self):
        # Returns the velocity that has been set to the motor
        return self.velocity #Possibly modify to return a speed in rad/sec or m/s?
    
    def getRealVelocity(self):
        # Returns the real value of the velocity from the encoder attached to the motor
        return self.sensor.getValue()


#------------------------------------------------------------------------------------------
class Servo():
    def __init__(self, servoNumber,arduinoWrap):
        # Initialize the servo in the wrapper class, get a reference to the wrapper
        self.number = servoNumber
        self.arduinoWrap = arduinoWrap
        self.servo = arduino.Servo(ard,SERVO_START_PORT + servoNumber)
        self.arduinoWrap.servos.append(self.servo)
    
    def setAngle(self, angle):
        # Set the angle of the servo, store value
        self.angle = angle
        self.servo.SetVal(angle)
    
    def getAngle(self):
        # Return the angle the servo is currently at
        return self.angle
