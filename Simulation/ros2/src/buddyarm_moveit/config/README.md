# User Guide

BuddyArm.urdf.xacro is the main xacro entry file, it includes other xacro file such as `BuddyArm.ros2_control.xacro`. Loads .yaml parameter file such as `initial_positions.yaml` and `user_cfg.yaml`

## Simulation

To use Gazebo simulation (or not), take a look at `user_cfg.yaml` file

- Gazebo launch script is `buddyarm_moveit/launch/gazebo.launch.py`.
- Default launch script is `buddyarm_moveit/launch/demo.launch.py`.

Use Gazebo launch script when `user_cfg.yaml` file is set to use Gazebo simulation, else use the default launch script.
