#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoOTA.h>
#include <PID_v1.h>
#include <math.h>

// ── WiFi ──────────────────────────────────────────────────
const char* ssid     = "Airbox-4FCB";
const char* password = "WT6FHJ65";

// ── Telnet — two separate ports ───────────────────────────
WiFiServer cmdServer(23);
WiFiServer dataServer(24);
WiFiClient cmdClient;
WiFiClient dataClient;

void cmdPrint  (String msg) { if (cmdClient  && cmdClient.connected())  cmdClient.print(msg);   }
void cmdPrintln(String msg) { if (cmdClient  && cmdClient.connected())  cmdClient.println(msg); }
void dataPrintln(String msg){ if (dataClient && dataClient.connected()) dataClient.println(msg);}

// ── Encoder pins ──────────────────────────────────────────
#define ENCODER_RA 33
#define ENCODER_RB 32
#define ENCODER_LA 35
#define ENCODER_LB 34

// ── Motor pins ────────────────────────────────────────────
#define IN1 25
#define IN2 26
#define ENA 12
#define IN3 27
#define IN4 14
#define ENB 13

// ── PWM config ────────────────────────────────────────────
#define PWM_FREQ        20000
#define PWM_RESOLUTION      8
#define PWM_CH_LEFT         0
#define PWM_CH_RIGHT        1

// ── Robot constants ───────────────────────────────────────
#define TICKS_PER_REV      1050.0f
#define WHEEL_DIAMETER_MM    44.0f
#define WHEELBASE_MM        72.0f
#define WHEEL_CIRCUMFERENCE (M_PI * WHEEL_DIAMETER_MM)
#define DIST_PER_TICK       (WHEEL_CIRCUMFERENCE / TICKS_PER_REV)

// ── Deadband ──────────────────────────────────────────────
#define MIN_PWM_LEFT_FORWARD    20
#define MIN_PWM_RIGHT_FORWARD   20
#define MIN_PWM_LEFT_BACKWARD  -19
#define MIN_PWM_RIGHT_BACKWARD -25

// ── Thresholds ────────────────────────────────────────────
#define ANGLE_THRESHOLD   0.03f
#define DIST_THRESHOLD    5.0f
#define STABLE_TIME_MS    500

// ── Encoder counters ──────────────────────────────────────
volatile int32_t leftTicks  = 0;
volatile int32_t rightTicks = 0;

// ── Odometry ──────────────────────────────────────────────
float x     = 0.0f;
float y     = 0.0f;
float theta = 0.0f;
int32_t prevLeftTicks  = 0;
int32_t prevRightTicks = 0;

// ── PID variables ─────────────────────────────────────────
double angleInput, angleOutput, angleSetpoint = 0.0;
double distInput,  distOutput,  distSetpoint  = 0.0;

// ── PID constants ─────────────────────────────────────────
double aKp = 120.0, aKi = 0.0, aKd = 1.5;
double dKp =  1.0, dKi = 0.0, dKd = 0.0;

// ── PID objects ───────────────────────────────────────────
PID anglePID(&angleInput, &angleOutput, &angleSetpoint, aKp, aKi, aKd, DIRECT);
PID distPID (&distInput,  &distOutput,  &distSetpoint,  dKp, dKi, dKd, DIRECT);

// ── State machine ─────────────────────────────────────────
enum State { IDLE, HOLD, ANGLE_TUNE, DIST_TUNE, RUN_WAYPOINT };
State currentState = IDLE;

// ── Speed profile ─────────────────────────────────────────
#define MAX_DIST_SPEED     180   // cruise speed (PWM)
#define MIN_DIST_SPEED      30   // minimum moving speed (PWM)
#define RAMP_UP_MM         80.0f // accelerate over first 80mm
#define RAMP_DOWN_MM      120.0f // decelerate over last 120mm

// ── Targets ───────────────────────────────────────────────
float targetAngle = M_PI / 2.0f;
float targetDist  = 500.0f;
float waypointX   = 0.0f;
float waypointY   = 0.0f;
uint8_t waypointPhase = 0;

// ── Stability tracking ────────────────────────────────────
unsigned long stableStartTime = 0;
bool isStable = false;

