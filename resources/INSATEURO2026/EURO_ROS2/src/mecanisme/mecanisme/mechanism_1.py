from mecanisme.mechanism_lift import MechanismLift
from mecanisme.mechanism_servo import MechanismServo
from mecanisme.mechanism_servo import ServoBot1
import rclpy
from rclpy.node import Node
import RPi.GPIO as GPIO
import time
SENSOR1_PIN=5 #left
SENSOR2_PIN=6 #right
RELAY_PUMP_PIN=16
Position1=1
Position2=2
Position3=3
Position4=4
Group1=1
Group2=2


class FirstMechanism(Node):
      def __init__(self):
        super().__init__('first_mechanism_node') 
        self.declare_parameter('load_type','nothing')
        self.servo=MechanismServo()
        self.lift=MechanismLift()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PUMP_PIN, GPIO.OUT)
        GPIO.setup(SENSOR1_PIN, GPIO.IN)  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        GPIO.setup(SENSOR2_PIN, GPIO.IN)  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      def release_bonderole_servo(self):
        self.servo.move_servo_pos("ServoBanderole",position_key=Position2)
      def hold_bonderole_servo(self):
        self.servo.move_servo_pos("ServoBanderole",position_key=Position1)

      def lift_planks_alot(self):
        self.lift.rotate_motor("FORKLIFT", Position3 ,0.001)
      def lift_planks_alot_second_mecanism(self):
        self.lift.rotate_motor("FORKLIFT", Position4 ,0.001)

      def initiate_forklift(self):
        self.lift.rotate_motor("FORKLIFT", Position2 ,0.001)

      def deploy_forklift(self):
        self.lift.rotate_motor("FORKLIFT",Position1,0.001)
        #time.sleep(1)
      def lift_planks(self):
        self.lift.rotate_motor("FORKLIFT", Position3 , 0.001)
        self.set_parameters([
            rclpy.parameter.Parameter('load_type', rclpy.Parameter.Type.STRING, 'plank')
        ])
        #time.sleep(1)

      def hold_cans(self):
        self.servo.move_all_servos(position_key=Position2, group=Group1)
      def place_first_cans(self):
        self.servo.move_all_servos(position_key=Position1, group=Group1)
	#self.servo.move_servo_pos("ServoML",position_key=Position1)
        #self.servo.move_servo_pos("ServoMR",position_key=Position1)
        #self.servo.move_servo_pos("RotateRight",position_key=Position2)
        #self.servo.move_servo_pos("RotateLeft",position_key=Position2)
      def place_first_cans_second_mecanism(self):
        self.servo.move_servo_pos("ServoML",position_key=Position1)
        self.servo.move_servo_pos("ServoMR",position_key=Position1)
        self.servo.move_servo_pos("RotateRight",position_key=Position2)
        self.servo.move_servo_pos("RotateLeft",position_key=Position2)

      def hold_plank(self):
        GPIO.output(RELAY_PUMP_PIN , GPIO.LOW)
        self.lift.rotate_motor("FORKLIFT", Position4 , 0.001)
      def place_first_plank_and_pick_last_cans(self):
        self.lift.rotate_motor("FORKLIFT", Position1, 0.001)
      def place_first_plank_and_pick_last_cans_second_mecanism(self):
        x=time.time()
        self.lift.rotate_motor("FORKLIFT", Position1, 0.001)
        self.servo.move_servo_pos("Elevate_left",position_key=Position2)
        self.servo.move_servo_pos("Elevate_Right",position_key=Position2)
        while((time.time()-x)<3.6):
          print("wait")
          time.sleep(0.1)
        print("khrajna")
        self.servo.move_servo_pos("Elevate_left",position_key=Position1)
        self.servo.move_servo_pos("Elevate_Right",position_key=Position1)



      def place_last_cans_and_second_plank(self):
        self.servo.move_servo_pos("RotateRight",position_key=Position1)
        self.servo.move_servo_pos("RotateLeft",position_key=Position1)
        time.sleep(1)
        self.servo.move_servo_pos("ServoL",position_key=Position1)
        self.servo.move_servo_pos("ServoR",position_key=Position1)
        time.sleep(1)
        self.servo.move_servo_pos("ELevate_left",position_key=Position3)
        self.servo.move_servo_pos("Elevate_Right",position_key=Position3)
        time.sleep(0.5)
        self.servo.move_servo_pos("RotateRight",position_key=Position2)
        self.servo.move_servo_pos("RotateLeft",position_key=Position2)
        time.sleep(2)

        GPIO.output(RELAY_PUMP_PIN,GPIO.HIGH)


      def finish_building(self):
        self.servo.move_servo_pos("Elevate_left",position_key=Position3)
        self.servo.move_servo_pos("Elevate_Right",position_key=Position3)
        while(1):
          if((GPIO.input(SENSOR1_PIN) == GPIO.LOW) and (GPIO.input(SENSOR2_PIN) == GPIO.HIGH)):
            self.servo.move_servo_pos("Elevate_left",position_key=Position1)
          elif ((GPIO.input(SENSOR1_PIN) == GPIO.HIGH) and (GPIO.input(SENSOR2_PIN) == GPIO.LOW)):
            self.servo.move_servo_pos("Elevate_Right",position_key=Position1)
          elif ((GPIO.input(SENSOR1_PIN) == GPIO.LOW) and (GPIO.input(SENSOR2_PIN) == GPIO.LOW)):
            self.servo.move_servo_pos("Elevate_left",position_key=Position1)
            self.servo.move_servo_pos("Elevate_Right",position_key=Position1)
            break
          print("wait")
          time.sleep(0.1)

        self.servo.move_servo_pos("RotateRight",position_key=Position1)
        self.servo.move_servo_pos("RotateLeft",position_key=Position1)
        self.servo.move_all_servos(position_key=Position1, group=Group1)
      def destroy_node(self):
        GPIO.cleanup()  # Cleanup GPIO when the node is destroyed
        super().destroy_node()

