# 🦾 ESP32 Dual-Arm Control Firmware (Pololu Maestro)

## Overview
This firmware is a **test and calibration unit** designed to validate the movement of two 3-DOF robotic arms (Left & Right). It interfaces an **ESP32** with a **Pololu Mini Maestro** servo controller using a direct UART connection. 

Unlike the full system code, this lightweight version focuses solely on servo kinematics, allowing you to toggle the arms between an "Extended" state (for pickup/drop) and an "Internal" state (safe/storage) without engaging the linear rail or pneumatics.

## 🛠 Hardware Configuration
* **Microcontroller:** ESP32
* **Servo Driver:** Pololu Mini Maestro 12-Channel
* **Communication:** UART (Compact Protocol) @ 9600 baud
* **Actuators:** 6x Servos (3 per arm: Shoulder, Elbow, Wrist)

### 🔌 Pinout
| ESP32 Pin | Connection |
| :--- | :--- |
| **GPIO 17** | TX $\to$ Maestro RX |
| **GPIO 16** | RX $\leftarrow$ Maestro TX |
| **5V / GND** | Power to Maestro Logic |

## 🕹 Usage
Flash the code and open the Serial Monitor at **115200 baud**.

### Serial Commands
* `e` : **Extend** (Move arms to Pickup/Drop position).
* `i` : **Internal** (Retract arms to safe Home position).
* `d` : **Demo** (Runs an automatic cycle: Extend $\to$ Wait $\to$ Retract).

## ⚙️ Calibration Data
The code uses hardcoded servo pulse widths (in quarter-microseconds) derived from physical calibration.
* **Positions Defined:**
    * `POSE_PICKUP`: Arms extended outwards.
    * `POSE_INTERNAL`: Arms folded inside the chassis.
* **Note:** The "Drop" position is currently mapped identically to the "Pickup" position for this test.
