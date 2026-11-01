# Introduction 

This repository provides a low-level state-estimation and motion control system designed for a differential-drive mobile robot. The system combines real-time positioning with smooth, controlled trajectory execution through three core pillars:

* **Encoder Odometry:** Continuously tracks the robot's global pose (X, Y, theta) using high-frequency encoder feedback .
* **Trapezoidal Velocity Profiling:** Manages acceleration, cruise, and deceleration phases to guarantee smooth, predictable motion.
* **Polar PD Control:** Stabilizes trajectory tracking by independently regulating linear distance and angular heading errors.

---

### Recommended Reading
* **[Cubot - Atelier Asservissement (PDF)](https://github.com/VRAC-team/la-maxi-liste-ressources-eurobot/blob/master/asservissement/Cubot-atelier_asservissement.pdf):** A good starting point that covers the fundamentals of PID control, odometry math, and trapezoidal velocity profiling in a clear, practical way. Reading this first is highly recommended before exploring the rest of the codebase.

>  **Note:** The core control loops,odometry,motion profiles and state machine logic are implemented in `NavStateMachineTest.c`.