#include <Arduino.h>

// ================================================================
// ================== 1. CONFIGURATION DU MATERIEL ================
// ================================================================

// --- MAESTRO (UART DIRECT) ---
// RX ESP (16) <--> TX Maestro
// TX ESP (17) <--> RX Maestro
const gpio_num_t MAESTRO_RX = GPIO_NUM_16;  
const gpio_num_t MAESTRO_TX = GPIO_NUM_17;  
HardwareSerial MaestroSerial(2); 

// --- CANAUX MAESTRO ---
#define CH_ARM1_SHOULDER   0
#define CH_ARM1_ELBOW      1
#define CH_ARM1_WRIST      2
#define CH_ARM2_SHOULDER   3
#define CH_ARM2_ELBOW      4
#define CH_ARM2_WRIST      5

// ================================================================
// ================== 2. VALEURS DE CALIBRATION ===================
// ================================================================
// Conversion : Valeur Photo * 4

// ------------------- BRAS 1 (ARM 1) -------------------

// 1. PICKUP (D'après vos photos)
#define A1_PICK_S  3843   // (960.75 * 4)
#define A1_PICK_E  10549  // (2637.25 * 4)
#define A1_PICK_W  7196   // (1799.00 * 4)

// 2. INTERNAL (D'après vos photos)
#define A1_INT_S   3375   // (843.75 * 4)
#define A1_INT_E   2595   // (648.75 * 4)
#define A1_INT_W   1035   // (258.75 * 4)

// 3. DROP (COPIE DE PICKUP)
#define A1_DROP_S  A1_PICK_S
#define A1_DROP_E  A1_PICK_E
#define A1_DROP_W  A1_PICK_W


// ------------------- BRAS 2 (ARM 2) -------------------

// 1. PICKUP (D'après vos photos)
#define A2_PICK_S  4077   // (1019.25 * 4)
#define A2_PICK_E  9301   // (2325.25 * 4)
#define A2_PICK_W  7897   // (1974.25 * 4)

// 2. INTERNAL (D'après vos photos)
#define A2_INT_S   3219   // (804.75 * 4)
#define A2_INT_E   2595   // (648.75 * 4)
#define A2_INT_W   2829   // (707.25 
```* 4)

// 3. DROP (COPIE DE PICKUP)
#define A2_DROP_S  A2_PICK_S
#define A2_DROP_E  A2_PICK_E
#define A2_DROP_W  A2_PICK_W


// Enumération des positions
enum ArmPose {
    POSE_PICKUP,    // Bras étendu (pour prendre ou poser)
    POSE_INTERNAL   // Bras rentré (Home / Stockage)
};

// ================================================================
// ================== 3. GESTION MAESTRO ==========================
// ================================================================

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

// Fonction de mouvement
void moveArm(int armID, ArmPose pose) {
    int tS, tE, tW; // Cibles

    if (armID == 1) {
        switch (pose) {
            case POSE_PICKUP:   tS = A1_PICK_S; tE = A1_PICK_E; tW = A1_PICK_W; break;
            case POSE_INTERNAL: tS = A1_INT_S;  tE = A1_INT_E;  tW = A1_INT_W;  break;
        }
        maestroSetTarget(CH_ARM1_SHOULDER, tS);
        maestroSetTarget(CH_ARM1_ELBOW,    tE);
        maestroSetTarget(CH_ARM1_WRIST,    tW);
    } 
    else if (armID == 2) {
        switch (pose) {
            case POSE_PICKUP:   tS = A2_PICK_S; tE = A2_PICK_E; tW = A2_PICK_W; break;
            case POSE_INTERNAL: tS = A2_INT_S;  tE = A2_INT_E;  tW = A2_INT_W;  break;
        }
        maestroSetTarget(CH_ARM2_SHOULDER, tS);
        maestroSetTarget(CH_ARM2_ELBOW,    tE);
        maestroSetTarget(CH_ARM2_WRIST,    tW);
    }
}

// ================================================================
// ================== 4. SEQUENCES ================================
// ================================================================

void runHome() {
    Serial.println(">>> HOME (INTERNAL)");
    moveArm(1, POSE_INTERNAL);
    moveArm(2, POSE_INTERNAL);
}

void runPickupDrop() {
    Serial.println(">>> EXTENSION (PICKUP / DROP)");
    moveArm(1, POSE_PICKUP);
    moveArm(2, POSE_PICKUP);
}

void runDemo() {
    // Séquence de test automatique
    Serial.println("--- DEMO CYCLE ---");
    
    Serial.println("1. Extension (Pickup/Drop)...");
    moveArm(1, POSE_PICKUP);
    moveArm(2, POSE_PICKUP);
    delay(2000); 

    Serial.println("2. Retrait (Internal)...");
    moveArm(1, POSE_INTERNAL);
    moveArm(2, POSE_INTERNAL);
    delay(2000);
    
    Serial.println("--- FIN CYCLE ---");
}

// ================================================================
// ================== 5. MAIN SETUP ===============================
// ================================================================

void setup() {
  Serial.begin(115200);
  Serial.println("--- SYSTEME 2 BRAS (PICKUP = DROP) ---");

  MaestroSerial.begin(9600, SERIAL_8N1, MAESTRO_RX, MAESTRO_TX);
  
  // Paramètres de sécurité (Vitesse)
  for(int i=0; i<6; i++) {
      maestroSetSpeed(i, 20); // Vitesse LENTE pour tester
      maestroSetAccel(i, 5); 
  }

  runHome();

  Serial.println("Commandes :");
  Serial.println("'e' -> Etendre (Pickup/Drop)");
  Serial.println("'i' -> Interne (Home)");
  Serial.println("'d' -> Demo automatique");
}

// ================================================================
// ================== 6. MAIN LOOP ================================
// ================================================================

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '\n' || cmd == '\r') return;

    switch(cmd) {
      case 'e': runPickupDrop(); break;
      case 'i': runHome(); break;
      case 'd': runDemo(); break;
      default: Serial.println("?"); break;
    }
  }
}
