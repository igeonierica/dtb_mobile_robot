import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch import LaunchDescription


def generate_launch_description():

    #use sim time
    use_sim_time = LaunchConfiguration('use_sim_time',default='true')
    
    #view rviz
    rviz_config_dir = os.path.join(
        get_package_share_directory('dtb_mobile_bringup',
        'rviz',
        'dtb_map.rviz')
    )

    spawn_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d',rviz_config_dir],
        output='screen'
    )

    ld = LaunchDescription()

    ld.add_action(spawn_rviz_cmd)

    return ld