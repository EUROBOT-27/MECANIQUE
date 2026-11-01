from mecanisme import maestro


ServoBot1 = {
    "ServoR": [3, 3200,4800],
    "ServoML": [1,3050, 1920],#2050 ,2950
    "ServoMR": [2, 4000, 6000],
    "ServoL": [0,5950,4000]
}

ServoBot2 = {
    "ServoBanderole": [9,7000,1500],
    "RotateRight": [11, 9000, 200],
   "RotateLeft": [10, 2800, 7000],
   "Elevate_left":[5, 0,10000, 2000],
   "Elevate_Right":[6, 0,2000, 10000]
}

class MechanismServo:
    def __init__(self):
        # Initialize the Maestro Controller
        self.servo = maestro.Controller()
        
        # Initialize ServoBot1
        for servo in ServoBot1.values():
            servo_id = servo[0]
            self.servo.setSpeed(servo_id,0)  # No speed limit
            self.servo.setAccel(servo_id, 0)  # No acceleration limit

            # Initialize servos to a known default position
            self.servo.setTarget(servo_id, servo[1])

        # Initialize ServoBot2
        for servo in ServoBot2.values():
            servo_id = servo[0]
            self.servo.setSpeed(servo_id, 0)  # No speed limit
            self.servo.setAccel(servo_id, 0)  # No acceleration limit

            # Initialize servos to a known default position 
            self.servo.setTarget(servo_id, servo[1])

    def move_servo(self, servo_name, target_position):
        """
        Move a specific servo to a target position.
        """
        # Check if the servo is in either ServoBot1 or ServoBot2
        if servo_name in ServoBot1:
            servo_data = ServoBot1[servo_name]
        elif servo_name in ServoBot2:
            servo_data = ServoBot2[servo_name]
        else:
            raise ValueError(f"Servo '{servo_name}' not found in any ServoBot.")
        
        # Get the servo ID and move it to the target position
        servo_id = servo_data[0]
        self.servo.setTarget(servo_id, target_position)
        print(target_position)
    def move_servo_pos(self, servo_name, position_key):
        """
        Move a specific servo to a target position.
        """
        # Check if the servo is in either ServoBot1 or ServoBot2
        if position_key not in [1,2]:
            raise ValueError("Position key must be 1 (start) or 2")
        if servo_name in ServoBot1:
            servo_data = ServoBot1[servo_name]
        elif servo_name in ServoBot2:
            servo_data = ServoBot2[servo_name]
        else:
            raise ValueError(f"Servo '{servo_name}' not found in any ServoBot.")
        
        # Get the servo ID and move it to the target position
        servo_id = servo_data[0]
        target_position = servo_data[position_key]  
        self.servo.setTarget(servo_id, target_position)
        print(target_position)

    def move_all_servos(self, position_key, group):
        """
        Move all servos in a group to their target position.
        """
        if position_key not in [1,2]:
            raise ValueError("Position key must be 1 (start) or 2")
        
        if group == 1:
            # Move all servos in ServoBot1
            for servo_name, servo_data in ServoBot1.items():
                servo_id = servo_data[0]


        elif group == 2:
            # Move all servos in ServoBot2
            for servo_name, servo_data in ServoBot2.items():
                servo_id = servo_data[0]
                target_position = servo_data[position_key]  
                self.servo.setTarget(servo_id, target_position)
        
        else:
            raise ValueError("Group must be 1 or 2.")
    
    def close_connection(self):
        """
        Close the connection to the servo controller.
        """
        self.servo.close()
 
            


