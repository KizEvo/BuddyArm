from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch
import yaml
import os

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("BuddyArm", package_name="buddyarm_moveit").to_moveit_configs()
    launch_package_path = moveit_config.package_path
    # If we don't use the correct xacro, exit now
    config_path = os.path.join(launch_package_path, "config", "user_cfg.yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file) or {}
    use_gazebo = config.get("user_cfg", {}).get("use_gazebo", False)
    if use_gazebo:
        raise RuntimeError("Incorrect user config, see config/README.md")
    return generate_demo_launch(moveit_config)