// ── Timing ────────────────────────────────────────────────
unsigned long lastOdomTime   = 0;
unsigned long lastPrintTime  = 0;
unsigned long lastHoldPrint  = 0;
const uint16_t ODOM_INTERVAL_MS  = 10;
const uint16_t PRINT_INTERVAL_MS = 100;  // 10Hz telemetry for dashboard
const uint16_t HOLD_PRINT_MS     = 200;  // print error 5x/sec in HOLD mode

// ── Command buffer ────────────────────────────────────────
String cmdBuffer = "";

// ══════════════════════════════════════════════════════════
// ISRs
// ══════════════════════════════════════════════════════════
void IRAM_ATTR leftEncoderISR() {
  if (digitalRead(ENCODER_LB) == LOW) leftTicks++;
  else                                 leftTicks--;
}
void IRAM_ATTR rightEncoderISR() {
  if (digitalRead(ENCODER_RB) == LOW) rightTicks++;
  else                                  rightTicks--;
}

// ══════════════════════════════════════════════════════════
// Odometry
// ══════════════════════════════════════════════════════════
void updateOdometry() {
  int32_t curLeft  = leftTicks;
  int32_t curRight = rightTicks;

  float dL = (curLeft  - prevLeftTicks)  * DIST_PER_TICK;
  float dR = (curRight - prevRightTicks) * DIST_PER_TICK;

  prevLeftTicks  = curLeft;
  prevRightTicks = curRight;

  float distCenter = (dL + dR) / 2.0f;
  float dTheta     = (dR - dL) / WHEELBASE_MM;

  theta += dTheta;
  while (theta >  M_PI) theta -= 2.0f * M_PI;
  while (theta < -M_PI) theta += 2.0f * M_PI;

  x += distCenter * cos(theta);
  y += distCenter * sin(theta);
}

void resetOdometry() {
  noInterrupts();
  leftTicks = 0; rightTicks = 0;
  interrupts();
  prevLeftTicks = 0; prevRightTicks = 0;
  x = 0.0f; y = 0.0f; theta = 0.0f;
}

// ══════════════════════════════════════════════════════════
// Helpers
// ══════════════════════════════════════════════════════════
float normalizeAngle(float a) {
  while (a >  M_PI) a -= 2.0f * M_PI;
  while (a < -M_PI) a += 2.0f * M_PI;
  return a;
}

int applyDeadbandLeft(int pwm) {
  if (pwm == 0) return 0;
  if (pwm > 0)  return map(pwm,    1,  255, MIN_PWM_LEFT_FORWARD,    255);
  else          return map(pwm, -255,   -1, -255, MIN_PWM_LEFT_BACKWARD);
}

int applyDeadbandRight(int pwm) {
  if (pwm == 0) return 0;
  if (pwm > 0)  return map(pwm,    1,  255, MIN_PWM_RIGHT_FORWARD,   255);
  else          return map(pwm, -255,   -1, -255, MIN_PWM_RIGHT_BACKWARD);
}

// ══════════════════════════════════════════════════════════
// Motor control
// ══════════════════════════════════════════════════════════
void setMotor(uint8_t in1, uint8_t in2, uint8_t pwmCh, int speed) {
  speed = constrain(speed, -255, 255);
  if (speed > 0) {
    digitalWrite(in1, HIGH); digitalWrite(in2, LOW);
    ledcWrite(pwmCh, speed);
  } else if (speed < 0) {
    digitalWrite(in1, LOW);  digitalWrite(in2, HIGH);
    ledcWrite(pwmCh, -speed);
  } else {
    digitalWrite(in1, LOW);  digitalWrite(in2, LOW);
    ledcWrite(pwmCh, 0);
  }
}

void setLeftMotor (int s) { setMotor(IN1, IN2, PWM_CH_LEFT,  applyDeadbandLeft (s)); }
void setRightMotor(int s) { setMotor(IN3, IN4, PWM_CH_RIGHT, applyDeadbandRight(s)); }
void stopMotors()          { setLeftMotor(0); setRightMotor(0); }

