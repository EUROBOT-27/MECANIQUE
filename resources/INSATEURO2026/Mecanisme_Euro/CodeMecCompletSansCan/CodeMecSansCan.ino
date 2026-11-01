#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MCP23X17.h> 
#include "BluetoothSerial.h" 
#include <AccelStepper.h> 

// ================================================================
// ================== 1. CONFIGURATION MATERIEL ===================
// ================================================================

// --- BLUETOOTH ---
BluetoothSerial SerialBT; 

// --- STEPPER (RAIL) ---
#define STEPPER_STEP_PIN   GPIO_NUM_33
#define STEPPER_DIR_PIN    GPIO_NUM_32
#define MAX_SPEED          200.0 
#define ACCELERATION       500.0

// CONFIGURATION DU DEPLACEMENT
#define RAIL_LIMIT         390    
#define BIG_STEP_SIZE      190    // <--- NOUVEAU : Taille du saut (190 pas)

AccelStepper stepper(AccelStepper::DRIVER, STEPPER_STEP_PIN, STEPPER_DIR_PIN);

// --- MAESTRO SERIAL (UART 2) ---
const int MAESTRO_RX_PIN = 16; 
const int MAESTRO_TX_PIN = 17;
HardwareSerial MaestroSerial(2);

// --- PNEUMATIQUE (MCP23X17) ---
Adafruit_MCP23X17 mcp; 

#define MCP_PIN_ARM_SUCKER  7  
#define MCP_PIN_INT_SUCKER  5  
#define MCP_PIN_PUMP        8  

// --- CANAUX MAESTRO ---
#define CH_SHOULDER     4
#define CH_WRIST        5
#define CH_ELBOW        6
#define CH_STORAGE      7

// ================================================================
// ================== 2. POSITIONS (XML) ==========================
// ================================================================

// --- INIT ---
#define POS_INIT_S      2248
#define POS_INIT_W      3999
#define POS_INIT_E      3687
#define POS_INIT_ROT    1815

// --- PICKUP 1 SEQUENCE ---
#define POS_PICK_1_S    3765
#define POS_PICK_1_W    3223
#define POS_PICK_1_E    3687

#define POS_PICK_2_S    3765
#define POS_PICK_2_W    7430
#define POS_PICK_2_E    12810

#define POS_PICK_3_S    4544
#define POS_PICK_3_W    7430
#define POS_PICK_3_E    12810

// --- PICKUP 2 SEQUENCE ---
#define POS_P2_STEP1_S  3765
#define POS_P2_STEP1_W  3223
#define POS_P2_STEP1_E  3687

#define POS_P2_STEP2_S  3765
#define POS_P2_STEP2_W  7430
#define POS_P2_STEP2_E  12810

#define POS_P2_STEP3_S  4544
#define POS_P2_STEP3_W  7430
#define POS_P2_STEP3_E  12810

#define POS_P2_STEP4_S  3219
#define POS_P2_STEP4_W  7430
#define POS_P2_STEP4_E  12810

#define POS_P2_STEP5_S  4155
#define POS_P2_STEP5_W  3531
#define POS_P2_STEP5_E  2517

// --- STORAGE ENTRY ---
#define POS_STOR_1_S    3063
#define POS_STOR_1_W    7430
#define POS_STOR_1_E    12810

#define POS_STOR_2_S    4310
#define POS_STOR_2_W    3843
#define POS_STOR_2_E    2517

#define POS_STOR_3_S    3687
#define POS_STOR_3_W    3531
#define POS_STOR_3_E    2560

#define POS_STOR_4_S    3765
#define POS_STOR_4_W    3223
#define POS_STOR_4_E    3687

// --- DROP 1 (FROM ARMS) ---
#define POS_D1_STEP1_S  4700
#define POS_D1_STEP1_W  3531
#define POS_D1_STEP1_E  2985

#define POS_D1_STEP2_S  3297
#define POS_D1_STEP2_W  7430
#define POS_D1_STEP2_E  12810

