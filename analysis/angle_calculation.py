
import math


def calculate_angle(a, b, c, min_visibility=0.5):
    """
    Tính góc ABC, trong đó B là đỉnh góc.

    Parameters
    ----------
    a, b, c:
        Tọa độ các điểm theo dạng:
        (x, y, z, visibility)
        hoặc (x, y, z)

    min_visibility:
        Ngưỡng độ tin cậy tối thiểu của landmark.

    Returns
    -------
    float:
        Góc từ 0 đến 180 độ.
    None:
        Nếu dữ liệu không hợp lệ hoặc landmark không đủ tin cậy.
    """

    # 1. Kiểm tra dữ liệu đầu vào
    if a is None or b is None or c is None:
        return None

    if len(a) < 2 or len(b) < 2 or len(c) < 2:
        return None

    # 2. Kiểm tra visibility nếu dữ liệu có chứa giá trị này
    for point in (a, b, c):
        if len(point) >= 4:
            visibility = point[3]

            if visibility < min_visibility:
                return None

    # 3. Tạo hai vector BA và BC
    vector_ba = (
        a[0] - b[0],
        a[1] - b[1]
    )

    vector_bc = (
        c[0] - b[0],
        c[1] - b[1]
    )

    # 4. Tính tích vô hướng
    dot_product = (
        vector_ba[0] * vector_bc[0]
        + vector_ba[1] * vector_bc[1]
    )

    # 5. Tính độ dài hai vector
    length_ba = math.sqrt(
        vector_ba[0] ** 2 + vector_ba[1] ** 2
    )

    length_bc = math.sqrt(
        vector_bc[0] ** 2 + vector_bc[1] ** 2
    )

    # 6. Tránh chia cho 0
    if length_ba == 0 or length_bc == 0:
        return None

    # 7. Tính cos của góc
    cos_angle = dot_product / (length_ba * length_bc)

    # Giới hạn cos trong [-1, 1] để tránh lỗi số thực
    cos_angle = max(-1.0, min(1.0, cos_angle))

    # 8. Chuyển từ radian sang độ
    angle = math.degrees(math.acos(cos_angle))

    return angle


def calculate_average_angle(angle1, angle2):
    """
    Tính trung bình hai góc trái và phải.
    Bỏ qua góc không hợp lệ.
    """

    valid_angles = [
        angle for angle in (angle1, angle2)
        if angle is not None
    ]

    if not valid_angles:
        return None

    return sum(valid_angles) / len(valid_angles)
