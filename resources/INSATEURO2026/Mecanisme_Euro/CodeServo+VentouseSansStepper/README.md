# 🦾 Dual-Arm Pneumatic Robot Control with Independent Internal Storage (4-Crate Capacity)

This firmware controls a dual-arm pick-and-place robot featuring **two independently rotating internal storage units**. It is designed to run on an ESP32, interfacing with a Pololu Maestro servo controller and an MCP23017 I/O expander for pneumatic control.

## 1. System Overview

The robot is capable of complex object manipulation sequences:
1.  **Pick objects** from an external location using two 3-DOF arms.
2.  **Store objects internally** by transferring them to rotating storage bays (Unit 1 & Unit 2).
3.  **Tilt storage units independently** (0° Flat to 180° Vertical) to compact the robot or secure items during transport.
4.  **Hold objects** with the arms if storage is full.
5.  **Drop objects** either directly from the arms or by retrieving them from internal storage.

## 2. Hardware Configuration

### **Pin Map (ESP32)**

| Subsystem | Pin Name | GPIO | Connection |
| :--- | :--- | :--- | :--- |
| **Servos (Maestro)** | RX | `16` | Connect to Maestro TX |
| | TX | `17` | Connect to Maestro RX |
| **Pneumatics (I2C)** | SDA | `21` | |
| | SCL | `22` | Address `0x20` |

### **Servo Channel Map (Pololu Maestro)**

| Channel | Function | Description |
| :--- | :--- | :--- |
| **0-2** | Arm 1 | Shoulder, Elbow, Wrist |
| **3-5** | Arm 2 | Shoulder, Elbow, Wrist |
| **6** | **Storage Unit 1 (Left)** | Rotation (0-180°) |
| **7** | **Storage Unit 2 (Right)** | Rotation (0-180°) |

### **Pneumatic Valve Map (MCP23017)**

| Index | Name | Function |
| :--- | :--- | :--- |
| **0** | `SUCKER_ARM_1` | Suction cup on Arm 1 |
| **1** | `SUCKER_ARM_2` | Suction cup on Arm 2 |
| **2** | `SUCKER_INT_1` | Internal Sucker for Unit 1 |
| **3** | `SUCKER_INT_2` | Internal Sucker for Unit 2 |

---

## 3. Installation

1.  **Libraries:** Install the following libraries via PlatformIO or Arduino Library Manager:
    * `Adafruit MCP23017`
    * `Wire` (Standard Arduino Library)
2.  **Upload:** Flash the `main.cpp` code to your ESP32.
3.  **Power Up:**
    * Ensure the **Maestro Servo Controller** has clean 5V-6V power.
    * Ensure the **Pump/Valves** have 12V/24V power.
    * Boot the ESP32.

---

## 4. Control Commands (Serial Monitor)

Connect via USB at **115200 baud**.

### **Automated Sequences**

| Key | Command | Logic |
| :--- | :--- | :--- |
| `h` | **Home All** | Moves arms to safe position, flattens both storage units. |
| `p` | **Pickup & Store** | Arms pick -> Retract -> **Store in Units** -> Arms Release. |
| `P` | **Pickup & Hold** | Arms pick -> Retract -> **Arms Hold** (Used when storage full). |
| `d` | **Drop (Arms)** | Arms extend -> Release held items -> Retract. |
| `D` | **Drop (Storage)** | Arms grab internal items -> Extend -> Release -> Retract. |

### **Manual Rotation Control**

| Key | Function | Description |
| :--- | :--- | :--- |
| `1` | **Unit 1 TILT** | Rotates Left Storage to **180°** (Vertical/Stored). |
| `2` | **Unit 1 FLAT** | Rotates Left Storage to **0°** (Horizontal/Receiving). |
| `3` | **Unit 2 TILT** | Rotates Right Storage to **180°** (Vertical/Stored). |
| `4` | **Unit 2 FLAT** | Rotates Right Storage to **0°** (Horizontal/Receiving). |

---

## 5. Calibration

### **Rotation Limits**
The code uses Maestro pulse width units (0.25µs). The defaults are set for standard 180° servos (1000µs to 2000µs).
* **Flat (0°):** `4000` (1000µs)
* **Tilt (180°):** `8000` (2000µs)

*If your servos require a wider range (e.g., 500µs - 2500µs) to hit 180°, edit these macros in `main.cpp`:*
```cpp
#define ROT_FLAT   2000   // 500us
#define ROT_TILT   10000  // 2500us
