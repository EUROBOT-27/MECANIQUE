/*
  ESP32 (BLE classic Arduino, no NimBLE) -> Pololu Mini Maestro (UART)
  + Relay pump control
  + 3 poses: lift (soulevement), rot (rotation), ext (extension)
  + sequence "seq ext" = lift -> rot -> ext
  + manual servo control: "ch,us" or "ch us"

  BLE:
    Service  : 7c2f4b10-8a6d-4c0f-9d2c-3efb5e7d1a01
    Control  : 7c2f4b11-8a6d-4c0f-9d2c-3efb5e7d1a01 (write/writeNR)
    Status   : 7c2f4b12-8a6d-4c0f-9d2c-3efb5e7d1a01 (notify)

  Commands (text):
    pump on|off|toggle
    pose lift|rot|ext
    seq ext
    seq stop
    sp ch val
    ac ch val
    debug on|off
    rst | reset
*/

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ----------------- CONFIG -----------------
static const char* DEV_NAME     = "ESP32-Maestro";
static const char* SERVICE_UUID = "7c2f4b10-8a6d-4c0f-9d2c-3efb5e7d1a01";
static const char* CONTROL_UUID = "7c2f4b11-8a6d-4c0f-9d2c-3efb5e7d1a01";
static const char* STATUS_UUID  = "7c2f4b12-8a6d-4c0f-9d2c-3efb5e7d1a01";

static const uint32_t MAESTRO_BAUD = 9600;
static const int MAESTRO_RX_PIN = 16; // ESP32 RX  (Maestro TX) optional for reads
static const int MAESTRO_TX_PIN = 17; // ESP32 TX -> Maestro RX
static const uint8_t MAESTRO_CH = 12;

// Relay (pump)
static const int  RELAY_PIN = 25;        // change if needed
static const bool RELAY_ACTIVE_HIGH = true;

// Maestro RST pin (active low)
static const int RST_PIN = 33;

// If you want to clamp manual "ch,us"
static const bool     CLAMP_ENABLE = false;
static const uint16_t CLAMP_MIN_US = 300;
static const uint16_t CLAMP_MAX_US = 3000;

// Sequence timings (ms) - tune
static const uint32_t T_LIFT = 700;
static const uint32_t T_ROT  = 700;
static const uint32_t T_EXT  = 900;
// ------------------------------------------

// ----------------- POSES (MUST BE ABOVE FUNCTIONS) -----------------
// poses apply to CH0..CH9 (10 channels)
static const uint8_t PCH = 10;

struct Pose {
  const char* name;
  uint16_t q[PCH];   // q = us*4 (quarter-microseconds)
  uint16_t sp[PCH];  // Maestro speed units
  uint16_t ac[PCH];  // Maestro accel units
};

// From your screenshots (q = value * 4)
static const Pose POSE_LIFT = {
  "LIFT",
  { 1425, 5168, 1931, 2517, 5480,  256,  256,  256, 16320, 16320 }, // 356.25,1292,482.75,629.25,1370,64,64,64,4080,4080
  {   50,   50,   50,   50,   50,   50,    0,    0,     0,     0 },
  {   50,   50,   50,   50,   50,   50,    0,    0,     0,     0 }
};

static const Pose POSE_ROT = {
  "ROT",
  { 1425, 7664, 1931, 2517, 7898,  256, 16320, 16320,  256,  256 }, // 356.25,1916,482.75,629.25,1974.5,64,4080,4080,64,64
  {   50,  100,  100,   50,  100,  100,   100,   100,  100,  100 },
  {   50,  100,  100,   50,  100,  100,   100,   100,  100,  100 }
};

static const Pose POSE_EXT = {
  "EXT",
  { 5948, 5402, 9535, 6416, 6260, 9457,  256,  256, 16320, 16320 }, // 1487,1350.5,2383.75,1604,1565,2364.25,64,64,4080,4080
  {   50,  100,  100,   50,  100,  100,  100,  100,   100,   100 },
  {   50,  100,  100,   50,  100,  100,  100,  100,   100,   100 }
};
// -------------------------------------------------------------------

HardwareSerial Maestro(1);
static BLECharacteristic* gStatus = nullptr;
static bool gBleConnected = false;
static bool gDebug = false;
// ----------------- Maestro low-level -----------------
static inline void write7(uint16_t v){
  Maestro.write((uint8_t)(v & 0x7F));
  Maestro.write((uint8_t)((v >> 7) & 0x7F));
}

static void maestroSetSpeed(uint8_t ch, uint16_t v){
  if (ch >= MAESTRO_CH) return;
  Maestro.write((uint8_t)0x87); Maestro.write(ch); write7(v);
}

static void maestroSetAccel(uint8_t ch, uint16_t v){
  if (ch >= MAESTRO_CH) return;
  Maestro.write((uint8_t)0x89); Maestro.write(ch); write7(v);
}

