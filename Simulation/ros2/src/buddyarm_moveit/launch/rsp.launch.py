from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_rsp_launch
from launch_ros.actions import SetParameter

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("BuddyArm", package_name="buddyarm_moveit").to_moveit_configs()
    # Launch RViz
    launch_description = generate_rsp_launch(moveit_config)
    # Apply simulation time to nodes in this launch scope, without this MoveIt can't execute properly
    launch_description.add_action(
        SetParameter(name="use_sim_time", value=True)
    )
    return launch_description
