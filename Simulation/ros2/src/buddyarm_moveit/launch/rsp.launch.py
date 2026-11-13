from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_rsp_launch
from launch_ros.actions import SetParameter
import yaml
import os

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("BuddyArm", package_name="buddyarm_moveit").to_moveit_configs()
    # Launch RViz
    launch_description = generate_rsp_launch(moveit_config)
    launch_package_path = moveit_config.package_path
    config_path = os.path.join(launch_package_path, "config", "user_cfg.yaml")
    # Apply simulation time to nodes in this launch scope, without this MoveIt can't execute properly
    with open(config_path, "r") as file:
        config = yaml.safe_load(file) or {}
    use_gazebo = config.get("user_cfg", {}).get("use_gazebo", False)
    if use_gazebo:
        launch_description.add_action(SetParameter(name="use_sim_time", value=True))
    return launch_description
