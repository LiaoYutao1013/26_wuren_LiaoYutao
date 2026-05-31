# ROS2 Basic Homework Usage

This workspace contains a Python implementation for driving turtlesim in a figure-eight path.

## Files

- `src/ros2_homework_basic_package/ros2_homework_basic_package/figure_eight_turtle.py`: publishes `geometry_msgs/msg/Twist` commands to `/turtle1/cmd_vel`.
- `src/ros2_homework_basic_package/config/figure_eight.yaml`: fixed parameters used by the controller.
- `src/ros2_homework_basic_package/launch/figure_eight.launch.py`: starts `turtlesim_node` and the figure-eight controller with the YAML parameters.

## Build

```bash
cd ros2_homework_basic_ws
colcon build
source install/setup.bash
```

## Run

```bash
ros2 launch ros2_homework_basic_package figure_eight.launch.py
```

The turtle first moves around one full circle, then reverses angular velocity for the next full circle. Repeating these two tangent circles forms a continuous figure-eight path.
