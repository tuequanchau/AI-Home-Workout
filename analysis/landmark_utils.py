
import math


# Các chỉ số landmarks theo MediaPipe Pose
LANDMARKS = {
    "LEFT_SHOULDER": 11,
    "RIGHT_SHOULDER": 12,
    "LEFT_ELBOW": 13,
    "RIGHT_ELBOW": 14,
    "LEFT_WRIST": 15,
    "RIGHT_WRIST": 16,
    "LEFT_HIP": 23,
    "RIGHT_HIP": 24,
    "LEFT_KNEE": 25,
    "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27,
    "RIGHT_ANKLE": 28
}


def get_landmark(landmarks, index):
    """
    Lấy tọa độ một landmark.

    Hỗ trợ:
    - List các landmark.
    - Dictionary có key là chỉ số landmark.
    - Object có thuộc tính x, y, z, visibility.

    Trả về:
    (x, y, z, visibility)
    """

    try:
        if isinstance(landmarks, dict):
            point = landmarks.get(index)

            if point is None:
                point = landmarks.get(str(index))
        else:
            point = landmarks[index]

        if point is None:
            return None

        if isinstance(point, dict):
            x = point.get("x")
            y = point.get("y")
            z = point.get("z", 0.0)
            visibility = point.get("visibility", 1.0)

        elif isinstance(point, (list, tuple)):
            if len(point) < 2:
                return None

            x = point[0]
            y = point[1]
            z = point[2] if len(point) > 2 else 0.0
            visibility = point[3] if len(point) > 3 else 1.0

        else:
            x = point.x
            y = point.y
            z = getattr(point, "z", 0.0)
            visibility = getattr(point, "visibility", 1.0)

        if x is None or y is None:
            return None

        values = [x, y, z, visibility]

        if not all(math.isfinite(float(value)) for value in values):
            return None

        return (
            float(x),
            float(y),
            float(z),
            float(visibility)
        )

    except (IndexError, KeyError, TypeError, AttributeError, ValueError):
        return None


def is_landmark_valid(landmarks, index, min_visibility=0.5):
    """
    Kiểm tra landmark có đủ độ tin cậy hay không.
    """

    point = get_landmark(landmarks, index)

    if point is None:
        return False

    return point[3] >= min_visibility


def get_point_2d(landmarks, index, min_visibility=0.5):
    """
    Trả về tọa độ (x, y) nếu landmark hợp lệ.
    """

    point = get_landmark(landmarks, index)

    if point is None:
        return None

    if point[3] < min_visibility:
        return None

    return point[0], point[1]


def get_point_3d(landmarks, index, min_visibility=0.5):
    """
    Trả về tọa độ (x, y, z) nếu landmark hợp lệ.
    """

    point = get_landmark(landmarks, index)

    if point is None:
        return None

    if point[3] < min_visibility:
        return None

    return point[0], point[1], point[2]
