#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource



def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')
    
    resolution = LaunchConfiguration('resolution', default='0.01')
    resolution_arg = DeclareLaunchArgument(
        'publish_period_sec',
        default_value=resolution,
        description='Resolution of a grid cell in the published occupancy grid'
    )

    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')
    publish_period_sec_arg = DeclareLaunchArgument(
        'publish_peroid_sec',
        default_value=publish_period_sec,
        description='OccupancyGrid publishing period'
    )

    my_package_prefix = get_package_share_directory('dtb_mobile_cartographer')
    
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir',
                                                  default=os.path.join(my_package_prefix, 'config'))
    cartographer_config_dir_arg = DeclareLaunchArgument(
        'cartographer_config_dir',
        default_value=cartographer_config_dir,
        description='Full path to config file to load'
    )

    configuration_basename=LaunchConfiguration('configuration_basename',
                                               default='dtb_mobile_lds_2d.lua')
    configuration_basename_arg=DeclareLaunchArgument(
        'configuration_basename',
        default_value=configuration_basename,
        description='Name of lua file for cartographer'
    )


    pkg_laser_filters_dir = get_package_share_directory('laser_filters')
    laser_filters_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_laser_filters_dir, 'examples', 'median_filter_example.launch.py')
        )
    )


    # tf2_node = Node(
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     name='link1_broadcaster',
    #     parameters=[{'use_sim_time':use_sim_time}],
    #     arguments=['0', '0', '0', '0', '0', '0', '1', 'map', 'odom'],
    #     output='screen'
    # )

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        parameters=[{'use_sim_time':use_sim_time}],
        arguments=['-configuration_directory', cartographer_config_dir,
                   '-configuration_basename', configuration_basename],
        remappings=[
            ('/scan', '/scan_filtered')
        ],
        output='screen'
    )
    
    occupancy_gird_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='occupancy_grid_node',
        parameters=[{'use_sim_time':use_sim_time}],
        arguments=['-resolution', resolution,
                   '-publish_period_sec', publish_period_sec]
    )



    cl = LaunchDescription()

    cl.add_action(use_sim_time_arg)
    cl.add_action(resolution_arg)
    cl.add_action(publish_period_sec_arg)
    cl.add_action(cartographer_config_dir_arg)
    cl.add_action(configuration_basename_arg)

    # cl.add_action(tf2_node)
    cl.add_action(laser_filters_cmd)
    cl.add_action(cartographer_node)
    cl.add_action(occupancy_gird_node)

    return cl