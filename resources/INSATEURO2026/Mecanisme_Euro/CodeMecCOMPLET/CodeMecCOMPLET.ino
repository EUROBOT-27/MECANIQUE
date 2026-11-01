#include <Arduino.h>
#include <Wire.h>
#include "BluetoothSerial.h" 
#include "driver/twai.h" 
#include <AccelStepper.h> 

// ================================================================
// ================== 1. HARDWARE CONFIGURATION ===================
// ================================================================

BluetoothSerial SerialBT; 

// CAN Bus Pins
#define CAN_RX_PIN  GPIO_NUM_16  
#define CAN_TX_PIN  GPIO_NUM_17  
#define CAN_CMD_ID          0x100  
#define CAN_RESP_ID         0x103  
#define CAN_MSG_DONE        0xAA

// Stepper Pins (GPIO 25/26 to avoid I2C conflict)
#define STEPPER_STEP_PIN    GPIO_NUM_26  
#define STEPPER_DIR_PIN     GPIO_NUM_25  
#define MAX_SPEED           1200.0   
#define ACCELERATION        1500.0  
#define HOMING_SPEED        3000.0    // Vitesse plus lente pour éviter les chocs
#define HOMING_ACCEL        3000.0
#define RAIL_LIMIT          1560    
#define BIG_STEP_SIZE       400 
#define BIG_STEP_SIZE1      1000
#define BIG_STEP_SIZE3      1400

AccelStepper stepper(AccelStepper::DRIVER, STEPPER_STEP_PIN, STEPPER_DIR_PIN);

// Maestro Serial Pins (Mapped to SDA/SCL)
const int MAESTRO_TX_PIN = 22; // SDA
const int MAESTRO_RX_PIN = 21; // SCL
HardwareSerial MaestroSerial(2);

// Valve & Pump Pins
#define VALVE_PIN_ARM1_SUCKER  GPIO_NUM_27  
#define VALVE_PIN_INT1_SUCKER  GPIO_NUM_12  
#define VALVE_PIN_ARM2_SUCKER  GPIO_NUM_13  
#define VALVE_PIN_INT2_SUCKER  GPIO_NUM_14  
#define VALVE_PIN_PUMP         GPIO_NUM_32  

#define BUMPER_PIN          GPIO_NUM_33

// Maestro Channels & Positions
#define CH_A1_STORAGE      0
#define CH_A2_STORAGE      8 
#define CH_Curseur_Yellow  1
#define CH_Curseur_Blue    3 
#define POS_ROT_NORMAL_1     2768
#define POS_ROT_NORMAL_2     1856 
#define POS_ROT_INVERSE_1    9984
#define POS_ROT_INVERSE_2    9890 


// Pump State Tracking
bool arm1_open = false;
bool arm2_open = false;
bool int1_open = false;
bool int2_open = false;

// ================================================================
// ================== VARIABLES DUAL-CORE =========================
// ================================================================
TaskHandle_t StepperTask;
volatile bool isHoming = false; // Sécurité pour reprendre la main (Homing & MoveTo)


// ================================================================
// ================== 2. XML FRAMES (VERIFIED) ====================
// ================================================================

