import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Launch static_sub_task_generator in a new terminal
        ExecuteProcess(
            cmd=['gnome-terminal', '--', 'ros2', 'run', 'strategy', 'static_sub_task_generator'],
            output='screen'
        ),
        # Launch static_task_generator in a new terminal
        ExecuteProcess(
            cmd=['gnome-terminal', '--', 'ros2', 'run', 'strategy', 'static_task_generator'],
            output='screen'
        ),
        # Launch strategy_server in a new terminal
        ExecuteProcess(
            cmd=['gnome-terminal', '--', 'ros2', 'run', 'strategy', 'strategy_server'],
            output='screen'
        ),
    ])