#define POS_D1_STEP3_S  4077
#define POS_D1_STEP3_W  7430
#define POS_D1_STEP3_E  12810

// --- DROP 2 (FROM STORAGE) ---
#define POS_ROT_INVERSE 9457
#define POS_DROP_0_S    4934
#define POS_DROP_0_W    3453
#define POS_DROP_0_E    2595

#define POS_DROP_1_S    2985
#define POS_DROP_1_W    3687
#define POS_DROP_1_E    3141

#define POS_DROP_2_S    2673
#define POS_DROP_2_W    3687
#define POS_DROP_2_E    3141

#define POS_DROP_3_S    3219
#define POS_DROP_3_W    3765
#define POS_DROP_3_E    3999
#define POS_DROP_3_ROT  9301

#define POS_DROP_4_S    4077
#define POS_DROP_4_W    7430
#define POS_DROP_4_E    12810
#define POS_DROP_4_ROT  1815

#define POS_DROP_5_S    3765
#define POS_DROP_5_W    7430
#define POS_DROP_5_E    12810
#define POS_DROP_5_ROT  1815

// ================================================================
// ================== 3. FONCTIONS CONTROLE =======================
// ================================================================

void logToAll(String msg) {
    Serial.println(msg);
    SerialBT.println(msg);
}

// --- FONCTIONS STEPPER (RAIL) ---

// Fonction interne pour gérer la sécurité et le mouvement
void executeMove(long steps) {
    long currentPos = stepper.currentPosition();
    long targetPos = currentPos + steps;

    // Sécurité Limites (0 -> 350)
    if (targetPos < 0) {
        logToAll("WARNING: Target < 0. Moving to 0.");
        targetPos = 0; 
    } else if (targetPos > RAIL_LIMIT) {
        logToAll("WARNING: Target > Limit. Moving to " + String(RAIL_LIMIT));
        targetPos = RAIL_LIMIT;
    }

    if (targetPos == currentPos) {
        logToAll("Limit reached. No movement.");
        return;
    }

    logToAll("Rail: Moving to " + String(targetPos));
    
    stepper.moveTo(targetPos);

    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
    
    logToAll("Rail: Done.");
}

// --- LES 2 NOUVELLES FONCTIONS DEMANDEES ---

void moveForward190() {
    logToAll(">>> CMD: Forward 190");
    executeMove(BIG_STEP_SIZE); // +190
}

void moveBackward190() {
    logToAll(">>> CMD: Backward 190");
    executeMove(-BIG_STEP_SIZE); // -190
}

void setZero() {
    stepper.setCurrentPosition(0);
    logToAll(">>> Rail Position Reset to 0.");
}

// --- FONCTIONS MAESTRO ---

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

// --- GESTION DES VALVES & POMPE ---

void updatePump() {
    bool armActive = mcp.digitalRead(MCP_PIN_ARM_SUCKER);
    bool intActive = mcp.digitalRead(MCP_PIN_INT_SUCKER);

    if (armActive || intActive) {
        mcp.digitalWrite(MCP_PIN_PUMP, HIGH);
    } else {
        mcp.digitalWrite(MCP_PIN_PUMP, LOW);
    }
}

void setArmValve(bool state) {
    if(state) {
        mcp.digitalWrite(MCP_PIN_ARM_SUCKER, HIGH); 
        logToAll("   [ARM VALVE] ON");
    } else {
        mcp.digitalWrite(MCP_PIN_ARM_SUCKER, LOW);  
        logToAll("   [ARM VALVE] OFF");
    }
    updatePump(); 
}

void setInternalValve(bool state) {
    if(state) {
        mcp.digitalWrite(MCP_PIN_INT_SUCKER, HIGH); 
        logToAll("   [INT VALVE] ON");
    } else {
        mcp.digitalWrite(MCP_PIN_INT_SUCKER, LOW);  
        logToAll("   [INT VALVE] OFF");
    }
    updatePump(); 
}

