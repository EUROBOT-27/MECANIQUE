# 5. Odometry 

 ### Ressources to read:
https://github.com/VRAC-team/la-maxi-liste-ressources-eurobot/blob/master/asservissement/Cubot-atelier_asservissement.pdf : this contains most of the odometry calculations and explains them very well,it also teaches how to calibrate odometry.

https://www.pm-robotix.eu/2022/02/02/asservissement-et-pilotage-de-robot-autonome/: look into the odometry section

https://sikula-robotik.desbwa.org/connaissances/asserv/odometrie.php

https://solderspot.net/2014/05/08/navbot-error-correction-using-umbmark/: another method to calibrate odometry(Must read to undestand why odom errors exist)

https://cvra.ch/robot-software/howto/calibrate-odometry/: also another method to calibrate odometry 

+read about the instantaneous center of rotation.

--- 
The code handling odometry is in the Nav_vFeedbackRoutine function in the NavStateMachineTest.c

## Odometry Calibration:
**Odometry calibration always comes after PID tuning**:

To accurately calibrate odometry, your robot must follow precise test paths, but without a well-tuned PID, unequal wheel speeds will cause the robot to curve off course instead of traveling in a straight line. By tuning the PID first, you ensure smooth, **repeatable motion**, making it easy to isolate and fix physical odometry errors.

The calibration paramaters are in NavConstants.h :
- WHEEL_DIAMETER_MM
- LEFT_WHEEL_GAIN
- TRACK_MM

To calibrate each parameter ,follow the process described in chapter 3 in this document: [Cubot - Atelier Asservissement (PDF)](https://github.com/VRAC-team/la-maxi-liste-ressources-eurobot/blob/master/asservissement/Cubot-atelier_asservissement.pdf)

>  **Note:** These parameters if not calibrated correctly can cause an odom error that accumulates to a considerable error at the end of the match so take your time when calibrating.


