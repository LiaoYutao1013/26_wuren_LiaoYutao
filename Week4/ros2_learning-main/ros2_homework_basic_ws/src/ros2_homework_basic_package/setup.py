import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'ros2_homework_basic_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='LiaoYutao',
    maintainer_email='bcliaoyutao@mail.scut.edu.cn',
    description='Python turtlesim controller that drives the turtle along a figure-eight path.',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'figure_eight_turtle = ros2_homework_basic_package.figure_eight_turtle:main',
        ],
    },
)