// ══════════════════════════════════════════════════════════
// State transitions
// ══════════════════════════════════════════════════════════
void enterIdle() {
  currentState = IDLE;
  stopMotors();
  anglePID.SetMode(MANUAL);
  distPID.SetMode(MANUAL);
  angleOutput = 0; distOutput = 0;
  cmdPrintln("[STATE] IDLE — motors stopped");
}

void enterHold() {
  resetOdometry();
  targetAngle  = 0.0f;
  currentState = HOLD;
  isStable     = false;
  anglePID.SetTunings(aKp, aKi, aKd);
  anglePID.SetOutputLimits(-200, 200);
  anglePID.SetMode(AUTOMATIC);
  anglePID.SetSampleTime(10); 
  cmdPrintln("[STATE] HOLD — twist the robot and watch it return");
  cmdPrintln("Kp:" + String(aKp) + " Ki:" + String(aKi) + " Kd:" + String(aKd));
}

void enterAngleTune(float target) {
  resetOdometry();
  targetAngle   = target;
  currentState  = ANGLE_TUNE;
  isStable      = false;
  anglePID.SetTunings(aKp, aKi, aKd);
  anglePID.SetOutputLimits(-200, 200);
  anglePID.SetMode(AUTOMATIC);
  anglePID.SetSampleTime(10); 
  cmdPrintln("[STATE] ANGLE_TUNE — target: " + String(degrees(targetAngle), 1) + " deg");
  cmdPrintln("Kp:" + String(aKp) + " Ki:" + String(aKi) + " Kd:" + String(aKd));
}

void enterDistTune(float target) {
  resetOdometry();
  targetDist   = target;
  currentState = DIST_TUNE;
  isStable     = false;
  distPID.SetTunings(dKp, dKi, dKd);
  distPID.SetOutputLimits(0, 200);
  distPID.SetMode(AUTOMATIC);
  distPID.SetSampleTime(10);
  anglePID.SetTunings(aKp, aKi, aKd);
  anglePID.SetOutputLimits(-50, 50);  // ← limit correction to ±50 only
  anglePID.SetSampleTime(10);
  anglePID.SetMode(AUTOMATIC);
  cmdPrintln("[STATE] DIST_TUNE — target: " + String(targetDist, 1) + " mm");
  cmdPrintln("Kp:" + String(dKp) + " Ki:" + String(dKi) + " Kd:" + String(dKd));
}

void enterRunWaypoint(float tx, float ty) {
  resetOdometry();
  waypointX     = tx;
  waypointY     = ty;
  waypointPhase = 0;
  currentState  = RUN_WAYPOINT;
  isStable      = false;
  anglePID.SetTunings(aKp, aKi, aKd);
  anglePID.SetOutputLimits(-200, 200);
  anglePID.SetMode(AUTOMATIC);
  anglePID.SetSampleTime(10); 
  distPID.SetTunings(dKp, dKi, dKd);
  distPID.SetOutputLimits(0, 200);
  distPID.SetMode(AUTOMATIC);
  distPID.SetSampleTime(10);
  cmdPrintln("[STATE] RUN_WAYPOINT → (" + String(tx,1) + ", " + String(ty,1) + ")");
}

