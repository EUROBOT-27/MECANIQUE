#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MCP23X17.h>

// ================== 1. HARDWARE CONFIGURATION ===================

// --- MAESTRO ---
const gpio_num_t MAESTRO_RX = GPIO_NUM_16;  
const gpio_num_t MAESTRO_TX = GPIO_NUM_17;  
HardwareSerial MaestroSerial(2); 

// --- MCP23017 VALVES ---
const int VANNES[] = {7, 6, 5, 4}; 
const int POMPE = 8;

#define SUCKER_ARM_1    0 
#define SUCKER_ARM_2    1 
#define SUCKER_INT_1    2 
#define SUCKER_INT_2    3 

// --- MAESTRO CHANNELS ---
#define CH_ARM1_SHOULDER   0
#define CH_ARM1_ELBOW      1
#define CH_ARM1_WRIST      2
#define CH_ARM2_SHOULDER   3
#define CH_ARM2_ELBOW      4
#define CH_ARM2_WRIST      5

// --- INTERNAL ROTATION CHANNELS ---
#define CH_ROT_1           6  // Left Storage
#define CH_ROT_2           7  // Right Storage

// ================== 2. CALIBRATION & POSITIONS ==================

// --- ARM 1 ---
#define A1_PICK_S  3843   
#define A1_PICK_E  10549  
#define A1_PICK_W  7196   
#define A1_INT_S   3375   
#define A1_INT_E   2595   
#define A1_INT_W   1035   

// --- ARM 2 ---
#define A2_PICK_S  4077   
#define A2_PICK_E  9301   
#define A2_PICK_W  7897   
#define A2_INT_S   3219   
#define A2_INT_E   2595   
#define A2_INT_W   2829   

// --- ROTATION (180 DEGREE RANGE) ---
// 0 deg = 4000 (1000us), 180 deg = 8000 (2000us)
// If you need wider range, use 2000 (500us) to 10000 (2500us)
#define ROT_FLAT   4000   
#define ROT_TILT   8000   

enum ArmPose {
    POSE_HOME_SAFE,       
    POSE_PICKUP_EXTERNAL, 
    POSE_GRIP_INTERNAL    
};

// ================== 3. GLOBAL OBJECTS ===========================
Adafruit_MCP23X17 mcp;

// ================== 4. MAESTRO DRIVER ===========================

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

void moveArm(int armID, ArmPose pose) {
    int tS, tE, tW; 
    if (armID == 1) {
        switch (pose) {
            case POSE_HOME_SAFE:
            case POSE_GRIP_INTERNAL:
                tS = A1_INT_S; tE = A1_INT_E; tW = A1_INT_W; break;
            case POSE_PICKUP_EXTERNAL:
                tS = A1_PICK_S; tE = A1_PICK_E; tW = A1_PICK_W; break;
        }
        maestroSetTarget(CH_ARM1_SHOULDER, tS);
        maestroSetTarget(CH_ARM1_ELBOW,    tE);
        maestroSetTarget(CH_ARM1_WRIST,    tW);
    } 
    else if (armID == 2) {
        switch (pose) {
            case POSE_HOME_SAFE:
            case POSE_GRIP_INTERNAL:
                tS = A2_INT_S; tE = A2_INT_E; tW = A2_INT_W; break;
            case POSE_PICKUP_EXTERNAL:
                tS = A2_PICK_S; tE = A2_PICK_E; tW = A2_PICK_W; break;
        }
        maestroSetTarget(CH_ARM2_SHOULDER, tS);
        maestroSetTarget(CH_ARM2_ELBOW,    tE);
        maestroSetTarget(CH_ARM2_WRIST,    tW);
    }
}

/**
 * Control Rotation Servos.
 * @param unit: 1 = Left, 2 = Right, 0 = Both
 * @param tilted: true = TILT (180 deg), false = FLAT (0 deg)
 */
void rotateInternalStorage(int unit, bool tilted) {
    uint16_t target = tilted ? ROT_TILT : ROT_FLAT;
    
    if (unit == 1) {
        Serial.printf(">>> ROT 1: %s\n", tilted ? "TILT" : "FLAT");
        maestroSetTarget(CH_ROT_1, target);
    } 
    else if (unit == 2) {
        Serial.printf(">>> ROT 2: %s\n", tilted ? "TILT" : "FLAT");
        maestroSetTarget(CH_ROT_2, target);
    } 
    else if (unit == 0) { // BOTH
        Serial.printf(">>> ROT ALL: %s\n", tilted ? "TILT" : "FLAT");
        maestroSetTarget(CH_ROT_1, target);
        maestroSetTarget(CH_ROT_2, target);
    }
}

// ================== 5. VALVE FUNCTIONS ==========================

void setValve(int index, bool state) {
  if (index >= 0 && index < 4) {
      mcp.digitalWrite(VANNES[index], state ? HIGH : LOW);
  }
}

// ================== 6. SEQUENCE LOGIC ===========================