#define FRAME_INIT                       2624, 3613, 3706, 4042, 3305, 2954,   50, 80, 0, 50, 0, 20,    50, 80, 0, 50, 0, 20
#define FRAME_PICK_UP_1                  4800, 7219, 10112, 7615, 9792, 4758,  20, 80, 0, 80, 0, 20,    20, 80, 0, 80, 0, 20
#define FRAME_STORE_1                    3524, 3293, 2883, 3256, 3224, 3743,   15, 0, 0, 0, 0, 12,      15, 0, 0, 0, 0, 12
#define FRAME_PICK_UP_2                  4560, 7500, 10112, 7597, 9792, 4820,  10, 70, 0, 70, 80, 10,   80, 70, 0, 70, 0, 80
#define FRAME_STORE_2                    4151, 2366, 3365, 2411, 3752, 4232,   20, 0, 80, 0, 80, 20,    20, 80, 0, 80, 0, 20
#define FRAME_PICK_DOWN_2                4542, 7219, 10112, 7597, 9792, 4635,   5, 0, 120, 0, 100, 5,    0, 0, 0, 0, 0, 0
#define FRAME_OFF                        4190, 9512, 10112, 9634, 9680, 4232,   10, 0, 0, 0, 80, 10,     80, 0, 0, 0, 0, 80
#define FRAME_ARM_2_OFF                  4542, 7219, 10112, 8469, 9792, 4420,   5, 0, 120, 0, 100, 5,    0, 0, 0, 0, 0, 0
#define FRAME_PICK_AFTER_FLIP            2742, 3245, 3516, 3304, 3379, 3100,   20, 0, 0, 0, 0, 10,      20, 0, 0, 0, 0, 10
#define FRAME_PICK_DOWN_AFTER_FLIP       4774, 7219, 10112, 7597, 9792, 4984,   30, 80, 0, 80, 0, 20,    0, 80, 0, 80, 0, 0
#define FRAME_PICK_AFTER_INT_1_FLIPPED   2742, 3245, 3516, 2916, 3224, 3643,   20, 0, 0, 0, 70, 20,     20, 0, 0, 80, 0, 20
#define FRAME_PICK_DOWN_INT_1_FLIPPED    4774, 7219, 10112, 7597, 9792, 5244,   30, 80, 0, 80, 0, 10,    0, 80, 0, 80, 0, 10
#define FRAME_PICK_AFTER_INT_2_FLIPPED   2976, 2671, 3141, 3304, 3379, 3130,   10, 0, 0, 0, 0, 10,      10, 0, 0, 0, 0, 10
#define FRAME_PICK_DOWN_INT_2_FLIPPED    4860, 7219, 10112, 7596, 9792, 4830,   20, 0, 0, 80, 0, 20,     20, 0, 0, 80, 0, 10


// ================================================================
// ================== 3. UTILS & CAN ==============================
// ================================================================

void logToAll(String msg) {
    Serial.println(msg);
    SerialBT.println(msg);
}

void setupCAN() {
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
    g_config.rx_queue_len = 20; 
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) twai_start();
}

void sendCANStatus(uint8_t status_code) {
    twai_message_t message;
    message.identifier = CAN_RESP_ID;
    message.extd = 0;
    message.data_length_code = 1;
    message.data[0] = status_code;
    twai_transmit(&message, pdMS_TO_TICKS(100));
}

// CORRECTION DUAL-CORE : Sécurisation de la commande moveTo
void executeMove(long steps) {
    long targetPos = constrain(stepper.currentPosition() + steps, 0, RAIL_LIMIT);
    if (targetPos != stepper.currentPosition()) {
        logToAll("Rail: Move to " + String(targetPos));
        
        // On bloque très brièvement le Core 0 pour éviter un crash mémoire
        isHoming = true;
        delay(2); 
        
        stepper.moveTo(targetPos);
        
        // On libère le Core 0 pour qu'il fasse tourner le moteur
        isHoming = false; 
    }
}

void waitForRail(unsigned long timeout_ms = 8000) {
    unsigned long start = millis();
    // On attend simplement que la distance arrive à zéro
    while (stepper.distanceToGo() != 0) {
        if (millis() - start > timeout_ms) break; // Sécurité anti-blocage
        delay(1); // Laisse le processeur respirer pendant l'attente
    }
}

void moveForward100() { executeMove(BIG_STEP_SIZE); }
void moveBackward100() { executeMove(-BIG_STEP_SIZE); }
void moveForward250() { executeMove(BIG_STEP_SIZE1); }
void moveBackward250() { executeMove(-BIG_STEP_SIZE1); }
void moveForward350() { executeMove(BIG_STEP_SIZE3); }
void moveBackward350() { executeMove(-BIG_STEP_SIZE3); }

