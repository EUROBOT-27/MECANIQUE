# ESP32 Dual-Arm Robot Controller (Linear Rail + Internal Storage)

This firmware controls a complex pick-and-place robot featuring **two servo-driven arms**, **a linear rail**, and **two rotating internal storage bays**. The system is designed to pick up objects, store them internally (using 180° rotation mechanisms), and deposit them sequentially.

It acts as a **CAN Bus Node** controlled by a main system but also supports **Serial Debugging**.

## 1. Hardware Architecture

### **Microcontroller & Comms**
* **MCU:** ESP32 (DevKit V1 or similar)
* **CAN Bus:** Native ESP32 TWAI driver (Requires Transceiver like SN65HVD230).
* **Servo Controller:** Pololu Maestro (via UART2).
* **Pneumatics:** MCP23017 I/O Expander (via I2C).

### **Pinout Configuration**

| Subsystem | Function | Pin / Address | Details |
| :--- | :--- | :--- | :--- |
| **Rail** | Step | **GPIO 33** | Stepper Driver |
| | Dir | **GPIO 32** | Stepper Driver |
| | Bumper | **GPIO 14** | Active HIGH (Pulldown Config) |
| **CAN Bus** | RX | **GPIO 4** | |
| | TX | **GPIO 5** | |
| **Servos** | RX | **GPIO 16** | To Maestro TX |
| | TX | **GPIO 17** | To Maestro RX |
| **Pneumatics** | SDA | **GPIO 21** | I2C |
| | SCL | **GPIO 22** | I2C |
| | Address | `0x20` | MCP23017 |

---

## 2. Servo & Rotation Configuration

The robot uses a **Pololu Maestro** to drive 8 channels.

### **Rotation Mechanism (180°)**
The internal storage bays rotate between "Flat" (Safe/Up) and "Tilt" (Storage/Down). The pulse width range is expanded to allow full 180° travel.
* **Flat (0°):** Target `2000` (approx 500µs)
* **Tilt (180°):** Target `10000` (approx 2500µs)

### **Channel Map**
* **0-2:** Arm 1 (Shoulder, Elbow, Wrist)
* **3-5:** Arm 2 (Shoulder, Elbow, Wrist)
* **6:** Rotation Unit 1 (Left)
* **7:** Rotation Unit 2 (Right)

---

## 3. Communication Protocol

### **A. CAN Bus Interface**
* **Baud Rate:** 500 kbps
* **Command ID (RX):** `0x100`
* **Response ID (TX):** `0x103` (Returns status byte upon completion)

#### **Command Table**

| HEX | Function | Description |
| :--- | :--- | :--- |
| **0xFF** | `HOME_ALL` | Homes rail, resets arms, flats storage. **Required on startup.** |
| **0x01** | `PICKUP_STORE` | Pick item -> Place in internal storage. |
| **0x02** | `PICKUP_HOLD` | Pick item -> Hold on arms (Storage remains full). |
| **0x03** | `DROP_ARMS` | Drop items currently held by arms. |
| **0x04** | `DROP_STORE` | Retrieve items from storage -> Drop them. |
| **0x11** | `ROT_1_TILT` | Rotate Unit 1 to **180°** (Storage). |
| **0x12** | `ROT_1_FLAT` | Rotate Unit 1 to **0°** (Safe). |
| **0x13** | `ROT_2_TILT` | Rotate Unit 2 to **180°** (Storage). |
| **0x14** | `ROT_2_FLAT` | Rotate Unit 2 to **0°** (Safe). |
| **0x20** | `EMERGENCY` | **HARD STOP.** Stops stepper, cuts pump & valves. |

---

### **B. Serial Monitor Controls**
Connect via USB at **115200 baud** for manual debugging.

| Key | Action |
| :--- | :--- |
| `H` | Home Rail & Reset System |
| `p` / `P` | Run Sequence: Pickup Store / Pickup Hold |
| `d` / `D` | Run Sequence: Drop Arms / Drop Storage |
| `1` / `2` | Unit 1: Tilt (180°) / Flat (0°) |
| `3` / `4` | Unit 2: Tilt (180°) / Flat (0°) |

---

## 4. Sequence Logic

The robot is designed to carry a maximum of **4 items** (2 inside, 2 on arms).

1.  **Pickup Store (Sequence 1):**
    * Arms pick up items from external source.
    * Arms retract and place items into the internal storage bays.
2.  **Pickup Hold (Sequence 2):**
    * Arms pick up new items and hold them (assuming storage is already full).
3.  **Drop Arms (Sequence 3):**
    * Arms extend and release the items they are holding.
4.  **Drop Storage (Sequence 4):**
    * Arms reach internally, vacuum is transferred from storage to arms.
    * Arms extend outwards and release.

---

## 5. Setup & Installation

### **Dependencies**
Ensure these libraries are installed in `platformio.ini` or Arduino Library Manager:
1.  **AccelStepper** (Mike McCauley)
2.  **Adafruit MCP23017** (Adafruit)
3.  **Wire** (Standard)

### **Safety Notes**
1.  **Homing:** The rail will not move to specific coordinates until `HOME_ALL` (0xFF or 'H') is successfully completed.
2.  **Servo Limits:** Ensure your rotation servos are mechanically capable of **180° rotation**. Sending a `10000` target (2500µs) to a standard 90° servo may damage its gears.
3.  **Power:** Ensure the Servo Controller (Maestro) and Pneumatic Pump have sufficient external power separate from the ESP32 USB.
