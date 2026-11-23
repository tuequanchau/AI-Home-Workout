"""Camera: mở webcam và cung cấp khung hình MỚI NHẤT. File này chỉ lo việc camera.

Việc của các file khác (không làm ở đây):
  - nhận diện 33 điểm, vẽ khung xương, lọc visibility -> camera/pose_detection.py
  - tính góc, đếm rep, nhận xét tư thế                 -> analysis/
  - buổi tập, trạng thái, luồng video cho web           -> core/workout_manager.py

Tối ưu giữ lại:
  - đọc camera ở luồng riêng, luôn giữ khung mới nhất (nhanh hơn, ít trễ)
  - BUFFERSIZE = 1 để giảm độ trễ
  - các tuỳ chọn camera đổi bằng biến môi trường, không cần sửa code:
        CAMERA_BACKEND = default | dshow | msmf   (mặc định "default" - an toàn nhất)
        CAMERA_MJPG    = 1  nén MJPG, có thể tăng FPS nhưng vài webcam bị ảnh đen
        CAMERA_FPS     = 30 ép FPS (0 = không ép; một số driver bị tụt còn ~1 FPS)

Chạy thử:  python camera/camera.py    (nhấn 'q' để thoát)
"""
import os
import sys
import time
import threading

import cv2


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


CAMERA_BACKEND = os.environ.get("CAMERA_BACKEND", "default").strip().lower()
USE_MJPG = os.environ.get("CAMERA_MJPG", "0") == "1"
TARGET_FPS = _env_int("CAMERA_FPS", 0)

_BACKENDS = {
    "dshow": getattr(cv2, "CAP_DSHOW", None),
    "msmf": getattr(cv2, "CAP_MSMF", None),
}


class Camera:
    def __init__(self, camera_id=0, width=640, height=480, threaded=True):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.threaded = threaded
        self.cap = None

        self._frame = None
        self._idx = 0              # số thứ tự khung mới nhất
        self._served_idx = 0       # khung đã giao cho get_new_frame()
        self._last_read = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    # ------------------------------ mở / đóng ------------------------------
    def start(self):
        """Mở webcam. Trả về True nếu thành công."""
        backend = _BACKENDS.get(CAMERA_BACKEND)
        if backend is None:                      # "default": để OpenCV tự chọn
            self.cap = cv2.VideoCapture(self.camera_id)
        else:
            self.cap = cv2.VideoCapture(self.camera_id, backend)

        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            return False

        if USE_MJPG:
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if TARGET_FPS:
            self.cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # giảm độ trễ (một số backend bỏ qua)

        self._last_read = time.time()
        if self.threaded:
            self._running = True
            self._thread = threading.Thread(target=self._reader, name="camera-reader", daemon=True)
            self._thread.start()
        return True

    def _reader(self):
        """Luồng riêng: liên tục đọc và giữ khung mới nhất."""
        while self._running and self.cap is not None:
            try:
                ok, frame = self.cap.read()
            except Exception:
                ok, frame = False, None
            if ok and frame is not None:
                with self._lock:       # read() cấp mảng mới mỗi lần nên không cần copy
                    self._frame = frame
                    self._idx += 1
                    self._last_read = time.time()
            else:
                time.sleep(0.01)

    def release(self):
        """Giải phóng camera. Gọi khi chưa mở cũng không lỗi."""
        self._running = False
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    # ------------------------------ đọc khung hình ------------------------------
    def _reader_alive(self):
        return self._thread is not None and self._thread.is_alive()

    def get_frame(self):
        """Khung hình mới nhất (có thể trùng khung lần trước). None nếu chưa có / mất tín hiệu."""
        if self._reader_alive():
            with self._lock:
                return self._frame
        if self.cap and self.cap.isOpened():        # chế độ không luồng
            success, frame = self.cap.read()
            return frame if success else None
        return None

    def get_new_frame(self):
        """Chỉ trả về khung CHƯA giao lần nào; None nếu chưa có khung mới (để vòng lặp khỏi xử lý lại khung cũ)."""
        if not self._reader_alive():
            return self.get_frame()
        with self._lock:
            if self._frame is None or self._idx == self._served_idx:
                return None
            self._served_idx = self._idx
            return self._frame

    def seconds_since_frame(self):
        """Số giây kể từ lần đọc được khung gần nhất (dùng để phát hiện camera đứng/mất tín hiệu)."""
        return time.time() - self._last_read

    @staticmethod
    def is_black(frame, threshold=8):
        """True nếu ảnh gần như đen (sai camera, bị che, thiếu sáng, backend lỗi)."""
        return frame is not None and cv2.mean(frame)[0] < threshold


# ======================== Chạy thử: camera + khung xương + FPS ========================
def main():
    try:
        from .pose_detection import PoseDetector     # khi dùng như package
    except ImportError:
        from pose_detection import PoseDetector      # khi chạy trực tiếp file này

    cam = Camera(camera_id=_env_int("CAMERA_ID", 0))
    if not cam.start():
        print("Lỗi: Không kết nối được webcam! Thử đổi CAMERA_ID (0, 1, 2) "
              "hoặc đóng ứng dụng đang dùng camera (Zoom, Meet, trình duyệt).")
        return 1

    detector = None
    fps, t_prev = 0.0, time.perf_counter()
    print("Đang mở webcam... Nhấn 'q' để dừng.")
    try:
        detector = PoseDetector(complexity=0)
        while True:
            frame = cam.get_new_frame()
            if frame is None:                        # chưa có khung mới
                if cam.seconds_since_frame() > 3:
                    print("Lỗi: Không đọc được hình ảnh từ webcam.")
                    break
                if cv2.waitKey(2) & 0xFF == ord("q"):
                    break
                continue

            black = Camera.is_black(frame)           # đo trước khi vẽ lên khung
            t0 = time.perf_counter()
            detector.find_pose(frame, draw=True)
            landmarks = detector.get_position(frame)
            pose_ms = (time.perf_counter() - t0) * 1000

            now = time.perf_counter()
            inst = 1.0 / max(now - t_prev, 1e-6)
            fps = inst if fps == 0 else 0.9 * fps + 0.1 * inst
            t_prev = now

            frame = cv2.flip(frame, 1)               # lật gương chỉ để hiển thị
            if landmarks:
                msg, color = f"Nhan dien OK ({len(landmarks)} diem)", (0, 255, 0)
            else:
                msg, color = "KHONG TIM THAY NGUOI!", (0, 0, 255)
            cv2.putText(frame, msg, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"FPS: {fps:.1f}  Pose: {pose_ms:.0f}ms", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            if black:
                cv2.putText(frame, "ANH DEN: kiem tra CAMERA_ID / che camera / CAMERA_BACKEND",
                            (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

            cv2.imshow("Demo Camera & Pose Detection - Tran Bao Han", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cam.release()
        if detector is not None:
            detector.close()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
