# Technical Description: Dual-Arm "Hybrid" Sorting Robot

## 1. System Overview
This system is an autonomous **Pick-and-Place module** designed to collect, store, transport, and deposit objects (crates/samples). Unlike standard robotic arms that move one object at a time, this robot uses a **Hybrid Buffer Strategy** to maximize carrying capacity:
1.  **Internal Storage:** It stores 2 objects passively on its chassis.
2.  **Active Holding:** It holds 2 additional objects actively with its robotic arms.
3.  **Total Capacity:** 4 Objects simultaneous transport.

## 2. Mechanical Architecture

### A. Linear Motion (The Rail)
The entire robot assembly is mounted on a linear rail (Gantry).
* **Actuator:** Stepper Motor (controlled via `AccelStepper`).
* **Feedback:** A physical limit switch (`BUMPER_PIN`) is used for **Homing** (Zero Calibration).
* **Positions:**
    * `RAIL_POS_PICKUP_1`: First Pickup Zone (Lot 1).
    * `RAIL_POS_PICKUP_2`: Second Pickup Zone (Lot 2).

### B. Dual Robotic Arms (Manipulators)
The robot features two symmetrical arms (Left/Arm 1 and Right/Arm 2).
* **Degrees of Freedom:** 3 DOF per arm (Shoulder, Elbow, Wrist).
* **Actuators:** Servomotors controlled via PWM (Pololu Maestro Channels 0-5).
* **Kinematics:**
    * `POSE_PICKUP_EXTERNAL`: Extended outwards to grab/drop objects.
    * `POSE_GRIP_INTERNAL`: Retracted inwards to transfer objects to storage or hold them during transport.

### C. Rotating Internal Storage
Located between the arms are two passive storage slots that can rotate to accommodate different object orientations or stacking requirements.
* **Actuators:** 2 Servomotors (Pololu Maestro Channels 6 & 7).
* **States:** `Flat` (0°) or `Tilted` (90°).

## 3. Pneumatic System (Gripping & Storage)
The robot uses vacuum suction for both manipulation and internal storage. It manages **4 independent vacuum channels**.

* **Source:** 1 Main Vacuum Pump (Pin `POMPE`).
* **Distribution:** 4 Solenoid Valves (controlled via **MCP23017**).

**Pneumatic Mapping:**

| Index | Valve Name | Function |
| :--- | :--- | :--- |
| **0** | `SUCKER_ARM_1` | **Dynamic:** Left Arm Gripper |
| **1** | `SUCKER_ARM_2` | **Dynamic:** Right Arm Gripper |
| **2** | `SUCKER_INT_1` | **Static:** Internal Storage Slot 1 |
| **3** | `SUCKER_INT_2` | **Static:** Internal Storage Slot 2 |

## 4. Electronic Control Architecture

* **Main Controller: ESP32**
    * **Function:** Handles logic, sequencing, kinematics, and serial communication.
    * **Interface:** USB Serial (115200 baud) for commands.

* **Servo Controller: Pololu Mini Maestro (12-Channel)**
    * **Connection:** UART2 (`GPIO 17` TX / `GPIO 16` RX).
    * **Function:** Generates precise PWM signals for **8 Servos** (6 Arm Servos + 2 Rotation Servos).
    * **Protocol:** Uses Pololu "Compact Protocol" for target, speed, and acceleration control.

* **IO Expansion: MCP23017**
    * **Connection:** I2C (`GPIO 21` SDA / `GPIO 22` SCL).
    * **Address:** `0x20`.
    * **Function:** Drives the **4 Solenoid Valves** + **1 Vacuum Pump** Relay.

* **Stepper Driver (Linear Rail)**
    * **Interface:** Standard STEP/DIR driver (e.g., A4988/TB6600).
    * **Pins:**
        * Step: `GPIO 33`
        * Direction: `GPIO 32`
    * **Sensors:**
        * Limit Switch (Bumper): `GPIO 14` (Input Pull-down).



## 5. Operational Sequence (The "Hybrid" Logic)
The robot operates using a **FIFO (First-In, First-Out)** strategy for loading, managing capacity via two distinct pickup modes and two drop modes.

### Phase 1: Loading (Capacity 0 $\to$ 4)
1.  **Pickup 1 (Store Internally)**
    * Arms extend and grab 2 objects.
    * Arms retract to `POSE_GRIP_INTERNAL`.
    * **Handoff:** Internal Suckers (2 & 3) turn ON; Arm Suckers turn OFF.
    * *Status: 2 Objects Stored, Arms Free.*
2.  **Pickup 2 (Active Hold)**
    * Robot moves to next rail position.
    * Arms extend and grab 2 *new* objects.
    * Arms retract to `POSE_GRIP_INTERNAL` and **keep holding** the objects.
    * *Status: 2 Objects Stored, 2 Objects in Arms (Full Capacity).*

### Phase 2: Unloading (Capacity 4 $\to$ 0)
1.  **Drop 1 (From Arms)**
    * Arms extend outwards (`POSE_PICKUP_EXTERNAL`).
    * Arm Suckers turn OFF to release objects.
    * Arms retract.
    * *Status: 2 Objects Stored, Arms Free.*
2.  **Drop 2 (From Storage)**
    * Arms retract to `POSE_GRIP_INTERNAL`.
    * **Retrieve:** Arm Suckers turn ON; Internal Suckers turn OFF.
    * Arms extend outwards.
    * Arm Suckers turn OFF to release.
    * *Status: System Empty.*

## 6. Safety Features
* **Active Homing:** Rail must be homed (`H`) before movement commands (`M`/`N`) are accepted.
* **Soft Starts:** Servos use acceleration limits to prevent jerking heavy crates.
* **Pump Priority:** Pump is enabled immediately upon boot to ensure vacuum availability.l collision with the environment.