// ================================================================
// ================== 4. SEQUENCES OPERATIONNELLES ================
// ================================================================

void init_pos() {
    logToAll(">> EXEC: Init Position");
    maestroSetTarget(CH_SHOULDER, POS_INIT_S);
    maestroSetTarget(CH_WRIST,    POS_INIT_W);
    maestroSetTarget(CH_ELBOW,    POS_INIT_E);
    maestroSetTarget(CH_STORAGE,  POS_INIT_ROT);
    
    setArmValve(false);
    setInternalValve(false);
    // Note: Pompe geree auto par updatePump
    mcp.digitalWrite(MCP_PIN_PUMP, LOW);
    delay(1000);
}

void pickup_1_store_internally() {
    logToAll("--- PHASE 1: PICKUP 1 (STORE INTERNALLY) ---");
    logToAll("1. Moving to Pickup...");
    maestroSetTarget(CH_SHOULDER, POS_PICK_1_S);
    maestroSetTarget(CH_WRIST,    POS_PICK_1_W);
    maestroSetTarget(CH_ELBOW,    POS_PICK_1_E);
    delay(1500); 

    maestroSetTarget(CH_SHOULDER, POS_PICK_2_S);
    maestroSetTarget(CH_WRIST,    POS_PICK_2_W);
    maestroSetTarget(CH_ELBOW,    POS_PICK_2_E);
    delay(1500);

    maestroSetTarget(CH_SHOULDER, POS_PICK_3_S);
    maestroSetTarget(CH_WRIST,    POS_PICK_3_W);
    maestroSetTarget(CH_ELBOW,    POS_PICK_3_E);
    setArmValve(true); 
    delay(1500);

    logToAll("2. Moving to Storage...");
    maestroSetTarget(CH_SHOULDER, POS_STOR_1_S);
    maestroSetTarget(CH_WRIST,    POS_STOR_1_W);
    maestroSetTarget(CH_ELBOW,    POS_STOR_1_E);
    delay(1500);

    maestroSetTarget(CH_SHOULDER, POS_STOR_2_S);
    maestroSetTarget(CH_WRIST,    POS_STOR_2_W);
    maestroSetTarget(CH_ELBOW,    POS_STOR_2_E);
    delay(1500);

    maestroSetTarget(CH_SHOULDER, POS_STOR_3_S);
    maestroSetTarget(CH_WRIST,    POS_STOR_3_W);
    maestroSetTarget(CH_ELBOW,    POS_STOR_3_E);
    delay(1500);

    logToAll("3. HANDOFF...");
    setInternalValve(true);  
    delay(2000);              
    setArmValve(false);      
    
    maestroSetTarget(CH_SHOULDER, POS_STOR_4_S);
    maestroSetTarget(CH_WRIST,    POS_STOR_4_W);
    maestroSetTarget(CH_ELBOW,    POS_STOR_4_E);
    delay(2000);
    logToAll("   [STATUS] 2 Objets Stockes.");
}

void pickup_2_active_hold() {
    logToAll("--- PHASE 1: PICKUP 2 (ACTIVE HOLD) ---");
    logToAll("1. Approach...");
    maestroSetTarget(CH_SHOULDER, POS_P2_STEP1_S);
    maestroSetTarget(CH_WRIST,    POS_P2_STEP1_W);
    maestroSetTarget(CH_ELBOW,    POS_P2_STEP1_E);
    maestroSetTarget(CH_STORAGE,  POS_INIT_ROT);
    delay(1500);

    logToAll("2. Lowering...");
    maestroSetTarget(CH_SHOULDER, POS_P2_STEP2_S);
    maestroSetTarget(CH_WRIST,    POS_P2_STEP2_W);
    maestroSetTarget(CH_ELBOW,    POS_P2_STEP2_E);
    delay(1500);

    logToAll("3. Grabbing...");
    maestroSetTarget(CH_SHOULDER, POS_P2_STEP3_S);
    maestroSetTarget(CH_WRIST,    POS_P2_STEP3_W);
    maestroSetTarget(CH_ELBOW,    POS_P2_STEP3_E);
    setArmValve(true); 
    delay(1500);

    logToAll("4. Lifting...");
    maestroSetTarget(CH_SHOULDER, POS_P2_STEP4_S);
    maestroSetTarget(CH_WRIST,    POS_P2_STEP4_W);
    maestroSetTarget(CH_ELBOW,    POS_P2_STEP4_E);
    delay(1500);

    logToAll("5. Holding...");
    maestroSetTarget(CH_SHOULDER, POS_P2_STEP5_S);
    maestroSetTarget(CH_WRIST,    POS_P2_STEP5_W);
    maestroSetTarget(CH_ELBOW,    POS_P2_STEP5_E);
    delay(1500);
    logToAll("   [STATUS] Capacity FULL.");
}

