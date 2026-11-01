# 🚂 ESP32 Linear Rail Control (Short Rail)

## Overview
This code controls a **stepper motor linear rail** using an **ESP32** and the `AccelStepper` library. It is designed for a "Short Rail" setup (320 steps total) and features safety mechanisms for homing and collision detection.

## 🛠 Hardware Configuration
* **Microcontroller:** ESP32
* **Driver:** A4988 / DRV8825 (STEP/DIR interface)
* **Sensor:** Mechanical Limit Switch (Bumper) for Homing (Zero).
* **Wiring:**
    * **Step:** GPIO 33
    * **Dir:** GPIO 32
    * **Bumper:** GPIO 14 (Wired to 3.3V, Pulldown logic)

## 📍 Defined Positions (Steps)
* **Home (0):** Defined by the limit switch.
* **POS_PICKUP (150):** First working zone.
* **POS_PICKUP2 (220):** Second working zone .
* **Max Limit (320):** Soft limit to prevent crashing into the far end.

## 🕹 Serial Commands (115200 baud)
| Key | Function | Description |
| :--- | :--- | :--- |
| `H` | **Home** | Calibrates zero using the limit switch. Must be done first. |
| `P` | **Pickup 1** | Moves to position 100. |
| `D` | **Pickup 2** | Moves to position 280. |
| `Z` | **Zero** | Returns to start (0). |
| `S` | **Stop** | Emergency stop during movement. |
| `F` | **Forward** | Manually moves +50 steps. |
| `B` | **Back** | Manually moves -50 steps. |

## ⚠️ Safety Features
1.  **Homing Requirement:** Movements are blocked until `H` is executed.
2.  **Soft Limits:** Prevents commands < 0 or > 320.
3.  **Crash Detection:** If the bumper is hit while the robot thinks it is far from home (>50 steps), it triggers an emergency stop and resets calibration.