void homeRail() {
    Serial.println("=== DEBUT DU HOMING ===");
    
    // 1. On bloque la tâche du Core 0 pour prendre le contrôle manuel
    isHoming = true;
    delay(10); // On laisse 10ms au Core 0 pour voir la variable et se mettre en pause
    
    // 2. Reduce speed for homing
    stepper.setMaxSpeed(HOMING_SPEED);
    stepper.setAcceleration(HOMING_ACCEL);

    stepper.moveTo(-10000); 

    // 3. Wait until the bumper is hit (Le Core 1 fait le run() en toute sécurité ici)
    while (digitalRead(BUMPER_PIN) == LOW) { 
        stepper.run();
    }
    
    // 4. Arrêt immédiat
    stepper.setCurrentPosition(0);

    // 5. Dégagement du bouton
    stepper.moveTo(5);
    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
    
    // 6. Set the perfect absolute zero exactly where the switch releases
    stepper.setCurrentPosition(0); 

    // 7. Restore normal speed for the rest of the program
    stepper.setMaxSpeed(MAX_SPEED);
    stepper.setAcceleration(ACCELERATION);
    
    // 8. Le homing est fini, on rend le contrôle du moteur au Core 0
    isHoming = false;
    
    Serial.println("=== HOMING TERMINE (Position = 0) ===");
}

// ================================================================
// ================== 4. PUMP & VALVE MANAGEMENT ==================
// ================================================================

void refreshPumpState() {
    if (arm1_open || arm2_open || int1_open || int2_open) {
        digitalWrite(VALVE_PIN_PUMP, HIGH);
    } else {
        digitalWrite(VALVE_PIN_PUMP, LOW);
    }
}

void setArmSuckers(bool state) {
    arm1_open = state;
    arm2_open = state;
    digitalWrite(VALVE_PIN_ARM1_SUCKER, state ? HIGH : LOW);
    digitalWrite(VALVE_PIN_ARM2_SUCKER, state ? HIGH : LOW);
    refreshPumpState();
}

void setIntSuckers(bool state) {
    int1_open = state;
    int2_open = state;
    digitalWrite(VALVE_PIN_INT1_SUCKER, state ? HIGH : LOW);
    digitalWrite(VALVE_PIN_INT2_SUCKER, state ? HIGH : LOW);
    refreshPumpState();
}

// ================================================================
// ================== 5. MAESTRO CONTROL ==========================
// ================================================================

void maestroSetTarget(uint8_t channel, uint16_t target) {
    MaestroSerial.write(0x84); MaestroSerial.write(channel);
    MaestroSerial.write(target & 0x7F); MaestroSerial.write((target >> 7) & 0x7F);
}

void maestroSetSpeed(uint8_t channel, uint16_t speed) {
    MaestroSerial.write(0x87); MaestroSerial.write(channel);
    MaestroSerial.write(speed & 0x7F); MaestroSerial.write((speed >> 7) & 0x7F);
}

void maestroSetAccel(uint8_t channel, uint16_t accel) {
    MaestroSerial.write(0x89); MaestroSerial.write(channel);
    MaestroSerial.write(accel & 0x7F); MaestroSerial.write((accel >> 7) & 0x7F);
}

void applyFrameDual(
    uint16_t p4, uint16_t p5, uint16_t p6, uint16_t p9, uint16_t p10, uint16_t p11,
    uint16_t s4, uint16_t s5, uint16_t s6, uint16_t s9, uint16_t s10, uint16_t s11,
    uint16_t a4, uint16_t a5, uint16_t a6, uint16_t a9, uint16_t a10, uint16_t a11
) {
    maestroSetSpeed(4, s4); maestroSetSpeed(5, s5); maestroSetSpeed(6, s6);
    maestroSetAccel(4, a4); maestroSetAccel(5, a5); maestroSetAccel(6, a6);
    maestroSetTarget(4, p4); maestroSetTarget(5, p5); maestroSetTarget(6, p6);

    maestroSetSpeed(9, s9); maestroSetSpeed(10, s10); maestroSetSpeed(11, s11);
    maestroSetAccel(9, a9); maestroSetAccel(10, a10); maestroSetAccel(11, a11);
    maestroSetTarget(9, p9); maestroSetTarget(10, p10); maestroSetTarget(11, p11);
}