// ══════════════════════════════════════════════════════════
// State machine update
// ══════════════════════════════════════════════════════════
void updateStateMachine() {
  switch (currentState) {

    case IDLE:
      stopMotors();
      break;

    // ── HOLD — disturbance rejection test ─────────────────
    case HOLD: {
      float angleError  = normalizeAngle(targetAngle - theta);
      angleInput        = angleError;
      angleSetpoint     = 0.0;
      anglePID.Compute();

      setLeftMotor (-(int)angleOutput);
      setRightMotor( (int)angleOutput);

      // print error to cmd port at 5Hz so you can read it
      if (millis() - lastHoldPrint >= HOLD_PRINT_MS) {
        lastHoldPrint = millis();
        cmdPrintln("err:" + String(degrees(angleError), 2) +
                   " deg  out:" + String(angleOutput, 1) +
                   "  th:" + String(degrees(theta), 2) + " deg");
      }
      break;
    }

    // ── ANGLE TUNE ────────────────────────────────────────
    case ANGLE_TUNE: {
      float angleError  = normalizeAngle(targetAngle - theta);
      angleInput        = angleError;
      angleSetpoint     = 0.0;
      anglePID.Compute();

      setLeftMotor (-(int)angleOutput);
      setRightMotor( (int)angleOutput);

      if (fabs(angleError) < ANGLE_THRESHOLD) {
        if (!isStable) { isStable = true; stableStartTime = millis(); }
        else if (millis() - stableStartTime > STABLE_TIME_MS) {
          stopMotors();
          cmdPrintln("[DONE] Angle reached: " + String(degrees(theta), 2) + " deg");
          enterIdle();
        }
      } else { isStable = false; }
      break;
    }

    // ── DIST TUNE ─────────────────────────────────────────
    case DIST_TUNE: {
  float distTraveled = sqrt(x * x + y * y);
  float distError    = targetDist - distTraveled;

  // ── Speed profile ──────────────────────────────────────
  int profileSpeed;

  if (distTraveled < RAMP_UP_MM) {
    profileSpeed = map((int)distTraveled, 0, (int)RAMP_UP_MM,
                       MIN_DIST_SPEED, MAX_DIST_SPEED);
  } else if (distError > RAMP_DOWN_MM) {
    profileSpeed = MAX_DIST_SPEED;
  } else if (distError > 0) {
    profileSpeed = map((int)distError, 0, (int)RAMP_DOWN_MM,
                       MIN_DIST_SPEED, MAX_DIST_SPEED);
  } else {
    // overshot — brief reverse
    int brakeSpeed = constrain((int)(distError * -2), -40, 0);
    setLeftMotor (brakeSpeed);
    setRightMotor(brakeSpeed);
    break;
  }

  profileSpeed = constrain(profileSpeed, 0, MAX_DIST_SPEED);

  // ── Straight line correction using angle PID ───────────
  // target heading = 0 (same direction as start)
  float headingError = normalizeAngle(0.0f - theta);
  angleInput         = headingError;
  angleSetpoint      = 0.0;
  anglePID.Compute();

  // apply correction — one side faster, other slower
  int leftSpeed  = constrain(profileSpeed - (int)angleOutput, 0, MAX_DIST_SPEED);
  int rightSpeed = constrain(profileSpeed + (int)angleOutput, 0, MAX_DIST_SPEED);

  setLeftMotor (leftSpeed);
  setRightMotor(rightSpeed);

  if (fabs(distError) < DIST_THRESHOLD) {
    if (!isStable) { isStable = true; stableStartTime = millis(); }
    else if (millis() - stableStartTime > STABLE_TIME_MS) {
      stopMotors();
      cmdPrintln("[DONE] Distance reached: " + String(distTraveled, 1) + "mm");
      cmdPrintln("Final heading: " + String(degrees(theta), 2) + " deg");
      enterIdle();
    }
  } else { isStable = false; }
  break;
}
    // ── RUN WAYPOINT ──────────────────────────────────────
    case RUN_WAYPOINT: {
      float dx            = waypointX - x;
      float dy            = waypointY - y;
      float distToTarget  = sqrt(dx * dx + dy * dy);
      float angleToTarget = atan2(dy, dx);
      float angleError    = normalizeAngle(angleToTarget - theta);

      if (waypointPhase == 0) {
        angleInput    = angleError;
        angleSetpoint = 0.0;
        anglePID.Compute();
        setLeftMotor (-(int)angleOutput);
        setRightMotor( (int)angleOutput);
        if (fabs(angleError) < ANGLE_THRESHOLD) {
          waypointPhase = 1;
          cmdPrintln("[WP] Aligned — driving...");
        }
      } else {
  float distToTarget  = sqrt(dx * dx + dy * dy);
  float distTraveled  = sqrt(x * x + y * y);
  float totalDist     = sqrt(waypointX*waypointX + waypointY*waypointY);

  // ── Speed profile ──────────────────────────────────────
  int profileSpeed;

  if (distTraveled < RAMP_UP_MM) {
    profileSpeed = map((int)distTraveled, 0, (int)RAMP_UP_MM,
                       MIN_DIST_SPEED, MAX_DIST_SPEED);
  } else if (distToTarget > RAMP_DOWN_MM) {
    profileSpeed = MAX_DIST_SPEED;
  } else if (distToTarget > 0) {
    profileSpeed = map((int)distToTarget, 0, (int)RAMP_DOWN_MM,
                       MIN_DIST_SPEED, MAX_DIST_SPEED);
  } else {
    profileSpeed = 0;
  }

  profileSpeed = constrain(profileSpeed, 0, MAX_DIST_SPEED);

  // ── Angle correction on top of speed profile ──────────
  angleInput    = angleError;
  angleSetpoint = 0.0;
  anglePID.Compute();

  int leftSpeed  = constrain(profileSpeed - (int)angleOutput, 0, MAX_DIST_SPEED);
  int rightSpeed = constrain(profileSpeed + (int)angleOutput, 0, MAX_DIST_SPEED);

  setLeftMotor (leftSpeed);
  setRightMotor(rightSpeed);

  if (distToTarget < DIST_THRESHOLD) {
    if (!isStable) { isStable = true; stableStartTime = millis(); }
    else if (millis() - stableStartTime > STABLE_TIME_MS) {
      stopMotors();
      cmdPrintln("[DONE] Waypoint reached! x:" + String(x,1) + " y:" + String(y,1));
      enterIdle();
    }
  } else { isStable = false; }
}
      break;
    }
  }
}

