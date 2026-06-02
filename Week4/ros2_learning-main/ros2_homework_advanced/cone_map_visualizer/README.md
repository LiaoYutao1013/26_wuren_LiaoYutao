# Cone Map Visualizer

This package subscribes to `/estimation/slam/map` (`fsd_common_msgs/msg/Map`) and publishes RViz `MarkerArray` data for cone visualization.

## Build

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
colcon build --packages-select fsd_common_msgs cone_map_visualizer
source install/setup.bash
```

## Run

Launch the visualizer, RViz, and the provided bag file:

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py
```

The RViz fixed frame is `world`, matching `Map.header.frame_id` in the provided bag.

## Topics

Input:

```text
/estimation/slam/map
```

Output:

```text
/visualization/cone_markers
```

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `input_topic` | `/estimation/slam/map` | Map topic to subscribe |
| `marker_topic` | `/visualization/cone_markers` | MarkerArray topic for RViz |
| `frame_override` | empty | Override marker frame; empty means use `msg.header.frame_id` |
| `marker_scale` | `0.45` | Cone marker sphere size |
| `z_offset` | `0.18` | Raise markers above the ground plane |
| `bag_path` | installed `map_to_visualize` | Bag path used by launch |
| `play_bag` | `true` | Whether launch should play the bag |
| `use_rviz` | `true` | Whether launch should start RViz |

Example without RViz:

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py use_rviz:=false
```

Example using an external bag:

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py bag_path:=/path/to/map_to_visualize
```
