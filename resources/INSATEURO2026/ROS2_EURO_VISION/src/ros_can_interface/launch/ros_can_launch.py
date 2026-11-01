import launch
import launch_ros.actions
from launch.actions import TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    can_init_node = Node(
        package='ros_can_interface',
        executable='can_init',
        name='can_init'
    )

    other_nodes = [
        Node(
            package='ros_can_interface',
            executable='can_receiveMessage',
            name='can_receiveMessage'
        ),
        Node(
            package='ros_can_interface',
            executable='can_sendMessage',
            name='can_sendMessage'
        ),
        Node(
            package='ros_can_interface',
            executable='can_sendResetSignal',
            name='can_sendResetSignal'
        ),
        Node(
            package='ros_can_interface',
            executable='can_sendStopSignal',
            name='can_sendStopSignal'
        ),
        Node(
            package='ros_can_interface',
            executable='can_sendAck',
            name='can_sendAck'
        ),
    ]

    return launch.LaunchDescription([
        # Start the can_init node immediately
        can_init_node,

        # Start the other nodes after a delay of 1 second
        TimerAction(
            period=1.0,  # Delay in seconds
            actions=other_nodes
        ),
    ])

