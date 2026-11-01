# Status feedback from ESP32 about mechanism states
# Reports current state of servos and mechanisms

bool[] servo_enabled    # Array of servo states (true=active, false=inactive)
uint8[] servo_angles    # Array of current servo angles (0-180 degrees)
bool communication_ok   # CAN communication health status
string error_message    # Error description if any (empty if ok)
