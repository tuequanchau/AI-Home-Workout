# File: tests/test_angles.py
import pytest
# Lưu ý: Nếu file trong thư mục analysis tên là angles.py thì đổi angle_calculation thành angles
from angle_calculation import calculate_angle, calculate_average_angle

# --- NHÓM 1: KIỂM THỬ HÀM TÍNH GÓC (calculate_angle) ---

def test_standing_straight():
    """1. Đứng thẳng -> Góc phải bằng 180 độ"""
    assert calculate_angle((0, 0), (0, 5), (0, 10)) == pytest.approx(180.0)

def test_squat_right_angle():
    """2. Squat vuông góc -> Góc phải bằng 90 độ"""
    assert calculate_angle((5, 0), (0, 0), (0, 5)) == pytest.approx(90.0)

def test_duplicate_points_returns_none():
    """3. Điểm tọa độ bị trùng (độ dài vector = 0) -> Trả về None"""
    assert calculate_angle((0, 0), (0, 0), (0, 5)) is None

def test_low_visibility_returns_none():
    """4. Khớp bị che khuất (visibility < 0.5) -> Trả về None"""
    a = (5, 0, 0, 0.9)   # Rõ nét (0.9)
    b = (0, 0, 0, 0.2)   # Bị mờ (0.2 < 0.5)
    c = (0, 5, 0, 0.8)   # Rõ nét (0.8)
    assert calculate_angle(a, b, c) is None

def test_invalid_input_returns_none():
    """5. Dữ liệu đầu vào bị rỗng hoặc thiếu tọa độ -> Trả về None"""
    assert calculate_angle(None, (0, 0), (0, 5)) is None
    assert calculate_angle((0,), (0, 0), (0, 5)) is None


# --- NHÓM 2: KIỂM THỬ HÀM TÍNH GÓC TRUNG BÌNH (calculate_average_angle) ---

def test_average_both_valid():
    """6. Cả hai chân đều rõ -> Tính trung bình cộng bình thường"""
    assert calculate_average_angle(90.0, 100.0) == pytest.approx(95.0)

def test_average_one_leg_obscured():
    """7. Một chân bị khuất (None) -> Lấy góc của chân còn lại"""
    assert calculate_average_angle(90.0, None) == pytest.approx(90.0)
    assert calculate_average_angle(None, 120.0) == pytest.approx(120.0)

def test_average_both_obscured():
    """8. Cả hai chân đều bị khuất -> Trả về None"""
    assert calculate_average_angle(None, None) is None