#include <Arduino.h>
#include <Bluepad32.h>

// --- Configuration des broches ---
const int LPWM_A = 26; const int RPWM_A = 27; // Moteur Gauche
const int LPWM_B = 32; const int RPWM_B = 33; // Moteur Droit
const int EN_PIN = 25;                        // Broche Enable (Activation)
const int BUZZER_PIN = 15;                    // Broche du Buzzer

// --- Notes de Musique (Fréquences en Hz) ---
// --- Notes de Musique (Fréquences en Hz) ---
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_C5  523
#define NOTE_D5  587
#define NOTE_E5  659
#define NOTE_C6  1047
#define NOTE_G4 392
#define NOTE_C5 523
#define NOTE_E5 659
#define NOTE_G5 784
// --- Notes de Musique (Fréquences en Hz) ---
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_D5  587
#define NOTE_E5  659
#define NOTE_C6  1047
ControllerPtr myController = nullptr;

void stopAll() {
    analogWrite(LPWM_A, 0); analogWrite(RPWM_A, 0);
    analogWrite(LPWM_B, 0); analogWrite(RPWM_B, 0);
}

void onConnectedController(ControllerPtr ctl) {
    if (myController == nullptr) {
        myController = ctl;
        Serial.println("MANETTE CONNECTÉE ! Prêt à rouler !");
    }
}

void onDisconnectedController(ControllerPtr ctl) {
    if (myController == ctl) {
        myController = nullptr;
        Serial.println("Manette déconnectée. Arrêt d'urgence !");
        stopAll(); 
        noTone(BUZZER_PIN); 
    }
}

void setup() {
    Serial.begin(115200);
    
    pinMode(LPWM_A, OUTPUT); pinMode(RPWM_A, OUTPUT);
    pinMode(LPWM_B, OUTPUT); pinMode(RPWM_B, OUTPUT);
    pinMode(EN_PIN, OUTPUT); digitalWrite(EN_PIN, HIGH);
    
    pinMode(BUZZER_PIN, OUTPUT);
    noTone(BUZZER_PIN); 
    
    stopAll(); 
    
    BP32.setup(&onConnectedController, &onDisconnectedController);
    BP32.forgetBluetoothKeys(); 
    
    Serial.println("Démarrage du robot. Mettez la manette en MODE APPAIRAGE (SHARE + PS) !");
}

void loop() {
    BP32.update();

    if (myController && myController->isConnected()) {
        
        // --- MÉMOIRE DES BOUTONS (Pour ne jouer qu'une fois par clic) ---
        // --- MÉMOIRE DES BOUTONS ---
        static bool btnB_played = false; // Cercle
        static bool btnA_played = false; // Croix
        static bool btnY_played = false; // Triangle
        static bool btnX_played = false; // Carré

        // 1. CERCLE (b) : WINNER ! (Petite fanfare de victoire)
        if (myController->b()) {
            if (!btnB_played) {
               tone(BUZZER_PIN, NOTE_G4); delay(150);
                tone(BUZZER_PIN, NOTE_C5); delay(150);
                tone(BUZZER_PIN, NOTE_E5); delay(150);
                tone(BUZZER_PIN, NOTE_G5); delay(300);
                tone(BUZZER_PIN, NOTE_E5); delay(150);
                tone(BUZZER_PIN, NOTE_G5); delay(400);
                noTone(BUZZER_PIN); // Arrête le son
                btnB_played = true;
            }
        } else { btnB_played = false; }

        // 2. CROIX (a) : MARIO (Pièce - conservé)
        if (myController->a()) {
            if (!btnA_played) {
                tone(BUZZER_PIN, NOTE_E5); delay(100);
                tone(BUZZER_PIN, NOTE_C6); delay(400);
                noTone(BUZZER_PIN);
                btnA_played = true;
            }
        } else { btnA_played = false; }

        // 3. TRIANGLE (y) : LOSING (Trombone triste : Womp womp womp woooomp)
        if (myController->y()) {
            if (!btnY_played) {
                tone(BUZZER_PIN, NOTE_C4);  delay(300);
                tone(BUZZER_PIN, NOTE_B3);  delay(300);
                tone(BUZZER_PIN, NOTE_AS3); delay(300);
                tone(BUZZER_PIN, NOTE_A3);  delay(500);
                noTone(BUZZER_PIN);
                btnY_played = true;
            }
        } else { btnY_played = false; }

        // 4. CARRÉ (x) : FUNNY (Megalovania / Sans Meme)
        if (myController->x()) {
            if (!btnX_played) {
                tone(BUZZER_PIN, NOTE_D4); delay(120);
                noTone(BUZZER_PIN);        delay(50); // Petite pause pour séparer les notes
                tone(BUZZER_PIN, NOTE_D4); delay(120);
                tone(BUZZER_PIN, NOTE_D5); delay(250);
                tone(BUZZER_PIN, NOTE_A4); delay(300);
                noTone(BUZZER_PIN);
                btnX_played = true;
            }
        } else { btnX_played = false; }


        // --- CONDUITE ET VITESSES ---
        int joyY = myController->axisY(); 
        int joyX = myController->axisX(); 

        if (abs(joyY) < 30) joyY = 0;
        if (abs(joyX) < 30) joyX = 0;

        int maxSpeed = 55; // Défaut : 25%

       if (myController->throttle() > 100) {      
             maxSpeed = 255; // 100%
        } else if (myController->brake() > 100) {
             maxSpeed = 191; // 75%
        } else if (myController->r1()) {
             maxSpeed = 127; // 50%
        } else if (myController->l1()) {
             maxSpeed = 89;  // 35%
        }

        int throttle = map(-joyY, -511, 512, -maxSpeed, maxSpeed); 
        int steering = map(joyX, -511, 512, -maxSpeed, maxSpeed);

        int leftSpeed = constrain(throttle + steering, -maxSpeed, maxSpeed);
        int rightSpeed = constrain(throttle - steering, -maxSpeed, maxSpeed);

        // MOTEUR GAUCHE
        if (leftSpeed > 0) {
            analogWrite(LPWM_A, leftSpeed); analogWrite(RPWM_A, 0);
        } else if (leftSpeed < 0) {
            analogWrite(LPWM_A, 0); analogWrite(RPWM_A, abs(leftSpeed));
        } else {
            analogWrite(LPWM_A, 0); analogWrite(RPWM_A, 0);
        }

        // MOTEUR DROIT
        if (rightSpeed > 0) {
            analogWrite(LPWM_B, rightSpeed); analogWrite(RPWM_B, 0);
        } else if (rightSpeed < 0) {
            analogWrite(LPWM_B, 0); analogWrite(RPWM_B, abs(rightSpeed));
        } else {
            analogWrite(LPWM_B, 0); analogWrite(RPWM_B, 0);
        }
    }
    
    delay(10); 
}