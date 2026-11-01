# 💨 ESP32 Pneumatic Control System (6 Channels)

## Overview
This firmware interfaces an **ESP32** with an **MCP23017 I/O Expander** (via I2C) to control a pneumatic system consisting of **6 independent suction cups (suckers)** and **1 main vacuum pump**. 

It allows for individual control of each channel via Serial commands, making it suitable for granular pick-and-place operations.

## 🛠 Hardware Configuration
* **Microcontroller:** ESP32
* **I/O Expander:** MCP23017 (Address `0x20`)
* **Communication:** I2C (SDA/SCL)
* **Actuators:**
    * **1x Vacuum Pump** (Relay controlled).
    * **6x Solenoid Valves** (Individual suckers).

### 🔌 MCP23017 Pinout
| Component | MCP Pin ID |
| :--- | :--- |
| **Pump Relay** | Pin 8 |
| **Sucker 1** | Pin 7 |
| **Sucker 2** | Pin 6 |
| **Sucker 3** | Pin 5 |
| **Sucker 4** | Pin 4 |
| **Sucker 5** | Pin 3 |
| **Sucker 6** | Pin 2 |

## 🕹 Serial Commands (115200 baud)
The system uses single-character commands for fast switching.

| Action | Key (ON) | Key (OFF) | Description |
| :--- | :--- | :--- | :--- |
| **Sucker 1** | `1` | `a` | Control Valve 1 |
| **Sucker 2** | `2` | `b` | Control Valve 2 |
| **Sucker 3** | `3` | `c` | Control Valve 3 |
| **Sucker 4** | `4` | `d` | Control Valve 4 |
| **Sucker 5** | `5` | `e` | Control Valve 5 |
| **Sucker 6** | `6` | `f` | Control Valve 6 |
| **Pump** | `P` | `p` | Main Pump Power |
| **E-STOP** | `Z` | `z` | **Emergency Stop** (All OFF) |

## ⚠️ Logic Note
The Pump logic is configured for **Active LOW** relays (Standard relay modules):
* **ON** sends `LOW` signal.
* **OFF** sends `HIGH` signal.
* Valves are configured as standard Active HIGH (High = Open).
