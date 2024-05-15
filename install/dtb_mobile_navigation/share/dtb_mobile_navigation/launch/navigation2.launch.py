import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_name = "dtb_mobile_navigation"
    pkg_path = os.path.join(get_package_share_directory(package_name))


    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    map_dir = LaunchConfiguration(
        'map',
        default=os.path.join(pkg_path, 'maps', 'map.yaml')
    )

    param_file_name = 'navigation2.yaml'

    param_dir = LaunchConfiguration(
        'params_file',
        default=os.path.join(pkg_path, 'config', param_file_name)
    )

    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    rviz_config = os.path.join(pkg_path, "rviz", "view_rviz.rviz")
    bringup_pkg_path = os.path.join(get_package_share_directory("dtb_mobile_bringup"))


    # nav_include=IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(nav2_launch_file_dir + '/bringup_launch.py'),
    #     launch_arguments={
    #         'map':map_dir,
    #         'use_sim_time':use_sim_time,
    #         'param_file':param_dir
    #     }.items()
    # )

    # laser_node = Node(
    #     package='tf2_ros',
    #     executable="static_transform_publisher",
    #     arguments=['0', '0', '0', '0', '0', '0', 'map','odom']
    # )

    
    # map_dir_cmd = DeclareLaunchArgument(
    #     'map',
    #     default_value=map_dir,
    #     description="Full path to map file to load"
    # )

    # param_dir_cmd = DeclareLaunchArgument(
    #     'params_file',
    #     default_value=param_dir,
    #     description="Full path to param file to load"
    # )

    # use_sim_time_cmd = DeclareLaunchArgument(
    #     'use_sim_time',
    #     default_value='true',
    #     description="Use simulation (Gazebo) clock if true"
    # )


    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(bringup_pkg_path, 'launch'), '/dtb_mobile_description2.launch.py']),
        ),
        DeclareLaunchArgument(
            'map',
            default_value=map_dir,
            description='Full path to map file to load'),

        DeclareLaunchArgument(
            'params_file',
            default_value=param_dir,
            description='Full path to param file to load'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
            launch_arguments={
                'map': map_dir,
                'use_sim_time': use_sim_time,
                'params_file': param_dir}.items(),
        ),
        #start_create_map_cmd,
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'),
    ])

    # ld = LaunchDescription()

    # ld.add_action(map_dir_cmd)
    # ld.add_action(param_dir_cmd)
    # ld.add_action(use_sim_time_cmd)
    
    # ld.add_action(laser_node)
    # ld.add_action(nav_include)
    
    # return ld

    