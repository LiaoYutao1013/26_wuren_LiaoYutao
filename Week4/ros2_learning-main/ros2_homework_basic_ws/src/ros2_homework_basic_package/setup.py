import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ros2_homework_basic_package'

setup(
    name=package_name,
    version='0.0.0',
    # 自动查找Python包目录，排除测试目录；
    packages=find_packages(exclude=['test']),
    data_files=[
        # 注册ament resource，使ros2 pkg能查找到该包；
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        # 安装package.xml，供ROS2工具读取包元信息和依赖；
        ('share/' + package_name, ['package.xml']),
        # 安装参数文件；
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        # 安装launch文件；
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
            # ros2启动入口；
            'figure_eight_turtle = ros2_homework_basic_package.figure_eight_turtle:main',
            # q键事件退出节点入口，发布quit_signal供控制节点订阅。
            'keyboard_quit_node = ros2_homework_basic_package.keyboard_quit_node:main',
        ],
    },
)