void drop_1_from_arms() {
    logToAll("--- PHASE 2: DROP 1 (FROM ARMS) ---");
    logToAll("1. Drop Position...");
    maestroSetTarget(CH_SHOULDER, POS_D1_STEP1_S);
    maestroSetTarget(CH_WRIST,    POS_D1_STEP1_W);
    maestroSetTarget(CH_ELBOW,    POS_D1_STEP1_E);
    maestroSetTarget(CH_STORAGE,  POS_INIT_ROT);
    delay(1500);

    logToAll("2. RELEASING...");
    setArmValve(true); 
    delay(1000);

    logToAll("3. Retracting...");
    maestroSetTarget(CH_SHOULDER, POS_D1_STEP2_S);
    maestroSetTarget(CH_WRIST,    POS_D1_STEP2_W);
    maestroSetTarget(CH_ELBOW,    POS_D1_STEP2_E);
    delay(1500);
    setArmValve(false); 
    
    logToAll("4. Backing off...");
    maestroSetTarget(CH_SHOULDER, POS_D1_STEP3_S);
    maestroSetTarget(CH_WRIST,    POS_D1_STEP3_W);
    maestroSetTarget(CH_ELBOW,    POS_D1_STEP3_E);
    delay(1500);
    logToAll("   [STATUS] Arms Empty.");
}

void drop_2_from_storage() {
    logToAll("--- PHASE 2: DROP 2 (FROM STORAGE) ---");
    logToAll("0. Safety/Prep...");
    maestroSetTarget(CH_SHOULDER, POS_DROP_0_S);
    maestroSetTarget(CH_WRIST,    POS_DROP_0_W);
    maestroSetTarget(CH_ELBOW,    POS_DROP_0_E);
    delay(1500);

    logToAll("1. Rotating Internal...");
    maestroSetTarget(CH_STORAGE, POS_ROT_INVERSE);
    delay(1500);

    logToAll("2. Retrieving...");
    maestroSetTarget(CH_SHOULDER, POS_DROP_1_S); 
    maestroSetTarget(CH_WRIST,    POS_DROP_1_W);
    maestroSetTarget(CH_ELBOW,    POS_DROP_1_E);
    delay(1500);

    maestroSetTarget(CH_SHOULDER, POS_DROP_2_S); 
    maestroSetTarget(CH_WRIST,    POS_DROP_2_W);
    maestroSetTarget(CH_ELBOW,    POS_DROP_2_E);
    setArmValve(true);       
    delay(1000);
    setInternalValve(false); 
    delay(1500);

    logToAll("3. Dropping...");
    maestroSetTarget(CH_SHOULDER, POS_DROP_3_S);
    maestroSetTarget(CH_WRIST,    POS_DROP_3_W);
    maestroSetTarget(CH_ELBOW,    POS_DROP_3_E);
    maestroSetTarget(CH_STORAGE,  POS_DROP_3_ROT);
    delay(1500);

    maestroSetTarget(CH_SHOULDER, POS_DROP_4_S);
    maestroSetTarget(CH_WRIST,    POS_DROP_4_W);
    maestroSetTarget(CH_ELBOW,    POS_DROP_4_E);
    maestroSetTarget(CH_STORAGE,  POS_DROP_4_ROT);
    delay(1500);

    setArmValve(false); 
    logToAll("   [DROP] Object released.");

    maestroSetTarget(CH_SHOULDER, POS_DROP_5_S);
    maestroSetTarget(CH_WRIST,    POS_DROP_5_W);
    maestroSetTarget(CH_ELBOW,    POS_DROP_5_E);
    maestroSetTarget(CH_STORAGE,  POS_DROP_5_ROT);
    delay(1500);
    logToAll("   [STATUS] Systeme Vide.");
}

