import sys
sys.path.append("..")


from arduino import *
a = Arduino()
left = BumpSensor(a, 4)
right = BumpSensor(a, 2)
front = BumpSensor(a, 6)

leftFront = IRSensor(a, 1)
leftSide = IRSensor(a, 0)

a.run()

while True:
    print [left.hit(), right.hit(), front.hit(), leftFront.dist(), leftSide.dist()]
