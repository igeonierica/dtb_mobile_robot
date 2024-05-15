import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from math import cos, sin, pi
from std_msgs.msg import Int32
from threading import Event

import numpy as np
import cv2
from geometry_msgs.msg import Twist

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

class SimpleMover(Node):
    def __init__(self):
        super().__init__('simple_mover')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

    def move_forward(self, speedx, speedz):
        twist = Twist()
        twist.linear.x = float(speedx) # 전진 속도를 float로 명시적으로 설정
        twist.angular.z = float(speedz)  # 회전 없음

        # 속도를 로봇에게 보내 로봇 이동 시작
        self.publisher_.publish(twist)
        self.get_logger().info('Moving forward')

class NavigationClient(Node):

    def __init__(self, goal_callback):
        super().__init__('navigation_client')
        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.goal_callback = goal_callback  # 콜백 함수 저장

    def send_goal(self, x, y, theta):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = sin(theta / 2)
        goal_msg.pose.pose.orientation.w = cos(theta / 2)

        self.action_client.wait_for_server()
        self._send_goal_future = self.action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result()
        if hasattr(result, 'result') and result.result:
            self.get_logger().info('Goal reached successfully!')
            if current_goal_index[0] == 1:  # 첫 번째 목표 도달 후
                print("Starting line tracer...")
                line_tracer()  # line_tracer 실행
            elif current_goal_index[0] < len(goals):
                self.goal_callback()  # 다음 목표로 이동
        else:
            self.get_logger().info('Failed to reach goal or goal canceled.')


class OneTimeSubscriber(Node):
    def __init__(self):
        super().__init__('qt_subscriber')
        self.subscription = self.create_subscription(
            Int32,
            'go_state',
            self.listener_callback, 10)
        self.event = Event()  # Event 객체 생성

    def listener_callback(self, msg):
        print("Received message:" , msg.data)
        self.event.set()  # 메시지 수신 시 이벤트 트리거

def start_state(args=None):
    #rclpy.init(args=args)  # rclpy.init() 호출
    subscriber = OneTimeSubscriber()
    # rclpy.spin_once()를 사용하여 최소 한 번의 콜백 호출을 기다림
    while not subscriber.event.is_set():
        rclpy.spin_once(subscriber)

    subscriber.destroy_node()
    rclpy.shutdown()
    # 메시지가 수신되고 이벤트가 설정된 후 추가 작업 실행
    print("Additional code execution in main after message reception.")

def line_tracer():
    while(True):

        # Capture the frames

        ret, frame = cap.read()
        # Crop the image
        frame = frame[200:480, 0:640]


        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Gaussian blur
        blur = cv2.GaussianBlur(gray,(5,5),0)
        # Color thresholding
        ret,thresh1 = cv2.threshold(blur,50,255,cv2.THRESH_BINARY_INV)
        # Erode and dilate to remove accidental line detections
        mask = cv2.erode(thresh1, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # Find the contours of the frame
        contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
        # Find the biggest contour (if detected)
        # ROS 시스템이 이미 초기화되었는지 확인
        if not rclpy.ok():
            # 초기화가 되지 않았다면, rclpy를 초기화합니다.
            rclpy.init()
            
        simple_mover = SimpleMover()

        if len(contours) > 0:

            c = max(contours, key=cv2.contourArea)
            # x 좌표의 최소값과 최대값 찾기
            min_x = min(point[0][0] for point in c)
            max_x = max(point[0][0] for point in c)
            # x 길이 계산
            x_length = max_x - min_x
            print(f"Contour's x length: {x_length}")
            if x_length > 255:
                break

            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            cv2.line(frame,(cx,0),(cx,720),(255,0,0),1)
            cv2.line(frame,(0,cy),(1280,cy),(255,0,0),1)
            cv2.drawContours(frame, contours, -1, (0,255,0), 1)
            #print(cx)

            #왼쪽으로 가야 됨 
            if cx >= 315:
                print("right")
                simple_mover.move_forward(0.15, -0.15)

            #on track  
            if cx < 315 and cx > 295:
                print("foward")
                simple_mover.move_forward(0.2, 0.0)  # 0.2 m/s 속도로 2.5초 동안 이동

            #오른쪽으로 가야 됨 
            if cx <= 295:
                print("left")
                simple_mover.move_forward(0.15, 0.15)

        simple_mover.destroy_node()
        #rclpy.shutdown()
        #Display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    go_to_next_goal()  # 다음 목표로 이동
    print("finish")

if __name__ == '__main__':
    rclpy.init()
    start_state()

    goals = [(78.123, -17.83, -2.0)]  # 예시 목표 위치들
    current_goal_index = [0]  # 현재 목표 인덱스
    print(current_goal_index)


    def go_to_next_goal():
        if current_goal_index[0] < len(goals):
            x, y, theta = goals[current_goal_index[0]]
            navigation_client.send_goal(x, y, theta)
            current_goal_index[0] += 1

    # ROS 시스템이 이미 초기화되었는지 확인
    if not rclpy.ok():
        # 초기화가 되지 않았다면, rclpy를 초기화합니다.
        rclpy.init()
        
    navigation_client = NavigationClient(go_to_next_goal)
    go_to_next_goal()  # 첫 목표로 시작
    

    rclpy.spin(navigation_client)
    rclpy.shutdown()
    print("all finish")