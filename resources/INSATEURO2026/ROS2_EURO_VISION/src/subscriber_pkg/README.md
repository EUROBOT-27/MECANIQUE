subscriber_pkg
===============

This is a small ament_python package that subscribes to the `nav_targets` topic
(geometry_msgs/PointStamped) and logs incoming navigation targets.

How to copy to Raspberry Pi
--------------------------
1. Copy the folder `src/subscriber_pkg` to the Raspberry Pi's workspace `src/`.
   Example (from Vision PC):

   scp -r src/subscriber_pkg pi@<raspberry_ip>:/home/pi/ros2_ws/src/

2. On the Raspberry Pi, build and source the workspace:

   cd /home/pi/ros2_ws
   colcon build --packages-select subscriber_pkg
   . install/setup.bash

3. Ensure environment variables match the Vision PC for DDS discovery (on both machines):

   export ROS_DOMAIN_ID=42
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

4. Run the subscriber on the Raspberry Pi:

   ros2 run subscriber_pkg nav_subscriber

If you prefer, run the `ros2 topic echo /nav_targets` CLI command instead to observe messages.