// ══════════════════════════════════════════════════════════
// Command parser
// ══════════════════════════════════════════════════════════
void parseCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  cmdPrintln("> " + cmd);

  if (cmd == "S") {
    enterIdle();

  } else if (cmd == "H") {
    enterHold();

  } else if (cmd == "R") {
    resetOdometry();
    cmdPrintln("[RESET] Odometry cleared");

  } else if (cmd.startsWith("A")) {
    float deg = 90.0f;
    if (cmd.length() > 1) deg = cmd.substring(2).toFloat();
    enterAngleTune(radians(deg));

  } else if (cmd.startsWith("D")) {
    float dist = 500.0f;
    if (cmd.length() > 1) dist = cmd.substring(2).toFloat();
    enterDistTune(dist);

  } else if (cmd.startsWith("W")) {
    float tx = 0, ty = 0;
    sscanf(cmd.c_str(), "W %f %f", &tx, &ty);
    enterRunWaypoint(tx, ty);

  } else if (cmd.startsWith("KA")) {
    sscanf(cmd.c_str(), "KA %lf %lf %lf", &aKp, &aKi, &aKd);
    anglePID.SetTunings(aKp, aKi, aKd);
    cmdPrintln("[KA] Angle PID → Kp:" + String(aKp) +
               " Ki:" + String(aKi) + " Kd:" + String(aKd));

  } else if (cmd.startsWith("KD")) {
    sscanf(cmd.c_str(), "KD %lf %lf %lf", &dKp, &dKi, &dKd);
    distPID.SetTunings(dKp, dKi, dKd);
    cmdPrintln("[KD] Dist PID → Kp:" + String(dKp) +
               " Ki:" + String(dKi) + " Kd:" + String(dKd));

  } else if (cmd == "?") {
    cmdPrintln("Commands:");
    cmdPrintln("  H               — HOLD mode (disturbance test)");
    cmdPrintln("  A [deg]         — angle tune (default 90)");
    cmdPrintln("  D [mm]          — dist  tune (default 500)");
    cmdPrintln("  W <x> <y>       — run waypoint");
    cmdPrintln("  KA <kp> <ki> <kd> — set angle PID");
    cmdPrintln("  KD <kp> <ki> <kd> — set dist  PID");
    cmdPrintln("  R               — reset odometry");
    cmdPrintln("  S               — stop");

  } else {
    cmdPrintln("[?] Unknown — type ? for help");
  }
}

