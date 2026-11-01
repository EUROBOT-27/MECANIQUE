# Eurobot 2025 – ROS Module

This repository contains the **ROS 2 integration layer** for Eurobot 2025. It provides the middleware to connect different modules of the robot (Vision, Navigation, Sensors, and Actuators).

## Responsibilities

* Launch ROS nodes for each subsystem
* Define topics, services, and actions
* Handle inter-module communication
* Integrate sensor data (IMU, gyroscope, encoders, camera)
* Provide simulation interfaces (Webots/Gazebo)

## Repository Structure

```
ros/
├── README.md              # Project documentation
├── launch/                # ROS 2 launch files for starting nodes
├── src/                   # ROS packages (nodes, msg, srv, action)
├── scripts/               # Utility scripts for robot operations
├── config/                # YAML configuration files
├── params/                # Parameter sets for PID, sensors, etc.
└── docs/                  # Documentation, diagrams, setup guides
```