// ================================================================
// ================== 6. MACRO SEQUENCES (OPTIMISÉES) =============
// ================================================================

void Curseur_init_pos() {
    logToAll("--- init_curseur---");
    maestroSetSpeed(1, 50); maestroSetAccel(1, 50); maestroSetTarget(1, 5981); 
    maestroSetSpeed(3, 50); maestroSetAccel(3, 50); maestroSetTarget(3, 3876); 
    delay(800); 
    sendCANStatus(CAN_MSG_DONE); 
}

void Curseur_Yellow_Down() {
    logToAll("=== SEQ START: YellowCurDown ===");
    maestroSetSpeed(1, 50); maestroSetAccel(1, 50); maestroSetTarget(1, 3021); 
    sendCANStatus(CAN_MSG_DONE); 
}

void Curseur_Blue_Down() {
    logToAll("=== SEQ START: BlueCurDown ===");
    maestroSetSpeed(3, 50); maestroSetAccel(3, 50); maestroSetTarget(3, 7102); 
    sendCANStatus(CAN_MSG_DONE); 
}

void init_pos() {
    logToAll(">> EXEC: Init Dual");
    setArmSuckers(false); 
    setIntSuckers(false);
    Curseur_init_pos(); 
    delay(300);
    applyFrameDual(FRAME_INIT);
    delay(800); 
    maestroSetTarget(CH_A1_STORAGE, POS_ROT_NORMAL_1);
    maestroSetTarget(CH_A2_STORAGE, POS_ROT_NORMAL_2);
    homeRail();
}

// --- FONCTIONS PARALLÉLISÉES ---

// Le paramètre 'overlap_steps' permet de choisir la direction du rail pendant le rangement
void pickup_1_store_internally(long overlap_steps = 0) {
    logToAll("--- DUAL: PICK UP 1 SIMPLE ---");
    applyFrameDual(FRAME_PICK_UP_1);
    delay(900); 
    setArmSuckers(true);
    delay(600);
    
    logToAll("--- DUAL: STORE 1 ---");
    applyFrameDual(FRAME_STORE_1);
    
    // On laisse les bras remonter pour éviter la collision
    delay(200); 

    // 1. ON DONNE L'ORDRE DE DÉPART AU RAIL (Le Core 0 gère ça en fond)
    if (overlap_steps != 0) {
        executeMove(overlap_steps); 
    }
    delay(600); 

    // 2. PENDANT QUE LE RAIL ROULE, on finit le transfert des ventouses
    setIntSuckers(true);  
    delay(700); 
    setArmSuckers(false); 
    delay(600); 
    
    // 3. À LA TOUTE FIN, on attend que le rail ait fini son trajet (s'il n'a pas déjà fini)
    if (overlap_steps != 0) {
        waitForRail();
    }
}

void pickup_2_active_hold(long overlap_steps = 0) {
    logToAll("--- DUAL: PICK UP 2 ---");
    applyFrameDual(FRAME_PICK_UP_2);
    delay(900);
    setArmSuckers(true);  
    delay(600); 
    
    logToAll("--- DUAL: STORE 2 ---");
    applyFrameDual(FRAME_STORE_2);
    
    delay(200); 

    // 2. ON LANCE LE RAIL (Il recule en temps masqué !)
    if (overlap_steps != 0) {
        executeMove(overlap_steps); 
    }

    // 3. On termine le délai de rangement initial (200ms + 200ms = 400ms au total)
    delay(200);
    
    // 4. On s'assure que le rail a fini sa course avant de passer à la suite
    if (overlap_steps != 0) {
        waitForRail();
    }
}
void drop_1_from_arms(long overlap_steps = 0) {
    logToAll("--- DUAL: DROP 1 ---");
    applyFrameDual(FRAME_PICK_DOWN_2);
    delay(300);
    setArmSuckers(false); 
    delay(350);
    applyFrameDual(FRAME_OFF);
    
    // On attend 300ms pour que les bras soient bien levés et dégagés
    delay(300);    
    
    // ON DONNE L'ORDRE DE DÉPART AU RAIL
    if (overlap_steps != 0) {
        executeMove(overlap_steps); 
    }    
}

