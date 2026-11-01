# Single servo command
# Used to control one servo on the Maestro 12x controller

uint8 servo_id          # Servo channel (0-11 for Maestro 12x)
bool enabled            # true=servo active, false=servo off (moves to safe position)
uint8 target_angle      # Target angle in degrees (0-180)