// Fonction centrale pour traiter les commandes (USB ou BT)
void processCommand(char cmd) {
    if(cmd == '\n' || cmd == '\r') return;

    switch(cmd) {
        // --- NOUVELLES COMMANDES STEPPER (RAIL) ---
        case '+': moveForward190(); break;   // <--- Appelle la fonction +190
        case '-': moveBackward190(); break;  // <--- Appelle la fonction -190
        
        case 'Z': // Reset position rail
        case 'z': setZero(); break;

        // --- COMMANDES BRAS ROBOT ---
        case '1': pickup_1_store_internally(); break;
        case '2': pickup_2_active_hold(); break;
        case '3': drop_1_from_arms(); break;
        case '4': drop_2_from_storage(); break;
        case 'i': init_pos(); break;
        default:  logToAll("Cmd inconnue."); break;
    }
}

// ================================================================
// ================== 5. SETUP & LOOP =============================
// ================================================================

void setup() {
    Serial.begin(115200);

    // --- SETUP BLUETOOTH ---
    SerialBT.begin("ESP32_Robot_Maestro"); 
    Serial.println("Bluetooth Initialise! Connectez-vous a 'ESP32_Robot_Maestro'");

    // --- SETUP STEPPER ---
    stepper.setMaxSpeed(MAX_SPEED);
    stepper.setAcceleration(ACCELERATION);
    
    // ====================================================
    // SOLUTION LOGICIELLE POUR INVERSER LA DIRECTION ICI :
    // ====================================================
    stepper.setPinsInverted(true, false, false); 
    
    stepper.setCurrentPosition(0); 

    // 1. Init MCP23X17
    Serial.println("Initialisation MCP23X17...");
    if (!mcp.begin_I2C()) { 
        Serial.println("ERREUR: MCP23X17 introuvable.");
        while (1); 
    }
    
    mcp.pinMode(MCP_PIN_ARM_SUCKER, OUTPUT);
    mcp.pinMode(MCP_PIN_INT_SUCKER, OUTPUT);
    mcp.pinMode(MCP_PIN_PUMP, OUTPUT);
    
    mcp.digitalWrite(MCP_PIN_ARM_SUCKER, LOW);
    mcp.digitalWrite(MCP_PIN_INT_SUCKER, LOW);
    mcp.digitalWrite(MCP_PIN_PUMP, LOW);

    // 2. Init Maestro
    Serial.println("Initialisation Maestro...");
    MaestroSerial.begin(9600, SERIAL_8N1, MAESTRO_RX_PIN, MAESTRO_TX_PIN);

    maestroSetSpeed(CH_SHOULDER, 50); maestroSetAccel(CH_SHOULDER, 50);
    maestroSetSpeed(CH_WRIST,    50); maestroSetAccel(CH_WRIST,    50);
    maestroSetSpeed(CH_ELBOW,     0); maestroSetAccel(CH_ELBOW,     0);
    maestroSetSpeed(CH_STORAGE,  72); maestroSetAccel(CH_STORAGE,  50);

    Serial.println("=== SYSTEME COMPLET PRET ===");
    init_pos();
}

void loop() {
    if (Serial.available()) {
        processCommand(Serial.read());
    }
    if (SerialBT.available()) {
        processCommand(SerialBT.read());
    }
}
