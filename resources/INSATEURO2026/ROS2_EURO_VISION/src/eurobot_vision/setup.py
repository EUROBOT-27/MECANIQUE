from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'eurobot_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=[
        'eurobot_vision',
        'eurobot_vision.kalman_filter',
        'eurobot_vision.occlusion_handler'
    ],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.json')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Eurobot vision system',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_node = eurobot_vision.vision_ros_node:main',
            'vision_node_cam = eurobot_vision.vision_ros_node_cam:main',
        ],
    },
)