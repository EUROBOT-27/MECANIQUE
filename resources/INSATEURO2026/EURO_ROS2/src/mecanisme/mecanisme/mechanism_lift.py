import RPi.GPIO as GPIO
import time
STEP_PIN = 24 # Replace with your STEP pin number
DIR_PIN = 23
Stepper = {
    "FORKLIFT": [23, 24, 235, 450, 580, 640],
   # "CANS": ["DIR_PIN_CANS", "STEP_PIN_CANS", 50, 150, 250]  
}

class MechanismLift:
    def __init__(self):
        # Set up the GPIO mode to BCM (Broadcom pin-numbering scheme)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        
        for stepper_name, stepper in Stepper.items():
            STEP_PIN = stepper[1]
            DIR_PIN = stepper[0]
            GPIO.setup(23, GPIO.OUT)
            GPIO.setup(24, GPIO.OUT)
            
            setattr(self, f"{stepper_name}_STEP_PIN", STEP_PIN)
            setattr(self, f"{stepper_name}_DIR_PIN", DIR_PIN)
            
            setattr(self, f"{stepper_name}_current_position", stepper[5])  # Position3 as the starting point
    def rotate_motor(self, motor_name, position, step_delay):
 
        # Get the pins for the selected motor
        STEP_PIN = getattr(self, f"{motor_name}_STEP_PIN")
        DIR_PIN = getattr(self, f"{motor_name}_DIR_PIN")
        
        positions = Stepper[motor_name][2:]  # positions are stored starting from index 2
        if position < 1 or position > len(positions):
            raise ValueError(f"Invalid position. Must be between 1 and {len(positions)}.")
        
        target_steps = positions[position - 1]  

        current_position = getattr(self, f"{motor_name}_current_position")
        
        # Determine the direction (up or down) based on the target position
        if target_steps > current_position:
            direction = 'up'
        elif target_steps < current_position:
            direction = 'down'
        else:
            direction = 'no movement'  # No movement if positions are the same

        if direction == 'up':
            GPIO.output(DIR_PIN, GPIO.HIGH)
        elif direction == 'down':
            GPIO.output(DIR_PIN, GPIO.LOW)

        # Rotate the motor by the calculated number of steps
        steps_to_move = abs(target_steps - current_position)  # Calculate the number of steps
        for _ in range(steps_to_move):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(step_delay)

        # After moving, update the current position to the target position
        setattr(self, f"{motor_name}_current_position", target_steps)

    def cleanup(self):
        """
        Cleanup GPIO pins.
        """
        GPIO.cleanup()


