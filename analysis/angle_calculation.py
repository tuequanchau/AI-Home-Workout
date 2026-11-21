"""Angle and distance helpers used by exercise analyzers."""
import math

from .landmark_utils import get_point_2d


def calculate_angle(a, b, c, min_visibility=0.5):
    """Return angle ABC in degrees, or None when the points are invalid."""
    if a is None or b is None or c is None:
        return None
    if len(a) < 2 or len(b) < 2 or len(c) < 2:
        return None

    for point in (a, b, c):
        if len(point) >= 4 and point[3] < min_visibility:
            return None

    bax, bay = float(a[0]) - float(b[0]), float(a[1]) - float(b[1])
    bcx, bcy = float(c[0]) - float(b[0]), float(c[1]) - float(b[1])

    len_ba = math.hypot(bax, bay)
    len_bc = math.hypot(bcx, bcy)
    if len_ba == 0 or len_bc == 0:
        return None

    cosine = (bax * bcx + bay * bcy) / (len_ba * len_bc)
    cosine = max(-1.0, min(1.0, cosine))
    return math.degrees(math.acos(cosine))


def calculate_average_angle(angle1, angle2):
    """Average the available angle values; return None if both are invalid."""
    valid_angles = [
        float(angle) for angle in (angle1, angle2)
        if angle is not None and math.isfinite(float(angle))
    ]
    if not valid_angles:
        return None
    return sum(valid_angles) / len(valid_angles)


def calculate_distance(point_a, point_b):
    """Calculate 2D Euclidean distance between two points."""
    if point_a is None or point_b is None:
        return None
    if len(point_a) < 2 or len(point_b) < 2:
        return None
    return math.hypot(
        float(point_a[0]) - float(point_b[0]),
        float(point_a[1]) - float(point_b[1]),
    )


def get_joint_angle(
    landmarks,
    index_a,
    index_b,
    index_c,
    min_visibility=0.5,
):
    """Get three landmarks and calculate the angle at index_b."""
    point_a = get_point_2d(landmarks, index_a, min_visibility)
    point_b = get_point_2d(landmarks, index_b, min_visibility)
    point_c = get_point_2d(landmarks, index_c, min_visibility)
    return calculate_angle(point_a, point_b, point_c)


def get_distance_between(
    landmarks,
    index_a,
    index_b,
    min_visibility=0.5,
):
    """Return 2D distance between two indexed landmarks."""
    point_a = get_point_2d(landmarks, index_a, min_visibility)
    point_b = get_point_2d(landmarks, index_b, min_visibility)
    return calculate_distance(point_a, point_b)
