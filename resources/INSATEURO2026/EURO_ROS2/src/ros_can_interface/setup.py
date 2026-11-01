from setuptools import find_packages, setup

package_name = 'ros_can_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='malek',
    maintainer_email='melekkhadhraoui3@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'can_init = ros_can_interface.can_init:main',
            'can_receiveMessage = ros_can_interface.can_receiveMessage:main',
            'can_sendMessage= ros_can_interface.can_sendMessage:main',
            'can_sendResetSignal= ros_can_interface.can_sendResetSignal:main',
            'can_sendStopSignal= ros_can_interface.can_sendStopSignal:main',
            'master_sender_interactive= ros_can_interface.master_sender_interactive:main',
            'can_sendAck = ros_can_interface.can_sendAcknowledgeSignal:main',
        ],
    },
)
