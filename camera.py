import cv2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from camera.pose_detection import PoseDetector
except ModuleNotFoundError:
    from pose_detection import PoseDetector
    
class Camera:
    def __init__(self, camera_id=0, width=640, height=480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None

    def start(self):
        """Mở webcam với độ phân giải chuẩn nhẹ 640x480."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            return True
        return False

    def get_frame(self):
        """Đọc 1 frame từ camera."""
        if self.cap and self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                return frame
        return None

    def release(self):
        """Giải phóng camera khi hoàn thành."""
        if self.cap and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    cam = Camera(camera_id=0, width=640, height=480)
    detector = PoseDetector(complexity=0)

    if not cam.start():
        print("Lỗi: Không kết nối được webcam!")
    else:
        print("Đang mở webcam... Nhấn phím 'q' để dừng.")
        while True:
            frame = cam.get_frame()
            if frame is None:
                print("Lỗi: Không đọc được hình ảnh từ webcam.")
                break

            # Lật ngược khung hình như soi gương
            frame = cv2.flip(frame, 1)

            # 1 & 2 & 3. Mở camera, nhận diện người và vẽ bộ xương
            frame = detector.find_pose(frame, draw=True)

            # 4. Trả về tọa độ các điểm
            landmarks = detector.get_position(frame)

            # 5. Xử lý trường hợp không nhìn thấy người
            if not landmarks:
                cv2.putText(frame, "KHONG TIM THAY NGUOI!", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f"Da nhan dien 33 diem (Diem: {len(landmarks)})", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("Demo Camera & Pose Detection - Tran Bao Han", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cam.release()
        detector.close()
        cv2.destroyAllWindows()
