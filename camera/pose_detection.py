
import os
import ctypes
import urllib.request
import time
import cv2
import mediapipe as mp


# =========================================================
# 1. FIX LỖI MEDIA PIPE TRÊN WINDOWS
# =========================================================

# Vá lỗi thiếu hàm free của thư viện MediaPipe
# trên một số phiên bản Python mới của Windows.
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


# =========================================================
# 2. CẤU HÌNH MODEL
# =========================================================

POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),

    (11, 12), (11, 23), (12, 24), (23, 24),

    (11, 13), (13, 15), (15, 17),
    (15, 19), (15, 21), (17, 19),

    (12, 14), (14, 16), (16, 18),
    (16, 20), (16, 22), (18, 20),

    (23, 25), (25, 27), (27, 29),
    (27, 31), (29, 31),

    (24, 26), (26, 28), (28, 30),
    (28, 32), (30, 32)
]


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/"
    "pose_landmarker_lite.task"
)

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "pose_landmarker_lite.task"
)


# =========================================================
# 3. POSE DETECTOR
# =========================================================

class PoseDetector:

    def __init__(
        self,
        mode=False,
        complexity=0,
        smooth=True,
        detection_con=0.5,
        tracking_con=0.5
    ):

        self.landmarks = []

        # Timestamp dành cho MediaPipe VIDEO mode
        self._last_timestamp_ms = 0

        # Phân biệt MediaPipe Legacy và MediaPipe Tasks
        self.use_legacy = hasattr(mp, "solutions")

        # -------------------------------------------------
        # A. MEDIAPIPE LEGACY
        # -------------------------------------------------

        if self.use_legacy:

            self.mp_pose = mp.solutions.pose

            self.pose = self.mp_pose.Pose(
                static_image_mode=mode,
                model_complexity=complexity,
                smooth_landmarks=smooth,
                min_detection_confidence=detection_con,
                min_tracking_confidence=tracking_con
            )

        # -------------------------------------------------
        # B. MEDIAPIPE TASKS (0.10.30+ / 1.x)
        # -------------------------------------------------

        else:

            # Tải model nếu chưa tồn tại
            if (
                not os.path.exists(MODEL_PATH)
                or os.path.getsize(MODEL_PATH) < 1000000
            ):

                print("Đang tải model Pose Landmarker Lite...")

                urllib.request.urlretrieve(
                    MODEL_URL,
                    MODEL_PATH
                )

            base_options = mp.tasks.BaseOptions(
                model_asset_path=MODEL_PATH
            )

            options = mp.tasks.vision.PoseLandmarkerOptions(
                base_options=base_options,

                # VIDEO phù hợp với webcam realtime
                running_mode=(
                    mp.tasks.vision.RunningMode.VIDEO
                ),

                num_poses=1,

                min_pose_detection_confidence=detection_con,
                min_pose_presence_confidence=detection_con,
                min_tracking_confidence=tracking_con
            )

            self.landmarker = (
                mp.tasks.vision.PoseLandmarker
                .create_from_options(options)
            )

    # =====================================================
    # 4. FIND POSE
    # =====================================================

    def find_pose(self, img, draw=True):

        """
        Phát hiện tư thế cơ thể gồm 33 landmarks.

        Input:
            img: ảnh BGR từ OpenCV
            draw: có vẽ skeleton hay không

        Output:
            Ảnh đã được xử lý
        """

        if img is None:
            self.landmarks = []
            return img

        # Chuyển BGR sang RGB
        img_rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        self.landmarks = []

        # -------------------------------------------------
        # A. MEDIAPIPE LEGACY
        # -------------------------------------------------

        if self.use_legacy:

            results = self.pose.process(img_rgb)

            if results.pose_landmarks:
                self.landmarks = (
                    results.pose_landmarks.landmark
                )

        # -------------------------------------------------
        # B. MEDIAPIPE TASKS
        # -------------------------------------------------

        else:

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=img_rgb
            )

            # Timestamp tính bằng milliseconds
            timestamp_ms = time.monotonic_ns() // 1_000_000

            # Đảm bảo timestamp luôn tăng
            timestamp_ms = max(
                timestamp_ms,
                self._last_timestamp_ms + 1
            )

            self._last_timestamp_ms = timestamp_ms

            results = self.landmarker.detect_for_video(
                mp_image,
                timestamp_ms
            )

            if (
                results.pose_landmarks
                and len(results.pose_landmarks) > 0
            ):

                self.landmarks = results.pose_landmarks[0]

        # -------------------------------------------------
        # C. VẼ SKELETON
        # -------------------------------------------------

        if self.landmarks and draw:

            h, w, _ = img.shape

            points = {}

            # Vẽ các landmarks
            for idx, lm in enumerate(self.landmarks):

                visibility = getattr(
                    lm,
                    "visibility",
                    1.0
                )

                if visibility > 0.5:

                    cx = int(lm.x * w)
                    cy = int(lm.y * h)

                    points[idx] = (cx, cy)

                    cv2.circle(
                        img,
                        (cx, cy),
                        4,
                        (0, 255, 0),
                        cv2.FILLED
                    )

            # Vẽ các đường nối
            for start_idx, end_idx in POSE_CONNECTIONS:

                if (
                    start_idx in points
                    and end_idx in points
                ):

                    cv2.line(
                        img,
                        points[start_idx],
                        points[end_idx],
                        (255, 0, 0),
                        2
                    )

        return img

    # =====================================================
    # 5. GET POSITION
    # =====================================================

    def get_position(
        self,
        img,
        draw=False,
        min_visibility=0.5
    ):

        """
        Trả về danh sách 33 landmarks.

        Mỗi landmark gồm:
            id
            x, y: tọa độ pixel
            z: tọa độ chiều sâu tương đối
            norm_x, norm_y: tọa độ chuẩn hóa
            visibility: độ tin cậy

        Trả về [] nếu không phát hiện người
        hoặc độ tin cậy trung bình không đạt yêu cầu.
        """

        if not self.landmarks:
            return []

        # Các khớp quan trọng để đánh giá tư thế
        key_indices = [11, 12, 23, 24, 25, 26]

        # Kiểm tra số lượng landmarks
        if len(self.landmarks) <= max(key_indices):
            return []

        # Tính visibility trung bình
        avg_vis = sum(
            getattr(
                self.landmarks[i],
                "visibility",
                1.0
            )
            for i in key_indices
        ) / len(key_indices)

        if avg_vis < min_visibility:
            return []

        h, w, _ = img.shape

        lm_list = []

        for idx, lm in enumerate(self.landmarks):

            visibility = getattr(
                lm,
                "visibility",
                1.0
            )

            cx = int(lm.x * w)
            cy = int(lm.y * h)

            lm_list.append({

                "id": idx,

                "x": cx,
                "y": cy,

                "z": lm.z,

                "norm_x": lm.x,
                "norm_y": lm.y,

                "visibility": visibility

            })

            # Vẽ thêm điểm nếu được yêu cầu
            if draw and visibility > min_visibility:

                cv2.circle(
                    img,
                    (cx, cy),
                    5,
                    (0, 0, 255),
                    cv2.FILLED
                )

        return lm_list

    # =====================================================
    # 6. CLOSE
    # =====================================================

    def close(self):

        """
        Giải phóng tài nguyên MediaPipe.
        """

        if self.use_legacy:

            if hasattr(self, "pose"):
                self.pose.close()

        else:

            if hasattr(self, "landmarker"):
                self.landmarker.close()
