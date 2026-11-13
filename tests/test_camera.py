# File: tests/test_camera.py
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from camera.camera import Camera


# --- 1. KIỂM TRA KHỞI TẠO (INITIALIZATION) ---

def test_camera_default_init():
    """1. Kiểm tra thông số mặc định khi khởi tạo Camera"""
    cam = Camera()
    assert cam.camera_id == 0
    assert cam.width == 640
    assert cam.height == 480
    assert cam.cap is None


def test_camera_custom_init():
    """2. Kiểm tra khởi tạo Camera với thông số tùy chỉnh"""
    cam = Camera(camera_id=1, width=1280, height=720)
    assert cam.camera_id == 1
    assert cam.width == 1280
    assert cam.height == 720
    assert cam.cap is None


# --- 2. KIỂM TRA MỞ CAMERA (START) ---

@patch("camera.camera.cv2.VideoCapture")
def test_camera_start_success(mock_video_capture):
    """3. Mở webcam thành công -> Trả về True và cài đúng độ phân giải"""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_video_capture.return_value = mock_cap

    cam = Camera(camera_id=0, width=640, height=480)
    result = cam.start()

    assert result is True
    mock_video_capture.assert_called_once_with(0)
    mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 640)
    mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 480)


@patch("camera.camera.cv2.VideoCapture")
def test_camera_start_failure(mock_video_capture):
    """4. Không tìm thấy webcam hoặc bị app khác chiếm -> Trả về False"""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_video_capture.return_value = mock_cap

    cam = Camera()
    result = cam.start()

    assert result is False


# --- 3. KIỂM TRA ĐỌC KHUNG HÌNH (GET_FRAME) ---

def test_get_frame_success():
    """5. Đọc frame thành công khi camera đang hoạt động"""
    cam = Camera()
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True

    # Tạo một bức ảnh đen giả lập kích thước 480x640 (3 kênh màu)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_cap.read.return_value = (True, fake_frame)
    cam.cap = mock_cap

    frame = cam.get_frame()
    assert frame is not None
    assert frame.shape == (480, 640, 3)


def test_get_frame_when_not_started():
    """6a. Gọi get_frame() khi chưa chạy start() -> Trả về None, không crash"""
    cam = Camera()
    assert cam.get_frame() is None


def test_get_frame_read_failure():
    """6b. Đang chạy nhưng mất tín hiệu webcam (read trả về False) -> Trả về None"""
    cam = Camera()
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)
    cam.cap = mock_cap

    assert cam.get_frame() is None


# --- 4. KIỂM TRA TẮT CAMERA (RELEASE) ---

def test_release_camera_when_opened():
    """7a. Giải phóng tài nguyên khi camera đang mở"""
    cam = Camera()
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    cam.cap = mock_cap

    cam.release()
    mock_cap.release.assert_called_once()


def test_release_camera_when_not_opened():
    """7b. Gọi release() khi camera chưa bật -> Không gây lỗi chương trình"""
    cam = Camera()
    cam.release()  # Phải chạy qua êm ái mà không báo lỗi