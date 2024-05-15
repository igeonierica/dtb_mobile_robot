import cv2
import numpy as np

# 카메라 캡처 객체 생성
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 이미지 대비를 증가시키기 위한 처리
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 더욱 좁은 범위의 HSV 설정으로 어두운 검은색 검출
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 55])

    # 마스크 생성
    mask = cv2.inRange(hsv, lower_black, upper_black)
    
    # 윤곽선 검출
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        # 각 컨투어에 대한 경계 상자 계산
        x, y, w, h = cv2.boundingRect(contour)
        # 세로로 긴 라인인지 확인 (가로:세로 비율이 1:4 이상일 경우)
        if h > 4 * w:
            # 윤곽선을 원본 이미지에 그림
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

    cv2.imshow('Original', frame)
    cv2.imshow('Black Line Detection', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
