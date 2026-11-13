# File: tests/test_pose_detection.py
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import numpy as np

from camera.pose_detection import (
    PoseDetector,
    POSE_CONNECTIONS,
    MODEL_URL,
    MODEL_PATH,
)


def _make_fake_landmarks(visibility=0.9, count=33):
    """Hàm hỗ trợ tạo dữ liệu giả lập 33 điểm khớp của MediaPipe."""
    return [
        SimpleNamespace(
            x=round(0.1 + (i % 10) * 0.08, 4),
            y=round(0.1 + (i // 10) * 0.2, 4),
            z=-0.05 * i,
            visibility=visibility,
        )
        for i in range(count)
    ]


# --- 1. KIỂM TRA CẤU HÌNH & KHỞI TẠO ---

def test_pose_connections_valid():
    """1. Kiểm tra 35 đường nối khung xương có chỉ số hợp lệ (0 -> 32)"""
    assert len(POSE_CONNECTIONS) == 35
    for start_idx, end_idx in POSE_CONNECTIONS:
        assert 0 <= start_idx <= 32
        assert 0 <= end_idx <= 32


@patch("camera.pose_detection.urllib.request.urlretrieve")
@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_init_tasks_api_with_existing_model(mock_mp, mock_exists, mock_getsize, mock_urlretrieve):
    """2. Khởi tạo MediaPipe bản mới khi file model đã có sẵn -> Không tải lại"""
    del mock_mp.solutions  # Giả lập môi trường MediaPipe Tasks API (0.10.30+)

    detector = PoseDetector(detection_con=0.6, tracking_con=0.7)

    assert detector.use_legacy is False
    assert detector.landmarks == []
    mock_urlretrieve.assert_not_called()
    mock_mp.tasks.vision.PoseLandmarker.create_from_options.assert_called_once()


@patch("camera.pose_detection.urllib.request.urlretrieve")
@patch("camera.pose_detection.os.path.exists", return_value=False)
@patch("camera.pose_detection.mp")
def test_init_downloads_model_if_missing(mock_mp, mock_exists, mock_urlretrieve):
    """3. Tự động tải file model nếu máy chưa có sẵn"""
    del mock_mp.solutions

    PoseDetector()

    mock_urlretrieve.assert_called_once_with(MODEL_URL, MODEL_PATH)


@patch("camera.pose_detection.mp")
def test_init_legacy_api(mock_mp):
    """4. Khởi tạo ở chế độ tương thích MediaPipe bản cũ (use_legacy=True)"""
    detector = PoseDetector(mode=True, complexity=1)

    assert detector.use_legacy is True
    mock_mp.solutions.pose.Pose.assert_called_once()


# --- 2. KIỂM TRA NHẬN DIỆN & VẼ KHUNG XƯƠNG (FIND_POSE) ---

@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_find_pose_detected_and_draw(mock_mp, mock_exists, mock_getsize):
    """5. Nhận diện được người và vẽ chấm/đường nối khung xương lên ảnh"""
    del mock_mp.solutions
    fake_landmarks = _make_fake_landmarks(visibility=0.9)

    mock_landmarker = MagicMock()
    mock_landmarker.detect.return_value = SimpleNamespace(pose_landmarks=[fake_landmarks])
    mock_mp.tasks.vision.PoseLandmarker.create_from_options.return_value = mock_landmarker

    detector = PoseDetector()
    blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
    output_img = detector.find_pose(blank_img, draw=True)

    assert len(detector.landmarks) == 33
    assert np.any(output_img > 0)  # Xác nhận đã vẽ các điểm màu lên nền đen


@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_find_pose_detected_without_draw(mock_mp, mock_exists, mock_getsize):
    """6. Nhận diện được người nhưng draw=False -> Không vẽ đè lên ảnh gốc"""
    del mock_mp.solutions
    fake_landmarks = _make_fake_landmarks(visibility=0.9)

    mock_landmarker = MagicMock()
    mock_landmarker.detect.return_value = SimpleNamespace(pose_landmarks=[fake_landmarks])
    mock_mp.tasks.vision.PoseLandmarker.create_from_options.return_value = mock_landmarker

    detector = PoseDetector()
    blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
    output_img = detector.find_pose(blank_img, draw=False)

    assert len(detector.landmarks) == 33
    assert np.all(output_img == 0)


@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_find_pose_no_person(mock_mp, mock_exists, mock_getsize):
    """7. Không có người trong khung hình -> landmarks rỗng []"""
    del mock_mp.solutions
    mock_landmarker = MagicMock()
    mock_landmarker.detect.return_value = SimpleNamespace(pose_landmarks=[])
    mock_mp.tasks.vision.PoseLandmarker.create_from_options.return_value = mock_landmarker

    detector = PoseDetector()
    blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
    output_img = detector.find_pose(blank_img, draw=True)

    assert detector.landmarks == []
    assert np.all(output_img == 0)


# --- 3. KIỂM TRA TRÍCH XUẤT TỌA ĐỘ (GET_POSITION) ---

@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_get_position_valid_landmarks(mock_mp, mock_exists, mock_getsize):
    """8. Trả về đúng cấu trúc tọa độ 33 điểm và quy đổi chuẩn pixel"""
    del mock_mp.solutions
    detector = PoseDetector()
    detector.landmarks = _make_fake_landmarks(visibility=0.95)
    # Gán tọa độ cố định cho điểm 0 để kiểm tra phép nhân pixel (640x480)
    detector.landmarks[0] = SimpleNamespace(x=0.5, y=0.25, z=-0.1, visibility=0.95)

    img = np.zeros((480, 640, 3), dtype=np.uint8)
    lm_list = detector.get_position(img, draw=True, min_visibility=0.5)

    assert len(lm_list) == 33
    first_point = lm_list[0]
    assert set(first_point.keys()) == {"id", "x", "y", "z", "norm_x", "norm_y", "visibility"}
    assert first_point["id"] == 0
    assert first_point["x"] == 320  # 0.5 * 640
    assert first_point["y"] == 120  # 0.25 * 480
    assert first_point["visibility"] == 0.95
    assert np.any(img[:, :, 2] == 255)  # Xác nhận có vẽ chấm đỏ khi draw=True


@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_get_position_empty_or_low_visibility(mock_mp, mock_exists, mock_getsize):
    """9. Trả về [] khi chưa có landmarks hoặc 6 khớp trụ cột (vai, hông, gối) bị mờ"""
    del mock_mp.solutions
    detector = PoseDetector()
    img = np.zeros((480, 640, 3), dtype=np.uint8)

    # Trường hợp A: Chưa phát hiện được người
    assert detector.get_position(img) == []

    # Trường hợp B: Các khớp chính có độ tin cậy thấp (0.2 < 0.5)
    detector.landmarks = _make_fake_landmarks(visibility=0.2)
    assert detector.get_position(img, min_visibility=0.5) == []


# --- 4. KIỂM TRA GIẢI PHÓNG TÀI NGUYÊN (CLOSE) ---

@patch("camera.pose_detection.os.path.getsize", return_value=5_500_000)
@patch("camera.pose_detection.os.path.exists", return_value=True)
@patch("camera.pose_detection.mp")
def test_close_releases_resources(mock_mp, mock_exists, mock_getsize):
    """10. Đóng bộ nhận diện AI giải phóng RAM đúng cách ở cả 2 chế độ"""
    # Chế độ Tasks API mới
    del mock_mp.solutions
    mock_landmarker = MagicMock()
    mock_mp.tasks.vision.PoseLandmarker.create_from_options.return_value = mock_landmarker

    detector_new = PoseDetector()
    detector_new.close()
    mock_landmarker.close.assert_called_once()

    # Chế độ Legacy API cũ
    mock_mp.solutions = MagicMock()
    detector_old = PoseDetector()
    detector_old.close()
    detector_old.pose.close.assert_called_once()