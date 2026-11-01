#include <Wire.h>
#include <Adafruit_MCP23X17.h>

Adafruit_MCP23X17 mcp;

// ================== CONFIG ==================
// Pump Pin 
const int POMPE = 8; 

const int VANNES[] = {7, 6, 5, 4, 3, 2}; 
const int NB_VANNES = sizeof(VANNES) / sizeof(VANNES[0]); 

// ============================================

void setup() {
  Serial.begin(115200);

  if (!mcp.begin_I2C(0x20)) {
    Serial.println("Erreur : MCP23017 non trouve !");
    while (1);
  }

  // --- Configuration des sorties ---
  mcp.pinMode(POMPE, OUTPUT);
  mcp.digitalWrite(POMPE, HIGH);
  
  for (int i = 0; i < NB_VANNES; i++) {
    mcp.pinMode(VANNES[i], OUTPUT);
  }

  // --- État de sécurité au démarrage ---
  stopAll();

  Serial.println("=================================");
  Serial.println("   SYSTEME 6 VENTOUSES (SUCKERS) ");
  Serial.println("=================================");
  Serial.println("ON     OFF    |  DESCRIPTION");
  Serial.println("--------------|--------------");
  Serial.println("'1'    'a'    |  Sucker 1 (Pin 7)");
  Serial.println("'2'    'b'    |  Sucker 2 (Pin 6)");
  Serial.println("'3'    'c'    |  Sucker 3 (Pin 5)");
  Serial.println("'4'    'd'    |  Sucker 4 (Pin 4)");
  Serial.println("'5'    'e'    |  Sucker 5 (Pin 3)");
  Serial.println("'6'    'f'    |  Sucker 6 (Pin 2)");
  Serial.println("--------------|--------------");
  Serial.println("'P'    'p'    |  POMPE MAIN");
  Serial.println("'Z'           |  STOP URGENCE");
  Serial.println("=================================");
}

// ================== CORE FUNCTIONS ==================

// Function to control a specific valve
void setSucker(int index, bool state) {
  if(index >= 0 && index < NB_VANNES) {
    mcp.digitalWrite(VANNES[index], state ? HIGH : LOW);
    Serial.print("Sucker "); Serial.print(index + 1);
    Serial.println(state ? " ON" : " OFF");
  }
}

// Function to control the pump
void setPump(bool state) {
  // Assuming Relay Logic: LOW = ON, HIGH = OFF
  // Change this if your relay works differently
  mcp.digitalWrite(POMPE, state ? LOW : HIGH); 
  Serial.println(state ? "Pump ON" : "Pump OFF");
}

void stopAll() {
  setPump(false); // Turn Pump OFF
  
  for (int i = 0; i < NB_VANNES; i++) {
    mcp.digitalWrite(VANNES[i], LOW); // All valves Closed
  }
  Serial.println("!!! STOP URGENCE / RESET !!!");
}

// ================== LOOP ==================

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == '\n' || cmd == '\r') return;

    // Note: We removed toupper() to distinguish between 'A' and 'a' if needed,
    // but here we use numbers for ON and letters for OFF.
    
    switch (cmd) {
      // --- ON COMMANDS (1-6) ---
      case '1': setSucker(0, true); break;
      case '2': setSucker(1, true); break;
      case '3': setSucker(2, true); break;
      case '4': setSucker(3, true); break;
      case '5': setSucker(4, true); break;
      case '6': setSucker(5, true); break;

      // --- OFF COMMANDS (a-f) ---
      case 'a': setSucker(0, false); break;
      case 'b': setSucker(1, false); break;
      case 'c': setSucker(2, false); break;
      case 'd': setSucker(3, false); break;
      case 'e': setSucker(4, false); break;
      case 'f': setSucker(5, false); break;

      // --- PUMP COMMANDS ---
      case 'P': setPump(true);  break; // Pump ON
      case 'p': setPump(false); break; // p minus: Pump OFF 

      // --- SAFETY ---
      case 'Z': // Emergency Stop
      case 'z': 
        stopAll();
        break;
    }
  }
}