void drop_2_from_storage(bool inv1, bool inv2) { 

    int flipSpeed = 0; 
    int flipAccel = 0; 

    // 1. PENDANT QUE LE RAIL ROULE, on ordonne aux rangements de tourner
    maestroSetSpeed(CH_A1_STORAGE, flipSpeed);
    maestroSetAccel(CH_A1_STORAGE, flipAccel);
    maestroSetSpeed(CH_A2_STORAGE, flipSpeed);
    maestroSetAccel(CH_A2_STORAGE, flipAccel);

    maestroSetTarget(CH_A1_STORAGE, inv1 ? POS_ROT_INVERSE_1 : POS_ROT_NORMAL_1);
    maestroSetTarget(CH_A2_STORAGE, inv2 ? POS_ROT_INVERSE_2 : POS_ROT_NORMAL_2);
    
    // 2. On attend le temps physique que les servos fassent leur rotation
    delay(400); 

    // 3. SÉCURITÉ : Avant de baisser les bras pour déposer, on s'assure que 
    // le rail est bien arrivé à destination (au cas où il mettrait plus de temps)
    waitForRail(); 
    
    // 4. Suite normale de la séquence de dépose...
    if(inv1==true && inv2==true){
        applyFrameDual(FRAME_PICK_AFTER_FLIP);
        delay(800);
        setArmSuckers(true); 
        delay(400);
        setIntSuckers(false); 
        delay(300);
        applyFrameDual(FRAME_PICK_DOWN_AFTER_FLIP);
        delay(750);
        setArmSuckers(false); 
        delay(300);
        applyFrameDual(FRAME_OFF);
        delay(400);
        applyFrameDual(FRAME_INIT);
    }
    if(inv1==false && inv2==true){
        applyFrameDual(FRAME_PICK_AFTER_INT_2_FLIPPED);
        delay(800);
        setArmSuckers(true); 
        delay(400);
        setIntSuckers(false); 
        delay(300);
        applyFrameDual(FRAME_PICK_DOWN_INT_2_FLIPPED);
        delay(750);
        setArmSuckers(false); 
        delay(300);
        applyFrameDual(FRAME_OFF);
        delay(400);
        applyFrameDual(FRAME_INIT);
    }
    if(inv1==true && inv2==false){
        applyFrameDual(FRAME_PICK_AFTER_INT_1_FLIPPED);
        delay(800);
        setArmSuckers(true); 
        delay(400);
        setIntSuckers(false); 
        delay(300);
        applyFrameDual(FRAME_PICK_DOWN_INT_1_FLIPPED);
        delay(750);
        setArmSuckers(false); 
        delay(300);
        applyFrameDual(FRAME_OFF);
        delay(400);
        applyFrameDual(FRAME_INIT);
    }
} 

// ================================================================
// ================== MACROS CAN PRINCIPALES ======================
// ================================================================

void Forward_seq_pickup_both() {
    logToAll("=== SEQ START: PICKUP BOTH (FWD FIRST) ===");
    moveForward350(); waitForRail();
    // Après le pickup 1, le rail REcule (-BIG_STEP_SIZE) pendant le rangement
    pickup_1_store_internally(-BIG_STEP_SIZE1); 
    pickup_2_active_hold();
    sendCANStatus(CAN_MSG_DONE); 
}

void seq_pickup_both() {
    logToAll("=== SEQ START: PICKUP BOTH ===");
    moveForward100(); waitForRail();
    // Après le pickup 1, le rail AVance (BIG_STEP_SIZE) pendant le rangement
    pickup_1_store_internally(BIG_STEP_SIZE1); 
    
    pickup_2_active_hold(-BIG_STEP_SIZE3);
    sendCANStatus(CAN_MSG_DONE);
}

