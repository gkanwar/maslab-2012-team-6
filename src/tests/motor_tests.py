import sys
sys.path.append("..")

from arduino import *
a = Arduino()
mc0 = MotorController(a, 18, 19)
m0 = Motor(a, mc0)
m1 = Motor(a, mc0)
mc1 = MotorController(a, 16, 17)
spinner = Motor(a, mc1)

a.run()

import time

m0.setVal(50)
time.sleep(1)
m0.setVal(-50)
time.sleep(1)
m0.setVal(0)

m1.setVal(50)
time.sleep(1)
m1.setVal(-50)
time.sleep(1)
m1.setVal(0)

spinner.setVal(50)
time.sleep(1)
spinner.setVal(0)
