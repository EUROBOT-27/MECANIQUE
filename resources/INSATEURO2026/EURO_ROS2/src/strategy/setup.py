from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'strategy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))) 
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
            'strat_deuxieme_static_task_generator=strategy.strat_deuxieme_static_task_generator:main',
            'strat_premiere_static_task_generator=strategy.strat_premiere_static_task_generator:main',
            'voltron_strat_deuxieme_static_task_generator=strategy.voltron_strat_deuxieme_static_task_generator:main',
            'voltron_strat_premiere_static_task_generator=strategy.voltron_strat_premiere_static_task_generator:main',            
            'strategy_server=strategy.strategy_server:main',
            'client=strategy.client:main',
            'static_sub_task_generator=strategy.static_sub_task_generator:main',
            
        ],
    },
)