// Exact raw target in quarter-microseconds
static void maestroSetTargetQ(uint8_t ch, uint16_t q){
  if (ch >= MAESTRO_CH) return;
  Maestro.write((uint8_t)0x84); Maestro.write(ch); write7(q);
}

static void maestroSetTargetUS(uint8_t ch, uint16_t us){
  if (ch >= MAESTRO_CH) return;

  if (CLAMP_ENABLE && us != 0){
    if (us < CLAMP_MIN_US) us = CLAMP_MIN_US;
    if (us > CLAMP_MAX_US) us = CLAMP_MAX_US;
  }
  maestroSetTargetQ(ch, (uint16_t)(us * 4));
}

// ----------------- BLE notify -----------------
static void notify(const char* s){
  if (!gStatus || !gBleConnected) return;
  gStatus->setValue((uint8_t*)s, strlen(s));
  gStatus->notify();
}

static void notifyf(const char* fmt, ...){
  char buf[96];
  va_list ap;
  va_start(ap, fmt);
  vsnprintf(buf, sizeof(buf), fmt, ap);
  va_end(ap);
  notify(buf);
}

static void maestroResetPulse(){
  digitalWrite(RST_PIN, LOW);
  delay(20);
  digitalWrite(RST_PIN, HIGH);
  notify("RST");
}

// ----------------- Pump -----------------
static bool pumpOn = false;

static void pumpApply(bool on){
  pumpOn = on;
  if (RELAY_ACTIVE_HIGH) digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  else                  digitalWrite(RELAY_PIN, on ? LOW  : HIGH);
  notify(on ? "PUMP=ON" : "PUMP=OFF");
}

// ----------------- Pose / Sequence engine -----------------
enum Act : uint8_t { IDLE=0, SEQ_EXT=1 };
static volatile Act act = IDLE;
static uint8_t stepIdx = 0;
static uint32_t nextMs = 0;

static void applyPose(const Pose& p){
  for (uint8_t ch=0; ch<PCH; ch++){
    maestroSetSpeed(ch, p.sp[ch]);
    maestroSetAccel(ch, p.ac[ch]);
  }
  for (uint8_t ch=0; ch<PCH; ch++){
    maestroSetTargetQ(ch, p.q[ch]);
  }
  notifyf("POSE=%s", p.name);
}

static void startSeqExt(){
  act = SEQ_EXT;
  stepIdx = 0;
  nextMs = 0;
  notify("SEQ=START");
}

static void stopSequence(){
  act = IDLE;
  stepIdx = 0;
  nextMs = 0;
  notify("SEQ=STOP");
}

static void tickActions(){
  if (act == IDLE) return;
  uint32_t now = millis();
  if (now < nextMs) return;

  // lift -> rot -> ext
  if (act == SEQ_EXT){
    if      (stepIdx == 0){ applyPose(POSE_LIFT); nextMs = now + T_LIFT; stepIdx++; }
    else if (stepIdx == 1){ applyPose(POSE_ROT ); nextMs = now + T_ROT;  stepIdx++; }
    else if (stepIdx == 2){ applyPose(POSE_EXT ); nextMs = now + T_EXT;  stepIdx++; }
    else { act = IDLE; notify("SEQ=DONE"); }
  }
}

// ----------------- Command queue -----------------
struct Msg { char s[96]; };
static QueueHandle_t q = nullptr;

class ServerCB : public BLEServerCallbacks {
  void onConnect(BLEServer*) override { gBleConnected = true; }
  void onDisconnect(BLEServer* s) override { gBleConnected = false; s->startAdvertising(); }
};

class ControlCB : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* c) override {
    const uint8_t* data = c->getData();
    size_t len = c->getLength();
    if (!data || !len) return;

    Msg m{};
    size_t n = (len >= sizeof(m.s)) ? sizeof(m.s)-1 : len;
    memcpy(m.s, data, n);
    m.s[n] = 0;

    if (q && xQueueSend(q, &m, 0) != pdTRUE){
      notify("ERR:queue");
    }
  }
};

// ----------------- Parsing helpers -----------------
static void toLowerInPlace(char* s){
  for (; *s; s++) *s = (char)tolower((unsigned char)*s);
}

