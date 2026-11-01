from setuptools import setup, find_packages

package_name = 'camera_node'

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
    maintainer='tasnim',
    maintainer_email='tasnim.daly.9@gmail.com',
    description='Camera publisher node for Eurobot',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'camera_node = camera_node.camera_publisher:main',
        ],
    },
)