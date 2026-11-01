from setuptools import find_packages, setup

package_name = 'eurobot2025_statemachine'

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
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'Eurobot2025_SMACH_V1=eurobot2025_statemachine.Eurobot2025_SMACH_V1:main',
            'Eurobot2025_SMACH_V2=eurobot2025_statemachine.Eurobot2025_SMACH_V2:main',
            'subscriber_test=eurobot2025_statemachine.subscriber_test:main'
        ],
    },
)
