import os
import ctypes
import urllib.request
import cv2

# Vá lỗi thiếu hàm 'free' của thư viện MediaPipe trên Windows (Python 3.13 - 3.15)
if os.name == "nt":
    _orig_getattr = ctypes.CDLL.__getattr__

    def _patched_getattr(self, name):
        try:
            return _orig_getattr(self, name)
        except AttributeError:
            if name == "free":
                for crt in ("ucrtbase", "msvcrt"):
                    try:
                        return getattr(ctypes.cdll, crt).free
                    except Exception:
                        pass
            raise

    ctypes.CDLL.__getattr__ = _patched_getattr

import mediapipe as mp

# Danh sách 35 đường nối khung xương chuẩn 33 điểm của MediaPipe
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
    (11, 12), (11, 23), (12, 24), (23, 24),
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
    (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
]

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "pose_landmarker_lite.task")


class PoseDetector:
    def __init__(self, mode=False, complexity=0, smooth=True,
                 detection_con=0.5, tracking_con=0.5):
        self.landmarks = []
        self.use_legacy = hasattr(mp, "solutions")

        if self.use_legacy:
            # Chạy trên máy dùng MediaPipe bản cũ (< 0.10.30)
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=mode,
                model_complexity=complexity,
                smooth_landmarks=smooth,
                min_detection_confidence=detection_con,
                min_tracking_confidence=tracking_con
            )
        else:
            # Chạy trên máy dùng MediaPipe bản mới (0.10.30+ và 1.x)
            if not os.path.exists(MODEL_PATH) or os.path.getsize(MODEL_PATH) < 1000000:
                print("Đang tải file nhận diện siêu nhẹ (~5MB)...")
                urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

            base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
            options = mp.tasks.vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=detection_con,
                min_pose_presence_confidence=detection_con,
                min_tracking_confidence=tracking_con
            )
            self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

    def find_pose(self, img, draw=True):
        """Phát hiện tư thế 33 điểm và vẽ bộ xương lên khung hình."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.landmarks = []

        if self.use_legacy:
            results = self.pose.process(img_rgb)
            if results.pose_landmarks:
                self.landmarks = results.pose_landmarks.landmark
        else:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            results = self.landmarker.detect(mp_image)
            if results.pose_landmarks and len(results.pose_landmarks) > 0:
                self.landmarks = results.pose_landmarks[0]

        if self.landmarks and draw:
            h, w, _ = img.shape
            points = {}
            for idx, lm in enumerate(self.landmarks):
                if getattr(lm, "visibility", 1.0) > 0.5:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    points[idx] = (cx, cy)
                    cv2.circle(img, (cx, cy), 4, (0, 255, 0), cv2.FILLED)

            for start_idx, end_idx in POSE_CONNECTIONS:
                if start_idx in points and end_idx in points:
                    cv2.line(img, points[start_idx], points[end_idx], (255, 0, 0), 2)

        return img

    def get_position(self, img, draw=False, min_visibility=0.5):
        """
        Trả về tọa độ 33 điểm cơ thể chuẩn hóa để bàn giao cho Thành viên 3.
        Trả về danh sách rỗng [] nếu không nhìn thấy người hoặc độ tin cậy thấp.
        """
        if not self.landmarks:
            return []

        # Kiểm tra độ tin cậy trung bình của các khớp chính (vai, hông, gối)
        key_indices = [11, 12, 23, 24, 25, 26]
        avg_vis = sum(getattr(self.landmarks[i], "visibility", 1.0) for i in key_indices) / len(key_indices)
        if avg_vis < min_visibility:
            return []

        lm_list = []
        h, w, _ = img.shape
        for idx, lm in enumerate(self.landmarks):
            visibility = getattr(lm, "visibility", 1.0)
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append({
                "id": idx,
                "x": cx,
                "y": cy,
                "z": lm.z,
                "norm_x": lm.x,
                "norm_y": lm.y,
                "visibility": visibility
            })
            if draw and visibility > min_visibility:
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        return lm_list

    def close(self):
        """Giải phóng tài nguyên AI để tiết kiệm RAM và pin."""
        if self.use_legacy:
            self.pose.close()
        else:
            self.landmarker.close()
            