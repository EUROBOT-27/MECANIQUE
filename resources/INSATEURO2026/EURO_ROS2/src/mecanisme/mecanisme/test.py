from mechanism_servo import MechanismServo
from mechanism_lift import MechanismLift
from mechanism_1 import FirstMechanism
import RPi.GPIO as GPIO

import rclpy
import time
RELAY_PUMP_PIN=16
SENSOR1_PIN=8 #left
SENSOR2_PIN=7 #right

#ServoBot1 = {
#    "ServoM1": [2, 3500,4800],
#    "ServoM2": [1,2900, 2050],
#    "ServoMR": [3, 4000, 6000],
#    "ServoML": [0,6000,4000]
#}

def main():
 # Initialize rclpy
    rclpy.init(args=None)
    #x=time.time()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16,GPIO.OUT)
    GPIO.setup(SENSOR1_PIN, GPIO.IN)
    GPIO.setup(SENSOR2_PIN,GPIO.IN)
    #while(1):
    #GPIO.output(RELAY_PUMP_PIN , GPIO.HIGH)
        #time.sleep(2)
  #  GPIO.output(RELAY_PUMP_PIN , GPIO.HIGH)
        #time.sleep(2)
    GPIO.output(16 , GPIO.HIGH)

    #P=MechanismServo()
    #while(1):
    #  P.move_all_servos(1,1)
    #  time.sleep(1)
    #  P.move_all_servos(2,1)
    #  time.sleep(1)
    #P.move_servo("Elevate_left",12000)
    #P.move_servo("Elevate_Right",1000)
    #while(1):
     #print("aa")
    S=FirstMechanism()
    while(1):
      a=int(input("enter a number"))
      if(a==0):
       S.deploy_forklift()
       S.hold_cans()
       #GPIO.output(16 , GPIO.HIGH)

    #S.lift_planks()
    #time.sleep(1)
      if(a==1):
       S.lift_planks()

      elif(a==2):
       S.lift_planks_alot()

    