void _seq_3_base_runner(bool inv1, bool inv2) {
    logToAll("=== SEQ START: DROP BOTH ===");

    drop_1_from_arms(BIG_STEP_SIZE1); 
    
    drop_2_from_storage(inv1, inv2); 
    sendCANStatus(CAN_MSG_DONE);
    moveBackward350(); waitForRail();
    init_pos();
}

// ================================================================

void processCommand(char cmd) {
    if(cmd == '1') seq_pickup_both();
    if(cmd == 'B') _seq_3_base_runner(true, true);
    if(cmd == '2') _seq_3_base_runner(false, true);
    if(cmd == '3') _seq_3_base_runner(true, false);
    if(cmd == 'i') init_pos();
    if(cmd == 'Y') Curseur_Yellow_Down();
}

// ================================================================
// ================== GESTION DUAL-CORE (STEPPER) =================
// ================================================================

// CORRECTION DUAL-CORE : Libération de la vitesse du moteur
void stepperLoop(void * pvParameters) {
    for(;;) {
        if (!isHoming) {
            stepper.run(); 
        }
        
        if (stepper.distanceToGo() == 0) {
            // Le moteur est à l'arrêt : on met la tâche en pause pour laisser
            // 100% de la puissance au Bluetooth et au programme principal
            delay(1); 
        } else {
            // Le moteur tourne : on cède la main une fraction de seconde 
            // pour que le programme principal puisse lire les capteurs
            taskYIELD(); 
        }
    }
}

// ================================================================
// ================== 7. SETUP & LOOP =============================
// ================================================================

void setup() {
    Serial.begin(115200);
    SerialBT.begin("ESP32_Robot_Maestro"); 
    
    setupCAN();

    // Stepper Setup
    pinMode(BUMPER_PIN, INPUT_PULLDOWN);
    stepper.setMaxSpeed(MAX_SPEED);
    stepper.setAcceleration(ACCELERATION);
    stepper.setPinsInverted(true, false, false);

    // Valve Pins Setup
    pinMode(VALVE_PIN_PUMP, OUTPUT);
    pinMode(VALVE_PIN_ARM1_SUCKER, OUTPUT);
    pinMode(VALVE_PIN_ARM2_SUCKER, OUTPUT);
    pinMode(VALVE_PIN_INT1_SUCKER, OUTPUT);
    pinMode(VALVE_PIN_INT2_SUCKER, OUTPUT);
    
    // Initial State: Everything OFF
    digitalWrite(VALVE_PIN_PUMP, LOW);
    setArmSuckers(false);
    setIntSuckers(false);

    // Maestro Serial Mapping
    MaestroSerial.begin(9600, SERIAL_8N1, MAESTRO_RX_PIN, MAESTRO_TX_PIN);

    // --- DÉMARRAGE DU DUAL-CORE ---
    xTaskCreatePinnedToCore(
        stepperLoop,      // La fonction à exécuter
        "StepperTask",    // Nom de la tâche
        10000,            // Taille de la mémoire allouée
        NULL,             // Paramètres
        1,                // <--- CHANGER ICI : Priorité 1 (Égale au loop principal)
        &StepperTask,     // Pointeur vers la tâche
        1                 // <--- CHANGER ICI : Assigné au Core 1 !!!
    );
    
    init_pos();
}

void loop() {
    if (Serial.available()) processCommand(Serial.read());
    if (SerialBT.available()) processCommand(SerialBT.read());
        
    twai_message_t msg;
    if (twai_receive(&msg, 0) == ESP_OK) {
        if (msg.identifier == CAN_CMD_ID) {
            uint8_t cmd = msg.data[0];
            if(cmd == 0x20) seq_pickup_both();
            if(cmd == 0x21) Forward_seq_pickup_both();
            if(cmd == 0x22) _seq_3_base_runner(true, false);
            if(cmd == 0x23) _seq_3_base_runner(true, true);
            if(cmd == 0x24) _seq_3_base_runner(false, true);
            if(cmd == 0x29) Curseur_init_pos();
            if(cmd == 0x30) Curseur_Blue_Down();
            if(cmd == 0x31) Curseur_Yellow_Down();
            if(cmd == 0xFF) init_pos();
        }
    }
}
