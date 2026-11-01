#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Wire.h>
#include <Adafruit_MCP23X17.h>
#include <AccelStepper.h>
#include <stdarg.h>

// ================== CONFIGURATION ==================

// --- BLE ---
#define BLE_NAME        "ESP32-Mecanisme"
#define SERVICE_UUID    "7c2f4b10-8a6d-4c0f-9d2c-3efb5e7d1a01"
#define CONTROL_UUID    "7c2f4b11-8a6d-4c0f-9d2c-3efb5e7d1a01"
#define STATUS_UUID     "7c2f4b12-8a6d-4c0f-9d2c-3efb5e7d1a01"

// --- MAESTRO SERVO ---
#define MAESTRO_RX       16
#define MAESTRO_TX       17
#define MAESTRO_BAUD     9600

// --- MCP23017 (Pump & Valves) ---
#define MCP_ADDR         0x20
#define PIN_PUMP         8
// Map Valve 1-6 based on PROVEN CODE {0, 1, 2, 3, 4, 5}
const uint8_t VALVE_PINS[] = {0, 1, 2, 3, 4, 5}; 
const int NB_VANNES = 6;

// --- STEPPER (DRV8825 - Integrated) ---
#define STEPPER_STEP_PIN   GPIO_NUM_33
#define STEPPER_DIR_PIN    GPIO_NUM_32

#define MAX_SPEED          1000.0  
#define ACCELERATION       500.0   

// Presets from functional code
#define POS_PICKUP         2000    
#define POS_DROP           4000    
#define RAIL_MAX_POS       5000 
#define CMD_QUEUE_LEN      8
#define CMD_BUF_LEN        96

// ================== GLOBALS ==================

HardwareSerial Maestro(1);
Adafruit_MCP23X17 mcp;
AccelStepper stepper(AccelStepper::DRIVER, STEPPER_STEP_PIN, STEPPER_DIR_PIN);

BLECharacteristic *pStatusCharacteristic;
bool deviceConnected = false;
bool mcpFound = false;
QueueHandle_t cmdQueue = nullptr;

struct CmdMessage {
  char text[CMD_BUF_LEN];
};

// ================== FUNCTIONS ==================

void notifyClient(const String& msg) {
  if (deviceConnected && pStatusCharacteristic) {
    pStatusCharacteristic->setValue(msg.c_str());
    pStatusCharacteristic->notify();
  }
  Serial.println("STATUS: " + msg);
}

void notifyClientf(const char *fmt, ...) {
  char buf[CMD_BUF_LEN];
  va_list args;
  va_start(args, fmt);
  vsnprintf(buf, sizeof(buf), fmt, args);
  va_end(args);
  notifyClient(String(buf));
}

long clampRailPosition(long pos) {
  if (pos < 0) return 0;
  if (pos > RAIL_MAX_POS) return RAIL_MAX_POS;
  return pos;
}

// --- MCP ACTIONS ---
void stopAllPumpValves() {
  if (!mcpFound) return;
  mcp.digitalWrite(PIN_PUMP, HIGH); // PROVEN CODE: HIGH is OFF (Safety)
  for(int i=0; i<NB_VANNES; i++) {
    mcp.digitalWrite(VALVE_PINS[i], LOW); // PROVEN CODE: LOW is OFF
  }
  notifyClient("MCP: ALL STOPPED");
}

// --- STEPPER ACTIONS ---
void resetStepperPosition() {
  stepper.setCurrentPosition(0);
  notifyClient("STEP: Position Zeroed");
}

void moveStepper(long pos) {
  const long target = clampRailPosition(pos);
  if (target != pos) {
    notifyClientf("STEP: Clamped to %ld", target);
  }
  notifyClient("STEP: Moving to " + String(target));
  stepper.moveTo(target);
}

void stopSystem() {
  stepper.stop();
  stepper.moveTo(stepper.currentPosition());
  stopAllPumpValves();
  notifyClient("SYSTEM STOP");
}

// --- MAESTRO ---
void setServo(int ch, int us) {
  int target = us * 4; 
  Maestro.write(0x84);
  Maestro.write(ch);
  Maestro.write(target & 0x7F);
  Maestro.write((target >> 7) & 0x7F);
  // notifyClient("SRV: " + String(ch) + "->" + String(us)); // Too verbose for sliders
}


