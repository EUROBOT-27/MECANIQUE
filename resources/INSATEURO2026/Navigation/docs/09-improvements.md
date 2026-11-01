# 9. Future Code Improvements & Recommendations


### 1. Differential Drive Inverse Kinematics
Explore implementing full **inverse kinematics** for differential drive robots. Top-tier Eurobot teams use this approach in their navigation system.

### 2. Smooth Trajectory Generation & Faster State Transitions
Our current `GoToXY` algorithm executes motion in discrete phases:  (`Nav_GoToXY_Rotate_en`, `Nav_GoToXY_Forward_en`, `Nav_GoToXY_RotateAfter_en`). 

* **The Problem:** The robot halts briefly between states to satisfy tight settling thresholds (a few millimeters/degrees), slowing down overall path completion.
* **Solutions to Explore:**
  * **Optimized Phase Transition:** Some teams use this type of this trajectory and their robots are extremely fast(look into EsialRobotik team)
  * **Curvilinear Trajectories:** Transition to continuous curved trajectories (blending linear and angular motions simultaneously). Refer to [Trajectoire Courbe (PDF)](https://techthetroll.wordpress.com/wp-content/uploads/2016/07/trajectoire_courbe.pdf) for a detailed mathematical breakdown of curve-based navigation(this is a eurobot team that documented it) .
  * **Hybrid Approach:** Combine point-to-point motion for tight maneuvers with curvilinear paths for long-distance navigation.

### 3. Dynamic Target Angle during linear motion
The CurrentTargetAngle calculations in the forward linear trajectory in the independenttrajectorystate function were made with the purpose of helping the robot to stay in line since pid_angle can react late.The issue is that it gives a huge target angle(2 to 3 degrees) which the rpbpt may not be able to correct before reaching its destination.Look more into cross-Track error correction to find a better alternative.

### 4. S-Curve (Jerk-Limited) Velocity Profiles
Replacing the current **trapezoidal profile** with an **S-curve (jerk-limited) profile** will eliminate infinite jerk during acceleration phase transitions, significantly reducing mechanical wear and wheel slip.

>**Important:** If you implement S-curve profiling after tuning your robot on a trapezoidal profile, **you may have to re-tune the PID controller gains**.

### 5. Simplification of State Machine Architecture
Refactor the current **4-level nested state machine** hierarchy .

### 6. Hardware Floating-Point Optimization (FPU)
Convert all floating-point calculations from standard double-precision `double` to single-precision `float`. Ensure the target MCU's hardware **Floating-Point Unit (FPU)** is enabled in your compiler/IDE configuration to maximize math execution speed in the core feedback loop.



