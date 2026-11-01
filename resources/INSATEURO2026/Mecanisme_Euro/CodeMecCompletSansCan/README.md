# Dual-Arm Robot Controller with Linear Rail & Internal Storage

This firmware controls a specialized pick-and-place robot featuring a linear rail, two servo-driven arms, and **two independently rotating internal storage units** (180° range). The system manages complex sequences to pick items, store them internally, and deploy them later.

## 1. Features

* **Linear Rail Control:** High-speed stepper motion with limit-switch homing and multiple pickup zones.
* **Dual Manipulators:** Two 3-DOF arms (Shoulder, Elbow, Wrist) for external interaction.
* **Split Internal Storage:** Two independent storage bays that rotate 180° (Flat/Safe <-> Tilted/Storage).
* **Pneumatic System:** Integrated control for a vacuum pump and 4 independent suction valves.
* **Automated Sequences:** Pre-programmed routines for picking, storing, holding, and dropping items.

## 2. Hardware Configuration

### **Pin Map (ESP32)**

| Subsystem | Pin Name | GPIO | Note |
| :--- | :--- | :--- | :--- |
| **Rail (Stepper)** | Step | `33` | |
| | Dir | `32` | |
| | Bumper | `14` | Active HIGH (Pulldown) |
| **Servos (Maestro)** | RX | `16` | Connect to Maestro TX |
| | TX | `17` | Connect to Maestro RX |
| **Pneumatics (I2C)** | SDA | `21` | |
| | SCL | `22` | Address `0x20` |

### **Servo Channel Map (Pololu Maestro)**

| Channel | Function |
| :--- | :--- |
| **0-2** | Arm 1 (Shoulder, Elbow, Wrist) |
| **3-5** | Arm 2 (Shoulder, Elbow, Wrist) |
| **6** | Rotation Unit 1 (Left) |
| **7** | Rotation Unit 2 (Right) |

---

## 3. Installation

1.  **Dependencies:** Install the following libraries via Arduino Library Manager or PlatformIO:
    * `AccelStepper` (Mike McCauley)
    * `Adafruit MCP23017` (Adafruit)
    * `Wire` (Built-in)
2.  **Upload:** Flash the firmware to your ESP32.
3.  **Power:** Ensure the 24V/12V power supplies for the Stepper and Servos are ON before booting the ESP32.

---

## 4. Control Commands (Serial Monitor)

Connect via USB at **115200 baud**.

### **Rail & Homing**
| Key | Command | Description |
| :--- | :--- | :--- |
| `H` | **Home Rail** | **Must be run first.** Finds the limit switch to calibrate position. |
| `M` | **Move to Pickup 1** | Moves rail to Position 100. |
| `N` | **Move to Pickup 2** | Moves rail to Position 280. |

### **Complex Sequences**
| Key | Command | Logic |
| :--- | :--- | :--- |
| `p` | **Pickup & Store** | Arms pick item -> Retract -> Place into internal storage -> Release. |
| `P` | **Pickup & Hold** | Arms pick item -> Retract -> Hold item (used when storage is full). |
| `d` | **Drop (Arms)** | Arms extend -> Release held items -> Retract. |
| `D` | **Drop (Storage)** | Arms reach internal -> Vacuum transfer -> Arms extend -> Release. |

### **Independent Rotation (Manual)**
| Key | Command | Description |
| :--- | :--- | :--- |
| `1` | **Unit 1 TILT** | Rotates Left Storage to **180°** (Storage Mode). |
| `2` | **Unit 1 FLAT** | Rotates Left Storage to **0°** (Safe Mode). |
| `3` | **Unit 2 TILT** | Rotates Right Storage to **180°** (Storage Mode). |
| `4` | **Unit 2 FLAT** | Rotates Right Storage to **0°** (Safe Mode). |

---

## 5. Calibration Notes

### **Rotation Limits (180°)**
The firmware uses extended pulse widths to achieve 180° rotation on standard servos.
* **0° (Flat):** Target `2000` (~500µs)
* **180° (Tilt):** Target `10000` (~2500µs)

> **Warning:** Ensure your servos are mechanically capable of this range. If they buzz or stall, adjust `ROT_FLAT` and `ROT_TILT` in the code immediately to prevent damage.

### **Rail Coordinates**
Modify these macros in `main.cpp` to adjust stopping points:
```cpp
#define RAIL_POS_PICKUP_1   100
#define RAIL_POS_PICKUP_2   280
