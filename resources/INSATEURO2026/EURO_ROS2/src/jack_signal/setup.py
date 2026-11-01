from setuptools import find_packages, setup

package_name = 'jack_signal'

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
    maintainer='adem',
    maintainer_email='dalyademoff@gmail.com',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'jack_signal_publisher=jack_signal.jack_signal_publisher:main',
            'game_launcher=jack_signal.game_launcher:main'
        ],
    },
)
