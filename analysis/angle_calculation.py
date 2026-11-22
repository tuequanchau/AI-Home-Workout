import math
from .landmark_utils import get_point_2d


def calculate_angle(a, b, c, min_visibility=0.5):
    """
    Tính góc ABC, trong đó B là đỉnh góc.

    Parameters
    ----------
    a, b, c:
        Tọa độ các điểm theo dạng (x, y), (x, y, z) hoặc (x, y, z, visibility).
    min_visibility:
        Ngưỡng độ tin cậy tối thiểu của landmark.

    Returns
    -------
    float: Góc từ 0 đến 180 độ, hoặc None nếu dữ liệu không hợp lệ.
    """
    if a is None or b is None or c is None:
        return None
    if len(a) < 2 or len(b) < 2 or len(c) < 2:
        return None

    for point in (a, b, c):
        if len(point) >= 4:
            visibility = point[3]
            if visibility < min_visibility:
                return None

    vector_ba = (a[0] - b[0], a[1] - b[1])
    vector_bc = (c[0] - b[0], c[1] - b[1])

    dot_product = vector_ba[0] * vector_bc[0] + vector_ba[1] * vector_bc[1]
    length_ba = math.sqrt(vector_ba[0] ** 2 + vector_ba[1] ** 2)
    length_bc = math.sqrt(vector_bc[0] ** 2 + vector_bc[1] ** 2)

    if length_ba == 0 or length_bc == 0:
        return None

    cos_angle = dot_product / (length_ba * length_bc)
    cos_angle = max(-1.0, min(1.0, cos_angle))

    return math.degrees(math.acos(cos_angle))


def calculate_distance(a, b, min_visibility=0.5):
    """
    Tính khoảng cách Euclid 2D giữa hai điểm a và b.
    """
    if a is None or b is None:
        return None
    if len(a) < 2 or len(b) < 2:
        return None

    for point in (a, b):
        if len(point) >= 4:
            if point[3] < min_visibility:
                return None

    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def calculate_average_angle(angle1, angle2):
    """
    Tính trung bình hai góc trái và phải, bỏ qua góc không hợp lệ (None).
    """
    valid_angles = [angle for angle in (angle1, angle2) if angle is not None]
    if not valid_angles:
        return None
    return sum(valid_angles) / len(valid_angles)


def get_joint_angle(landmarks, index_a, index_b, index_c, min_visibility=0.5):
    """
    Lấy tọa độ ba landmark và tính góc khớp tại đỉnh index_b.
    """
    point_a = get_point_2d(landmarks, index_a, min_visibility)
    point_b = get_point_2d(landmarks, index_b, min_visibility)
    point_c = get_point_2d(landmarks, index_c, min_visibility)
    return calculate_angle(point_a, point_b, point_c, min_visibility)


def get_distance_between(landmarks, index_a, index_b, min_visibility=0.5):
    """
    Lấy tọa độ hai landmark và tính khoảng cách 2D giữa chúng.
    """
    point_a = get_point_2d(landmarks, index_a, min_visibility)
    point_b = get_point_2d(landmarks, index_b, min_visibility)
    return calculate_distance(point_a, point_b, min_visibility)