// ══════════════════════════════════════════════════════════
// Telemetry — port 24 only
// ══════════════════════════════════════════════════════════
void printTelemetry() {
  String stateStr;
  switch (currentState) {
    case IDLE:         stateStr = "IDLE";         break;
    case HOLD:         stateStr = "HOLD";         break;
    case ANGLE_TUNE:   stateStr = "ANGLE_TUNE";   break;
    case DIST_TUNE:    stateStr = "DIST_TUNE";    break;
    case RUN_WAYPOINT: stateStr = "RUN_WAYPOINT"; break;
  }

  String msg = "{";
  msg += "\"state\":\""  + stateStr                                       + "\",";
  msg += "\"x\":"        + String(x,            2)                        + ",";
  msg += "\"y\":"        + String(y,            2)                        + ",";
  msg += "\"th\":"       + String(theta,         4)                       + ",";
  msg += "\"aErr\":"     + String(normalizeAngle(targetAngle - theta), 4) + ",";
  msg += "\"dErr\":"     + String(targetDist - sqrt(x*x + y*y), 2)       + ",";
  msg += "\"aPID\":"     + String(angleOutput,   2)                       + ",";
  msg += "\"dPID\":"     + String(distOutput,    2)                       + ",";
  msg += "\"aKp\":"      + String(aKp)                                    + ",";
  msg += "\"aKi\":"      + String(aKi)                                    + ",";
  msg += "\"aKd\":"      + String(aKd)                                    + ",";
  msg += "\"dKp\":"      + String(dKp)                                    + ",";
  msg += "\"dKi\":"      + String(dKi)                                    + ",";
  msg += "\"dKd\":"      + String(dKd)                                    + ",";
  msg += "\"L\":"        + String(leftTicks)                              + ",";
  msg += "\"R\":"        + String(rightTicks);
  msg += "}";

  dataPrintln(msg);
}

// ══════════════════════════════════════════════════════════
// Setup
// ══════════════════════════════════════════════════════════
void setup() {
  // Motors
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  ledcSetup(PWM_CH_LEFT,  PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CH_RIGHT, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(ENA, PWM_CH_LEFT);
  ledcAttachPin(ENB, PWM_CH_RIGHT);
  stopMotors();

  // Encoders
  pinMode(ENCODER_LA, INPUT_PULLUP); pinMode(ENCODER_LB, INPUT_PULLUP);
  pinMode(ENCODER_RA, INPUT_PULLUP); pinMode(ENCODER_RB, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_LA), leftEncoderISR,  RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RA), rightEncoderISR, RISING);

  // WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  // OTA
  ArduinoOTA.setHostname("diff-robot");
  ArduinoOTA.begin();

  // Telnet
  cmdServer.begin();  cmdServer.setNoDelay(true);
  dataServer.begin(); dataServer.setNoDelay(true);

  // PID off until activated
  anglePID.SetMode(MANUAL);
  distPID.SetMode(MANUAL);
}

// ══════════════════════════════════════════════════════════
// Loop
// ══════════════════════════════════════════════════════════
void loop() {
  ArduinoOTA.handle();

  // ── Command client — port 23 ─────────────────────────────
  if (!cmdClient || !cmdClient.connected()) {
    WiFiClient newClient = cmdServer.available();
    if (newClient) {
      cmdClient = newClient;
      cmdPrintln("=== diff-robot ready ===");
      cmdPrintln("Type ? for command list");
    }
  }

  // ── Data client — port 24 ────────────────────────────────
  if (!dataClient || !dataClient.connected()) {
    WiFiClient newClient = dataServer.available();
    if (newClient) {
      dataClient = newClient;
      dataPrintln("=== telemetry stream ===");
    }
  }

  // ── Read commands ────────────────────────────────────────
  while (cmdClient && cmdClient.connected() && cmdClient.available()) {
    char c = cmdClient.read();
    if (c == '\n' || c == '\r') {
      if (cmdBuffer.length() > 0) {
        parseCommand(cmdBuffer);
        cmdBuffer = "";
      }
    } else {
      cmdBuffer += c;
    }
  }

  // ── Odometry + state machine at 100Hz ────────────────────
  if (millis() - lastOdomTime >= ODOM_INTERVAL_MS) {
    lastOdomTime = millis();
    updateOdometry();
    updateStateMachine();
  }

  // ── Telemetry at 2Hz → port 24 ───────────────────────────
  if (millis() - lastPrintTime >= PRINT_INTERVAL_MS) {
    lastPrintTime = millis();
    printTelemetry();
  }
}