// --- PARSER ---
void processCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd.length() == 0) return;
  
  Serial.println("CMD: " + cmd);

  // SERVO: "C<ch> <us>" e.g. "C0 1500"
  if (cmd.startsWith("C")) {
     int space = cmd.indexOf(' ');
     if (space > 0) {
        int ch = cmd.substring(1, space).toInt();
        int val = cmd.substring(space+1).toInt();
        if (ch >= 0 && ch <= 11 && val >= 0 && val <= 4096) {
          setServo(ch, val);
        } else {
          notifyClient("ERR: Invalid servo command");
        }
     }
  }
  // MCP ACTIONS
  else if (cmd == "S" || cmd == "STOP") { stopSystem(); }
  else if (cmd == "PUMP:ON")  { if(mcpFound) mcp.digitalWrite(PIN_PUMP, LOW); notifyClient("Pump ON"); } // Active LOW
  else if (cmd == "PUMP:OFF") { if(mcpFound) mcp.digitalWrite(PIN_PUMP, HIGH); notifyClient("Pump OFF"); } // Active HIGH

  // Direct Valve Controls: V<num>:<0|1> e.g. V0:1, V5:0
  else if (cmd.startsWith("V")) {
    int colon = cmd.indexOf(':');
    if (colon > 1) {
      int vIdx = cmd.substring(1, colon).toInt();
      int state = cmd.substring(colon+1).toInt();
      if (mcpFound && vIdx >= 0 && vIdx < NB_VANNES) {
        uint8_t mcpPin = VALVE_PINS[vIdx];
        mcp.digitalWrite(mcpPin, state ? HIGH : LOW);
        Serial.printf("MCP_VALVE: %d (Pin %d) set to %d\n", vIdx, mcpPin, state);
        notifyClient("V" + String(vIdx) + (state ? " ON" : " OFF"));
      } else {
        Serial.printf("E: Valve %d invalid\n", vIdx);
      }
    }
  }
  
  // STEPPER ACTIONS (From Functional Code)
  else if (cmd == "P") { moveStepper(POS_PICKUP); }
  else if (cmd == "D") { moveStepper(POS_DROP); }
  else if (cmd == "Z" || cmd == "SZ") { moveStepper(0); }
  else if (cmd == "F") { moveStepper(stepper.currentPosition() + 500); }
  else if (cmd == "B") { moveStepper(stepper.currentPosition() - 500); }
  else if (cmd == "H") { resetStepperPosition(); }
  else if (cmd == "SKIP_HOME") { notifyClient("STEP: Virtual Home Set"); }
  else if (cmd.startsWith("SM")) {
     int space = cmd.indexOf(' ');
     if (space > 0) {
       moveStepper(cmd.substring(space+1).toInt());
     }
   }
  else {
    notifyClient("ERR: Unknown command");
  }
}

// ================== SETUP & LOOP ==================

class ServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("BLE Connected");
    };
    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("BLE Disconnected");
      BLEDevice::startAdvertising();
    }
};

class CharCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pC) {
      String val = pC->getValue();
      if (val.length() > 0 && cmdQueue) {
        CmdMessage msg{};
        const size_t copyLen = val.length() < (CMD_BUF_LEN - 1) ? val.length() : (CMD_BUF_LEN - 1);
        memcpy(msg.text, val.c_str(), copyLen);
        msg.text[copyLen] = '\0';
        if (xQueueSend(cmdQueue, &msg, 0) != pdTRUE) {
          notifyClient("ERR: Command queue full");
        }
      }
    }
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- ESP32 Mecanisme (BLE + NO BUMPER MODE) ---");
  Serial.println("WARNING: Position 0 is where the robot started.");
  Serial.println("Serial monitor baud: 115200");
  cmdQueue = xQueueCreate(CMD_QUEUE_LEN, sizeof(CmdMessage));
  
  // 1. Maestro
  Maestro.begin(MAESTRO_BAUD, SERIAL_8N1, MAESTRO_RX, MAESTRO_TX);
  
  // 2. MCP
  Wire.begin(); 
  if (!mcp.begin_I2C(MCP_ADDR)) {
    Serial.println("CRITICAL ERR: MCP23017 not found!");
    mcpFound = false;
  } else {
    Serial.println("MCP23017 Ready.");
    mcpFound = true;
    mcp.pinMode(PIN_PUMP, OUTPUT);
    for(int i=0; i<NB_VANNES; i++) {
        mcp.pinMode(VALVE_PINS[i], OUTPUT);
    }
    stopAllPumpValves(); // Safety Init (Pump HIGH, Valves LOW)
  }
  
  // 3. Stepper (DRV8825 Config from Functional Code)
  stepper.setMaxSpeed(MAX_SPEED);
  stepper.setAcceleration(ACCELERATION);
  
  // 4. BLE
  BLEDevice::init(BLE_NAME);
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);
  BLECharacteristic *pControl = pService->createCharacteristic(
                                  CONTROL_UUID, 
                                  BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
                                );
  pControl->setCallbacks(new CharCallbacks());
  pStatusCharacteristic = pService->createCharacteristic(
                            STATUS_UUID,
                            BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
                          );
  pStatusCharacteristic->addDescriptor(new BLE2902());
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  BLEDevice::startAdvertising();
  
  Serial.println("BLE Ready. Advertising as: " + String(BLE_NAME));
  Serial.println("System Ready.");
}

void loop() {
  // 1. Handle queued BLE commands in the main loop task.
  CmdMessage msg{};
  while (cmdQueue && xQueueReceive(cmdQueue, &msg, 0) == pdTRUE) {
    processCommand(String(msg.text));
  }
  
  // 2. Run Stepper
  stepper.run();

  // 3. Periodic Debug (Optional: Every 2 seconds if moving)
  static unsigned long lastDebug = 0;
  if (millis() - lastDebug > 2000 && stepper.distanceToGo() != 0) {
    lastDebug = millis();
    Serial.printf("DEBUG: Pos:%ld, Target:%ld, Speed:%.2f\n", 
                  stepper.currentPosition(), stepper.targetPosition(), stepper.speed());
  }
}
