import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch import LaunchDescription


def generate_launch_description():
    #use_sim_time
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    #sllidar a1 launch execute 라이다 기능 활성화 
    sllidar_a1_prefix = get_package_share_directory('sllidar_ros2')
    sllidar_a1_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(sllidar_a1_prefix,'launch','sllidar_a1_launch.py'))
    )

    #trace mini base 주행 기능 활성화 
    tracer_prefix = get_package_share_directory('tracer_base')
    tracer_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tracer_prefix,'launch','tracer_mini_base.launch.py'))
    )

    #base tf laser 노드 사용 
    base_2_laser_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_2_laser_tf',
        parameters=[{'use_sim_time':use_sim_time}],
        arguments=['0.215','0','0.275','-3.141592','3.141592','3.141592','base_link','laser'],
        output='screen'
    )

    #base_link tf imu_link
    base_2_imu_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_2_imu_tf',
        parameters=[{'use_sim_time':use_sim_time}],
        arguments=['0','0','0','0','0','-3.141592','base_link','imu_link'],
        output='screen'
    )

    #map tf odom
    map_2_odom_cmd = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_2_odom_tf',
        parameters=[{'use_sim_time':use_sim_time}],
        arguments=['0','0','0','0','0','0','map','odom'],
        output='screen'
    )

    base_to_laser_publisher = ExecuteProcess(
        #cmd=["ros2", "run", "tf2_ros", "static_transform_publisher", '0.215', '0', '0.275', '-3.141592', '3.141592', '3.141592', "base_link", "laser"], output="screen"
        cmd=["ros2", "run", "tf2_ros", "static_transform_publisher", '0.215', '0', '0.275', '-3.141592', '3.141592', '3.141592', "base_link", "laser"], output="screen"
    )


    odom_to_base_publisher = ExecuteProcess(
        cmd=["ros2", "run", "tf2_ros", "static_transform_publisher", '0', '0', '0', '0', '0', '0', "base_link", "imu_link"], output="screen"
    )

    #최종적으로 모든 액션들을 포함하는 런치 
    ld = LaunchDescription()
    ld.add_action(sllidar_a1_cmd)
    ld.add_action(tracer_cmd)
    ld.add_action(base_2_laser_node)
    ld.add_action(base_2_imu_node)
    ld.add_action(map_2_odom_cmd)
    ld.add_action(base_to_laser_publisher)
    ld.add_action(odom_to_base_publisher)
    

    return ld