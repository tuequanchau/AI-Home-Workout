import math
import os
import sys
from types import SimpleNamespace
import pytest

# Đảm bảo pytest luôn nhận diện đúng thư mục gốc AI-Home-Workout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analysis.landmark_utils import (
    LANDMARKS,
    get_landmark,
    is_landmark_valid,
    get_point_2d,
    get_point_3d,
)


# =====================================================================
# 1. KIỂM THỬ HẰNG SỐ CHỈ SỐ KHỚP (LANDMARKS)
# =====================================================================
class TestLandmarksMapping:
    def test_mediapipe_landmark_indices(self):
        """Kiểm tra đầy đủ 12 khớp và đúng chỉ số chuẩn của MediaPipe Pose."""
        expected = {
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
            "RIGHT_ANKLE": 28,
        }
        assert LANDMARKS == expected


# =====================================================================
# 2. KIỂM THỬ HÀM TRÍCH XUẤT TỌA ĐỘ (get_landmark)
# =====================================================================
class TestGetLandmark:
    def test_list_of_mediapipe_objects(self):
        """Hỗ trợ list chứa object có thuộc tính x, y, z, visibility."""
        lm_full = SimpleNamespace(x=0.25, y=0.5, z=-0.1, visibility=0.95)
        lm_minimal = SimpleNamespace(x=10, y=20)  # Thiếu z, visibility -> dùng mặc định 0.0 và 1.0
        landmarks = [lm_full, lm_minimal]

        assert get_landmark(landmarks, 0) == (0.25, 0.5, -0.1, 0.95)
        assert get_landmark(landmarks, 1) == (10.0, 20.0, 0.0, 1.0)

    def test_list_of_tuples_and_lists(self):
        """Hỗ trợ điểm dạng tuple/list có 2, 3 hoặc 4 phần tử."""
        landmarks = [
            (0.1, 0.2),                 # Chỉ có x, y -> z=0.0, visibility=1.0
            [0.3, 0.4, 0.5],            # Có x, y, z -> visibility=1.0
            (0.6, 0.7, 0.8, 0.85),      # Đủ 4 giá trị
        ]
        assert get_landmark(landmarks, 0) == (0.1, 0.2, 0.0, 1.0)
        assert get_landmark(landmarks, 1) == (0.3, 0.4, 0.5, 1.0)
        assert get_landmark(landmarks, 2) == (0.6, 0.7, 0.8, 0.85)

    def test_dict_landmarks_with_int_and_str_keys(self):
        """Hỗ trợ dictionary có key dạng số nguyên hoặc chuỗi, và điểm dạng dict."""
        landmarks = {
            11: {"x": 0.4, "y": 0.6, "z": -0.2, "visibility": 0.9},
            "12": {"x": 0.5, "y": 0.7},  # Key chuỗi, thiếu z và visibility
        }
        assert get_landmark(landmarks, 11) == (0.4, 0.6, -0.2, 0.9)
        assert get_landmark(landmarks, 12) == (0.5, 0.7, 0.0, 1.0)

    @pytest.mark.parametrize(
        "landmarks, index",
        [
            ([], 0),                                            # IndexError: list rỗng
            ([None], 0),                                        # Phần tử là None
            ({}, 11),                                           # Key không tồn tại trong dict
            ([(0.5,)], 0),                                      # Tuple chỉ có 1 phần tử (< 2)
            ([{"x": None, "y": 0.5}], 0),                       # x bị None
            ([{"x": 0.5, "y": None}], 0),                       # y bị None
            ([SimpleNamespace(x=0.5)], 0),                      # Object thiếu thuộc tính y (AttributeError)
            ([{"x": "not_a_number", "y": 0.5}], 0),             # Không thể ép kiểu float (ValueError)
            (None, 0),                                          # landmarks là None (TypeError)
        ],
    )
    def test_invalid_inputs_return_none(self, landmarks, index):
        """Các trường hợp thiếu dữ liệu, sai kiểu hoặc vượt chỉ số đều trả về None."""
        assert get_landmark(landmarks, index) is None

    @pytest.mark.parametrize(
        "bad_val",
        [float("nan"), float("inf"), float("-inf")],
    )
    def test_non_finite_coordinates_return_none(self, bad_val):
        """Nếu x, y, z hoặc visibility chứa NaN hoặc vô cực (inf) -> trả về None."""
        assert get_landmark([(bad_val, 0.5, 0.0, 1.0)], 0) is None
        assert get_landmark([(0.5, bad_val, 0.0, 1.0)], 0) is None
        assert get_landmark([(0.5, 0.5, bad_val, 1.0)], 0) is None
        assert get_landmark([(0.5, 0.5, 0.0, bad_val)], 0) is None


# =====================================================================
# 3. KIỂM THỬ ĐỘ TIN CẬY (is_landmark_valid)
# =====================================================================
class TestIsLandmarkValid:
    def test_visibility_thresholds(self):
        """Hợp lệ khi visibility >= min_visibility, ngược lại False."""
        landmarks = [
            (0.1, 0.2, 0.0, 0.8),   # > 0.5 -> True
            (0.1, 0.2, 0.0, 0.5),   # == 0.5 (giá trị biên) -> True
            (0.1, 0.2, 0.0, 0.49),  # < 0.5 -> False
        ]
        assert is_landmark_valid(landmarks, 0, min_visibility=0.5) is True
        assert is_landmark_valid(landmarks, 1, min_visibility=0.5) is True
        assert is_landmark_valid(landmarks, 2, min_visibility=0.5) is False
        assert is_landmark_valid(landmarks, 2, min_visibility=0.4) is True

    def test_missing_landmark_is_invalid(self):
        """Landmark không tồn tại trả về False."""
        assert is_landmark_valid([], 5) is False


# =====================================================================
# 4. KIỂM THỬ LẤY TỌA ĐỘ 2D VÀ 3D (get_point_2d & get_point_3d)
# =====================================================================
class TestGetPoint2DAnd3D:
    def test_get_point_2d_valid_and_boundary(self):
        """Trả về (x, y) khi visibility >= min_visibility, trả về None khi thấp hơn."""
        landmarks = [
            (0.25, 0.75, -0.3, 0.9),   # Hợp lệ
            (0.1, 0.2, 0.0, 0.5),      # Đúng ngưỡng biên 0.5 -> hợp lệ
            (0.1, 0.2, 0.0, 0.49),     # Dưới ngưỡng -> None
        ]
        assert get_point_2d(landmarks, 0) == (0.25, 0.75)
        assert get_point_2d(landmarks, 1) == (0.1, 0.2)
        assert get_point_2d(landmarks, 2) is None
        assert get_point_2d(landmarks, 99) is None

    def test_get_point_3d_valid_and_boundary(self):
        """Trả về (x, y, z) khi visibility >= min_visibility, trả về None khi thấp hơn."""
        landmarks = [
            (0.25, 0.75, -0.3, 0.9),   # Đủ 3 tọa độ
            (0.4, 0.6),                # Thiếu z -> mặc định z = 0.0, visibility = 1.0
            (0.1, 0.2, 0.3, 0.5),      # Đúng ngưỡng biên 0.5 -> hợp lệ
            (0.1, 0.2, 0.3, 0.3),      # Dưới ngưỡng -> None
        ]
        assert get_point_3d(landmarks, 0) == (0.25, 0.75, -0.3)
        assert get_point_3d(landmarks, 1) == (0.4, 0.6, 0.0)
        assert get_point_3d(landmarks, 2) == (0.1, 0.2, 0.3)
        assert get_point_3d(landmarks, 3) is None
        assert get_point_3d(landmarks, 99) is None