void runHoming() {
    Serial.println(">>> HOME");
    moveArm(1, POSE_HOME_SAFE);
    moveArm(2, POSE_HOME_SAFE);
    rotateInternalStorage(0, false); // Flatten BOTH
}

void runPickup1_Store() {
    Serial.println(">>> PICKUP 1: STORE INTERNALLY");

    rotateInternalStorage(0, false); // Ensure both Flat
    delay(500);

    // 1. Extend & Grab
    moveArm(1, POSE_PICKUP_EXTERNAL);
    moveArm(2, POSE_PICKUP_EXTERNAL);
    delay(1500); 
    setValve(SUCKER_ARM_1, true);
    setValve(SUCKER_ARM_2, true);
    delay(500); 

    // 2. Transfer
    moveArm(1, POSE_GRIP_INTERNAL);
    moveArm(2, POSE_GRIP_INTERNAL);
    delay(1500);
    setValve(SUCKER_INT_1, true);
    setValve(SUCKER_INT_2, true);
    delay(500);
    setValve(SUCKER_ARM_1, false);
    setValve(SUCKER_ARM_2, false);
    delay(500);
    
    Serial.println(">>> STORED.");
}

void runPickup2_Hold() {
    Serial.println(">>> PICKUP 2: HOLD");
    moveArm(1, POSE_PICKUP_EXTERNAL);
    moveArm(2, POSE_PICKUP_EXTERNAL);
    delay(1500); 
    setValve(SUCKER_ARM_1, true);
    setValve(SUCKER_ARM_2, true);
    delay(500); 
    moveArm(1, POSE_GRIP_INTERNAL);
    moveArm(2, POSE_GRIP_INTERNAL);
    delay(1500);
}

void runDrop1_FromArms() {
    Serial.println(">>> DROP 1: ARMS");
    moveArm(1, POSE_PICKUP_EXTERNAL); 
    moveArm(2, POSE_PICKUP_EXTERNAL);
    delay(1500);
    setValve(SUCKER_ARM_1, false); 
    setValve(SUCKER_ARM_2, false);
    delay(500);
    moveArm(1, POSE_HOME_SAFE); 
    moveArm(2, POSE_HOME_SAFE);
}

void runDrop2_FromStorage() {
    Serial.println(">>> DROP 2: STORAGE");
    
    // 1. Transfer from Internal to Arms
    moveArm(1, POSE_GRIP_INTERNAL);
    moveArm(2, POSE_GRIP_INTERNAL);
    delay(1000);
    setValve(SUCKER_ARM_1, true); 
    setValve(SUCKER_ARM_2, true);
    delay(500); 
    setValve(SUCKER_INT_1, false); 
    setValve(SUCKER_INT_2, false); 
    delay(500);

    // 3. Drop
    moveArm(1, POSE_PICKUP_EXTERNAL);
    moveArm(2, POSE_PICKUP_EXTERNAL);
    delay(1500); 
    setValve(SUCKER_ARM_1, false); 
    setValve(SUCKER_ARM_2, false);
    delay(500);
    runHoming();
}

// ================================================================
// ================== 7. SETUP & LOOP =============================
// ================================================================

void setup() {
  Serial.begin(115200);
  Serial.println("--- SYSTEME DUAL-MODE + SPLIT ROTATION ---");
  Serial.println("Commandes:");
  Serial.println("  'p'/'P' : Pickup Store / Pickup Hold");
  Serial.println("  'd'/'D' : Drop Arms / Drop Storage");
  Serial.println("  'h'     : Home All");
  Serial.println("  '1'/'2' : Unit 1 TILT / FLAT");
  Serial.println("  '3'/'4' : Unit 2 TILT / FLAT");

  MaestroSerial.begin(9600, SERIAL_8N1, MAESTRO_RX, MAESTRO_TX);
  
  Wire.begin(21, 22); 
  if (!mcp.begin_I2C(0x20)) while(1);
  
  for (int i=0; i<4; i++) {
      mcp.pinMode(VANNES[i], OUTPUT);
      mcp.digitalWrite(VANNES[i], LOW);
  }
  mcp.pinMode(POMPE, OUTPUT);
  mcp.digitalWrite(POMPE, HIGH); 

  for(int i=0; i<8; i++) {
      maestroSetSpeed(i, 20); 
      maestroSetAccel(i, 5); 
  }

  runHoming();
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '\n' || cmd == '\r') return;

    switch(cmd) {
      case 'p': runPickup1_Store(); break;
      case 'P': runPickup2_Hold(); break;
      case 'd': runDrop1_FromArms(); break;
      case 'D': runDrop2_FromStorage(); break;
      case 'h': runHoming(); break;

      // --- INDIVIDUAL ROTATION CONTROL ---
      case '1': rotateInternalStorage(1, true);  break; // Unit 1 TILT
      case '2': rotateInternalStorage(1, false); break; // Unit 1 FLAT
      case '3': rotateInternalStorage(2, true);  break; // Unit 2 TILT
      case '4': rotateInternalStorage(2, false); break; // Unit 2 FLAT
    }
  }
}
