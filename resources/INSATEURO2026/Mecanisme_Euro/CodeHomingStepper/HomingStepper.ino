#include <Arduino.h>
#include <AccelStepper.h>

// ================== 1. CONFIGURATION DU MATERIEL ================

#define STEPPER_STEP_PIN   GPIO_NUM_33
#define STEPPER_DIR_PIN    GPIO_NUM_32

// --- CAPTEUR (FIN DE COURSE) ---
#define BUMPER_PIN         GPIO_NUM_14 

// ================== 2. REGLAGES ET VITESSES =====================

#define MAX_SPEED          600.0   
#define ACCELERATION       300.0   

// Limites du rail (0 = Bumper, 320 = Bout du rail)
#define MAX_RAIL_POS       320     

// --- ZONES (MODIFIED) ---
#define POS_PICKUP         150     
#define POS_PICKUP2        220  

// Réglages du Homing
#define HOMING_SPEED_FAST  -200.0  
#define HOMING_SPEED_SLOW  -50.0   
#define BACKOFF_STEPS      20      

// ================== 3. OBJETS ET VARIABLES ======================

AccelStepper stepper(AccelStepper::DRIVER, STEPPER_STEP_PIN, STEPPER_DIR_PIN);
bool isHomed = false; 

// ================== 4. FONCTION HOMING ==========================

void executeHoming() {
    Serial.println("\n>>> DEBUT HOMING...");

    if (digitalRead(BUMPER_PIN) == HIGH) {
        Serial.println("   Switch deja enfonce. Recul de 30 pas...");
        stepper.move(30); 
        stepper.runToPosition();
        delay(200);
    }

    Serial.println("   Phase 1: Recherche rapide...");
    stepper.setSpeed(HOMING_SPEED_FAST); 
    
    while (digitalRead(BUMPER_PIN) == LOW) {
        stepper.runSpeed(); 
    }
    
    stepper.setCurrentPosition(0); 
    stepper.setSpeed(0);
    delay(200); 

    Serial.println("   Phase 2: Recul (Backoff)...");
    stepper.runToNewPosition(BACKOFF_STEPS); 

    Serial.println("   Phase 3: Precision...");
    stepper.setSpeed(HOMING_SPEED_SLOW);
    
    while (digitalRead(BUMPER_PIN) == LOW) {
        stepper.runSpeed();
    }

    stepper.setCurrentPosition(0); 
    stepper.setSpeed(0);
    isHomed = true;
    
    stepper.runToNewPosition(10); 
    
    Serial.println(">>> HOMING TERMINE. Zero defini.");
}

// ================== 5. FONCTION DEPLACEMENT =====================

void moveToPosition(long position) {
    if (!isHomed) {
        Serial.println("ERREUR: Faites le Homing ('H') d'abord !");
        return;
    }

    if (position < 0 || position > MAX_RAIL_POS) {
        Serial.printf("ERREUR: %ld est hors limites (0-%d)\n", position, MAX_RAIL_POS);
        return;
    }

    Serial.printf("Deplacement vers %ld...\n", position);
    stepper.moveTo(position); 

    while (stepper.distanceToGo() != 0) {
        
        if (stepper.currentPosition() > 50 && digitalRead(BUMPER_PIN) == HIGH) {
            Serial.println("!!! URGENCE : Bumper tape accidentellement !!!");
            stepper.stop();
            isHomed = false; 
            return;
        }
        
        if (Serial.available()) {
            char c = Serial.read();
            if (c == 's' || c == 'S') {
                stepper.stop();
                Serial.println("ARRET DEMANDE.");
                return;
            }
        }

        stepper.run(); 
    }
    Serial.println("Arrive.");
}

// ================== 6. SETUP ====================================

void setup() {
    Serial.begin(115200);
    Serial.println("\n--- ESP32 STEPPER CONTROLLER ---");
    // Updated Menu Text
    Serial.println("Commandes: H=Home, P=Pickup, D=Pickup2, Z=Zero, S=Stop");

    pinMode(BUMPER_PIN, INPUT_PULLDOWN); 

    stepper.setMaxSpeed(MAX_SPEED);      
    stepper.setAcceleration(ACCELERATION); 
}

// ================== 7. LOOP =====================================

void loop() {
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        
        if (cmd == '\n' || cmd == '\r') return;

        switch (toupper(cmd)) {
            case 'H': 
                executeHoming(); 
                break;
                
            case 'P': 
                moveToPosition(POS_PICKUP); 
                break;
                
            case 'D': 
                moveToPosition(POS_PICKUP2); 
                break;
                
            case 'Z': 
                moveToPosition(0); 
                break;
                
            case 'S': 
                stepper.stop(); 
                break;
                
            case 'F': 
                if(isHomed) moveToPosition(stepper.currentPosition() + 50);
                else Serial.println("Home d'abord !");
                break;
                
            case 'B': 
                if(isHomed) moveToPosition(stepper.currentPosition() - 50);
                else Serial.println("Home d'abord !");
                break;
        }
    }
}
