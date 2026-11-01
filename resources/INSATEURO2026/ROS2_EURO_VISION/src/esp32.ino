#include <Arduino.h>
#include "driver/twai.h"

// ================== UART MAESTRO ==================
const gpio_num_t MAESTRO_RX = GPIO_NUM_16;  
const gpio_num_t MAESTRO_TX = GPIO_NUM_17;  
HardwareSerial MaestroSerial(2);            

// ================== CAN  ====================
#define CAN_TX GPIO_NUM_5
#define CAN_RX GPIO_NUM_4
#define CAN_ID_SERVO 0x100

// ================== SERVO =========================
// 4 Servos: channels 0-3 on Maestro 12x
#define NUM_SERVOS 4

// Servo state structure
struct ServoState {
  bool enabled;
  uint16_t targetAngle;  // 0-180 degrees
};

ServoState servos[NUM_SERVOS] = {{false, 90}, {false, 90}, {false, 90}, {false, 90}};

// Convert angle (0-180°) to Maestro units (typically 4000-8000 for 0-180°)
uint16_t angleToMaestroUnits(uint16_t angle) {
  // Map 0-180 degrees to 4000-8000 quarter-microseconds
  if (angle > 180) angle = 180;
  return 4000 + (angle * 4000 / 180);
}

// ================== MAESTRO FUNCTIONS =============
void maestroSetTarget(uint8_t channel, uint16_t target) {
  MaestroSerial.write(0x84);
  MaestroSerial.write(channel);
  MaestroSerial.write(target & 0x7F);
  MaestroSerial.write((target >> 7) & 0x7F);
}

void maestroSetSpeed(uint8_t channel, uint16_t speed) {
  MaestroSerial.write(0x87);
  MaestroSerial.write(channel);
  MaestroSerial.write(speed & 0x7F);
  MaestroSerial.write((speed >> 7) & 0x7F);
}

void maestroSetAccel(uint8_t channel, uint16_t accel) {
  MaestroSerial.write(0x89);
  MaestroSerial.write(channel);
  MaestroSerial.write(accel & 0x7F);
  MaestroSerial.write((accel >> 7) & 0x7F);
}

// ================== SETUP ==========================
void setup() {
  Serial.begin(115200);

  // UART Maestro
  MaestroSerial.begin(9600, SERIAL_8N1, MAESTRO_RX, MAESTRO_TX);
  Serial.println("Maestro UART ready");

  // Initialize all 4 servos with default speed and acceleration
  for (int i = 0; i < NUM_SERVOS; i++) {
    maestroSetSpeed(i, 20);
    maestroSetAccel(i, 10);
  }

  // CAN config
  twai_general_config_t g_config =
      TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX, CAN_RX, TWAI_MODE_NORMAL);
  twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
  twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

  if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
    Serial.println("CAN driver installed");
  } else {
    Serial.println("CAN install FAILED");
    return;
  }

  if (twai_start() == ESP_OK) {
    Serial.println("CAN started");
  } else {
    Serial.println("CAN start FAILED");
    return;
  }
}

// ================== LOOP ===========================
void loop() {
  twai_message_t message;

  // Check CAN message
  if (twai_receive(&message, pdMS_TO_TICKS(100)) == ESP_OK) {
    if (!message.extd &&
        message.identifier == CAN_ID_SERVO &&
        message.data_length_code >= 8) {

      // Message format: [en1, angle1, en2, angle2, en3, angle3, en4, angle4]
      // Each enable is 1 byte (0 or 1), each angle is 1 byte (0-180)
      Serial.println("CAN: Received servo command");
      
      for (int i = 0; i < NUM_SERVOS; i++) {
        uint8_t enable = message.data[i * 2];      // Enable byte
        uint8_t angle = message.data[i * 2 + 1];   // Angle byte
        
        servos[i].enabled = (enable == 1);
        servos[i].targetAngle = angle;
        
        if (servos[i].enabled) {
          // Servo is enabled, set target position
          uint16_t maestroTarget = angleToMaestroUnits(angle);
          maestroSetTarget(i, maestroTarget);
          Serial.printf("Servo %d: ON at %d degrees (Maestro: %d)\n", i, angle, maestroTarget);
        } else {
          // Servo is disabled, move to safe position (90 degrees center)
          uint16_t maestroTarget = angleToMaestroUnits(90);
          maestroSetTarget(i, maestroTarget);
          Serial.printf("Servo %d: OFF (moved to 90°)\n", i);
        }
      }
    }
  }
}