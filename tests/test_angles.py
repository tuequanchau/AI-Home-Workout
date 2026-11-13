# File: tests/test_angles.py
import math

def calculate_angle(a, b, c):
    """Công thức toán học tính góc giữa 3 khớp (Hông - Gối - Cổ chân)"""
    # Bảo vệ app: Nếu camera bị che làm 2 điểm trùng nhau thì trả về 0 độ
    if a == b or b == c:
        return 0.0
    
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    
    if angle > 180.0:
        angle = 360.0 - angle
        
    return round(angle, 1)

# --- 3 KỊCH BẢN KIỂM THỬ TỰ ĐỘNG ---

def test_standing_straight():
    """1. Trường hợp chuẩn: Đứng thẳng chân -> Góc gối phải bằng 180 độ"""
    assert calculate_angle((0, 0), (0, 5), (0, 10)) == 180.0

def test_squat_right_angle():
    """2. Trường hợp chuẩn: Squat đùi vuông góc bắp chân -> Góc gối bằng 90 độ"""
    assert calculate_angle((5, 0), (0, 0), (0, 5)) == 90.0

def test_edge_case_duplicate_points():
    """3. Trường hợp lỗi camera: Điểm tọa độ bị trùng -> Trả về 0.0, không sập app"""
    assert calculate_angle((0, 0), (0, 0), (0, 5)) == 0.0