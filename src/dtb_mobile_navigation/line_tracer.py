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
            #if x_length > 255:
                #break

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
        rclpy.shutdown()
        #Display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print("finish")

if __name__ == '__main__':
    line_tracer()
