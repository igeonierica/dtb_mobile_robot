import os
import launch
import launch_ros

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.substitutions import ThisLaunchFileDir


def generate_launch_description():
    
    rviz_config_file = os.path.join(get_package_share_directory('dtb_mobile_bringup'), 'rviz','tracer_bringup_rivz.rviz')

    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false',
                                             description='Use simulation clock if true')

    port_name_arg = DeclareLaunchArgument('port_name', default_value='can0',
                                         description='CAN bus name, e.g. can0')
    odom_frame_arg = DeclareLaunchArgument('odom_frame', default_value='odom',
                                           description='Odometry frame id')
    base_link_frame_arg = DeclareLaunchArgument('base_frame', default_value='base_footprint',
                                                description='Base link frame id')
    odom_topic_arg = DeclareLaunchArgument('odom_topic_name', default_value='odom',
                                           description='Odometry topic name')
    is_tracer_mini_arg = DeclareLaunchArgument('is_tracer_mini', default_value='false',
                                          description='Scout mini model')
    simulated_robot_arg = DeclareLaunchArgument('simulated_robot', default_value='false',
                                                   description='Whether running with simulator')
    sim_control_rate_arg = DeclareLaunchArgument('control_rate', default_value='50',
                                                 description='Simulation control loop update rate')
    
    
    tracer_base_node = launch_ros.actions.Node(
        package='tracer_base',
        executable='tracer_base_node',
        output='screen',
        emulate_tty=True,
        parameters=[{
                'use_sim_time': launch.substitutions.LaunchConfiguration('use_sim_time'),
                'port_name': launch.substitutions.LaunchConfiguration('port_name'),                
                'odom_frame': launch.substitutions.LaunchConfiguration('odom_frame'),
                'base_frame': launch.substitutions.LaunchConfiguration('base_frame'),
                'odom_topic_name': launch.substitutions.LaunchConfiguration('odom_topic_name'),
                'is_tracer_mini': launch.substitutions.LaunchConfiguration('is_tracer_mini'),
                'simulated_robot': launch.substitutions.LaunchConfiguration('simulated_robot'),
                'control_rate': launch.substitutions.LaunchConfiguration('control_rate'),
        }])
    

    #sllidar a1 launch execute 라이다 기능 활성화 
    sllidar_a1_prefix = get_package_share_directory('sllidar_ros2')
    sllidar_a1_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(sllidar_a1_prefix,'launch','sllidar_a1_launch.py'))
    )
    
    tracer_lidar_node = Node(package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_pub_laser',
        arguments=['0.215', '0', '0.275','0', '3.14159', '3.14159','base_link','base_scan'],
    )



    robot_model_pkg_dir = LaunchConfiguration(
        'robot_model_pkg_dir',
        default=os.path.join(get_package_share_directory('my_diff_mobile'), 'launch')
    )
    
    jonit_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([robot_model_pkg_dir, '/tracer_mini_description.launch.py'])
    )
    rviz2_node = Node(package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', rviz_config_file],
                    )
    
    return LaunchDescription([
        use_sim_time_arg,
        port_name_arg,        
        odom_frame_arg,
        base_link_frame_arg,
        odom_topic_arg,
        is_tracer_mini_arg,
        simulated_robot_arg,
        sim_control_rate_arg,
        tracer_base_node,
        tracer_lidar_node,
        sllidar_a1_cmd,
        jonit_node,
        # rviz2_node
    ])
