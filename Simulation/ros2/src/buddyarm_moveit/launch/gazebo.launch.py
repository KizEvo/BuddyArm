import os

from moveit_configs_utils import MoveItConfigsBuilder 
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction
)
from launch.substitutions import (
    Command,
    PathJoinSubstitution,
    LaunchConfiguration,
)
from launch_ros.substitutions import FindPackageShare

from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
 
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
 
from srdfdom.srdf import SRDF
 
from moveit_configs_utils.launch_utils import (
    add_debuggable_node,
    DeclareBooleanLaunchArg,
)

def generate_launch_description():
    """
    Launches a MoveIt2 and Gazebo simulation

    The MoveIt2 code section is from the `generate_demo_launch()` of `moveit_configs_utils.launches` library
    """
    # ============================ Global CONFIG ============================

    ld = LaunchDescription()

    # ============================ MoveIt2 CONFIG ============================

    moveit_config = MoveItConfigsBuilder("BuddyArm", package_name="buddyarm_moveit").to_moveit_configs()

    launch_package_path = moveit_config.package_path

    ld.add_action(DeclareBooleanLaunchArg("use_rviz", default_value=True))

    # ============================ MoveIt2 LAUNCH ============================

    # If there are virtual joints, broadcast static tf by including virtual_joints launch
    virtual_joints_launch = (
        launch_package_path / "launch/static_virtual_joint_tfs.launch.py"
    )
 
    if virtual_joints_launch.exists():
        ld.add_action(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(virtual_joints_launch)),
            )
        )
 
    # Given the published joint states, publish tf for the robot links
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/rsp.launch.py")
            ),
        )
    )

    # Launch MoveIt2 move_group
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/move_group.launch.py")
            ),
        )
    )
 
    # Run Rviz and load the default config to see the state of the move_group node
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/moveit_rviz.launch.py")
            ),
            condition=IfCondition(LaunchConfiguration("use_rviz")),
        )
    )
 
    # Spawn controllers
    # 1. joint_state_broadcaster
    # 2. buddyarm_controller
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/spawn_controllers.launch.py")
            ),
        )
    )

    # ============================ Gazebo section ============================
    
    # Launch Gazebo, start an empty world
    gazebo_launch_file = PathJoinSubstitution([
        FindPackageShare('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py'
    ])
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch_file),
            launch_arguments={
                'gz_args': '-r empty.sdf'
            }.items()
        )
    )

    # Start Gazebo ROS2 bridge, Gazebo use ROS2 clock, this suppress warning in the logs
    ld.add_action(
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
            output="screen",
        )
    )


    # Spawn robot into Gazebo 5 seconds later, allow Gazebo simulation to startup properly, change the time as needed.
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'buddyarm',
            '-allow_renaming', 'true'
        ],
        output="screen"
    )
    delayed_robot_spawn = TimerAction(
        period=5.0,
        actions=[spawn_robot]
    )
    ld.add_action(delayed_robot_spawn)

    return ld