static void trimInPlace(char* s){
  if (!s) return;
  size_t len = strlen(s);
  while (len && (s[len-1] == '\r' || s[len-1] == '\n' || s[len-1] == ' ' || s[len-1] == '\t')) s[--len] = 0;
  char* p = s;
  while (*p && (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n')) p++;
  if (p != s) memmove(s, p, strlen(p) + 1);
}

static bool parseChUs(const char* s, uint8_t& ch, uint16_t& us){
  int a=-1, b=-1;
  if (sscanf(s, "%d,%d", &a, &b) != 2){
    if (sscanf(s, "%d %d", &a, &b) != 2) return false;
  }
  if (a < 0 || a >= MAESTRO_CH) return false;
  if (b < 0 || b > 65535) return false;
  ch = (uint8_t)a;
  us = (uint16_t)b;
  return true;
}

static void debugEcho(const char* cmd){
  if (!gDebug) return;
  notifyf("DBG:%s", cmd);
}

// ----------------- Command handler -----------------
static void handleCmd(char* s){
  if (!s || !*s) return;
  trimInPlace(s);
  if (!*s) return;

  // normalize
  toLowerInPlace(s);

  // pump
  if (!strncmp(s, "pump", 4)){
    if (strstr(s, "on")) pumpApply(true);
    else if (strstr(s, "off")) pumpApply(false);
    else pumpApply(!pumpOn);
    debugEcho(s);
    return;
  }

  // pose (instant apply, does not block)
  if (!strncmp(s, "pose", 4)){
    if (strstr(s, "lift") || strstr(s, "soul")) { applyPose(POSE_LIFT); debugEcho(s); return; }
    if (strstr(s, "rot"))                      { applyPose(POSE_ROT);  debugEcho(s); return; }
    if (strstr(s, "ext"))                      { applyPose(POSE_EXT);  debugEcho(s); return; }
    notify("ERR:pose");
    return;
  }

  // seq
  if (!strncmp(s, "seq", 3)){
    if (strstr(s, "stop")) { stopSequence(); return; }
    if (strstr(s, "ext")){
      startSeqExt();
      return;
    }
    notify("ERR:seq");
    return;
  }

  // motion limits
  if (!strncmp(s, "sp ", 3)){
    int ch=-1, v=-1;
    if (sscanf(s, "sp %d %d", &ch, &v) == 2 && ch >= 0 && ch < MAESTRO_CH && v >= 0){
      maestroSetSpeed((uint8_t)ch, (uint16_t)v);
      notify("OK:sp");
      debugEcho(s);
    } else notify("ERR:sp");
    return;
  }

  if (!strncmp(s, "ac ", 3)){
    int ch=-1, v=-1;
    if (sscanf(s, "ac %d %d", &ch, &v) == 2 && ch >= 0 && ch < MAESTRO_CH && v >= 0){
      maestroSetAccel((uint8_t)ch, (uint16_t)v);
      notify("OK:ac");
      debugEcho(s);
    } else notify("ERR:ac");
    return;
  }

  if (!strncmp(s, "debug ", 6)){
    if (strstr(s, "on")) gDebug = true;
    else if (strstr(s, "off")) gDebug = false;
    notify(gDebug ? "DBG=ON" : "DBG=OFF");
    return;
  }

  if (!strncmp(s, "rst", 3) || !strncmp(s, "reset", 5)){
    maestroResetPulse();
    return;
  }

  // manual servo set "ch,us"
  if (act != IDLE){
    uint8_t ch; uint16_t us;
    if (parseChUs(s, ch, us)){
      notify("ERR:busy");
      return;
    }
  }

  uint8_t ch; uint16_t us;
  if (parseChUs(s, ch, us)){
    maestroSetTargetUS(ch, us);
    notifyf("OK:ch=%u us=%u", (unsigned)ch, (unsigned)us);
    debugEcho(s);
    return;
  }

  notify("ERR:cmd");
}

static void processLine(char* line){
  trimInPlace(line);
  if (!*line) return;
  handleCmd(line);
}

static void processRaw(char* s){
  trimInPlace(s);
  if (!*s) return;
  char* start = s;
  while (*start){
    char* end = start;
    while (*end && *end != '\n' && *end != ';') end++;
    if (*end){
      *end = 0;
      processLine(start);
      start = end + 1;
    }else{
      processLine(start);
      break;
    }
  }
}

void setup(){
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pumpApply(false);

  pinMode(RST_PIN, OUTPUT);
  digitalWrite(RST_PIN, HIGH);

  Maestro.begin(MAESTRO_BAUD, SERIAL_8N1, MAESTRO_RX_PIN, MAESTRO_TX_PIN);

  q = xQueueCreate(12, sizeof(Msg));

  BLEDevice::init(DEV_NAME);
  BLEServer* server = BLEDevice::createServer();
  server->setCallbacks(new ServerCB());

  BLEService* svc = server->createService(SERVICE_UUID);

  BLECharacteristic* control = svc->createCharacteristic(
    CONTROL_UUID,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
  );
  control->setCallbacks(new ControlCB());

  gStatus = svc->createCharacteristic(STATUS_UUID, BLECharacteristic::PROPERTY_NOTIFY);
  gStatus->addDescriptor(new BLE2902());

  svc->start();

  BLEAdvertising* adv = BLEDevice::getAdvertising();
  adv->addServiceUUID(SERVICE_UUID);
  adv->setScanResponse(true);
  BLEDevice::startAdvertising();

  if (!q) notify("ERR:queue_init");
  notify("BOOT");
}

void loop(){
  tickActions();

  Msg m;
  while (q && xQueueReceive(q, &m, 0) == pdTRUE){
    processRaw(m.s);
  }
  delay(2);
}
