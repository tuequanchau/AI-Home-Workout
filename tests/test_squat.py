import os
import sys
from unittest.mock import patch
import pytest

# Đảm bảo pytest luôn nhận diện đúng thư mục gốc AI-Home-Workout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Tránh lỗi ImportError nếu angle_calculation.py chưa cập nhật hàm get_joint_angle
import analysis.angle_calculation as angle_calc
if not hasattr(angle_calc, "get_joint_angle"):
    angle_calc.get_joint_angle = lambda *args, **kwargs: None

from analysis.squat import SquatCounter


def mock_knee_angles(left_angle, right_angle):
    """Giả lập kết quả trả về của hàm get_joint_angle cho chân trái (23,25,27) và phải (24,26,28)."""
    def fake_get_joint_angle(landmarks, p1, p2, p3, min_visibility):
        if (p1, p2, p3) == (23, 25, 27):
            return left_angle
        if (p1, p2, p3) == (24, 26, 28):
            return right_angle
        return None

    return fake_get_joint_angle


# =====================================================================
# 1. KIỂM THỬ KHỞI TẠO VÀ ĐẶT LẠI BỘ ĐẾM (__init__ & reset)
# =====================================================================
class TestSquatInitAndReset:
    def test_default_initialization(self):
        """Kiểm tra các giá trị ngưỡng và trạng thái mặc định khi khởi tạo."""
        counter = SquatCounter()
        assert counter.min_visibility == 0.5
        assert counter.standing_angle == 155
        assert counter.bottom_angle == 100
        assert counter.descent_angle == 120
        assert counter.state == "STANDING"
        assert counter.reps == 0
        assert counter.last_angle is None
        assert counter.last_feedback == "Đứng thẳng để bắt đầu tập."

    def test_custom_initialization(self):
        """Kiểm tra khởi tạo với các ngưỡng góc tùy chỉnh."""
        counter = SquatCounter(
            min_visibility=0.7,
            standing_angle=160,
            bottom_angle=90,
            descent_angle=130,
        )
        assert counter.min_visibility == 0.7
        assert counter.standing_angle == 160
        assert counter.bottom_angle == 90
        assert counter.descent_angle == 130

    def test_reset_counter(self):
        """Kiểm tra hàm reset() đưa bộ đếm về trạng thái ban đầu."""
        counter = SquatCounter()
        counter.state = "BOTTOM"
        counter.reps = 4
        counter.last_angle = 92.5
        counter.last_feedback = "Đã đạt vị trí Squat. Bây giờ hãy đứng lên."

        counter.reset()

        assert counter.state == "STANDING"
        assert counter.reps == 0
        assert counter.last_angle is None
        assert counter.last_feedback == "Đứng thẳng để bắt đầu tập."


# =====================================================================
# 2. KIỂM THỬ TÍNH GÓC HAI ĐẦU GỐI (get_knee_angles)
# =====================================================================
class TestGetKneeAngles:
    def test_both_knees_valid(self):
        """Nhận diện được cả hai chân -> tính trung bình cộng hai góc."""
        counter = SquatCounter()
        with patch("analysis.squat.get_joint_angle", side_effect=mock_knee_angles(100.0, 110.0)):
            avg, left, right = counter.get_knee_angles(landmarks=[])
            assert avg == pytest.approx(105.0)
            assert left == 100.0
            assert right == 110.0

    def test_only_left_knee_valid(self):
        """Chỉ nhìn thấy chân trái (chân phải None) -> lấy góc chân trái."""
        counter = SquatCounter()
        with patch("analysis.squat.get_joint_angle", side_effect=mock_knee_angles(95.0, None)):
            avg, left, right = counter.get_knee_angles(landmarks=[])
            assert avg == pytest.approx(95.0)
            assert left == 95.0
            assert right is None

    def test_only_right_knee_valid(self):
        """Chỉ nhìn thấy chân phải (chân trái None) -> lấy góc chân phải."""
        counter = SquatCounter()
        with patch("analysis.squat.get_joint_angle", side_effect=mock_knee_angles(None, 120.0)):
            avg, left, right = counter.get_knee_angles(landmarks=[])
            assert avg == pytest.approx(120.0)
            assert left is None
            assert right == 120.0

    def test_both_knees_none(self):
        """Không nhận diện được chân nào -> trả về (None, None, None)."""
        counter = SquatCounter()
        with patch("analysis.squat.get_joint_angle", side_effect=mock_knee_angles(None, None)):
            avg, left, right = counter.get_knee_angles(landmarks=[])
            assert avg is None
            assert left is None
            assert right is None


# =====================================================================
# 3. KIỂM THỬ CHU TRÌNH CHUYỂN TRẠNG THÁI VÀ ĐẾM REP (update)
# =====================================================================
class TestSquatUpdateAndCounting:
    def _send_angles(self, counter, left, right=None):
        """Nếu chỉ truyền 1 góc, mặc định hai chân có góc bằng nhau."""
        if right is None and left is not None:
            right = left
        with patch("analysis.squat.get_joint_angle", side_effect=mock_knee_angles(left, right)):
            return counter.update(landmarks=[])

    def test_invalid_frame_returns_valid_false(self):
        """Khung hình mất dấu cả hai đầu gối -> valid=False, giữ nguyên reps và state."""
        counter = SquatCounter()
        counter.reps = 2
        counter.state = "DESCENDING"
        counter.last_angle = 115.0

        res = self._send_angles(counter, None, None)

        assert res["exercise"] == "Squat"
        assert res["valid"] is False
        assert res["angle"] is None
        assert res["left_angle"] is None
        assert res["right_angle"] is None
        assert res["reps"] == 2
        assert res["state"] == "DESCENDING"
        assert "Không nhận diện được đầu gối" in res["feedback"]
        assert counter.last_angle == 115.0

    def test_complete_one_full_rep(self):
        """Chu trình chuẩn: STANDING -> DESCENDING -> BOTTOM -> ASCENDING -> STANDING (+1 rep)."""
        counter = SquatCounter()

        # 1. Đứng thẳng (170 độ)
        r1 = self._send_angles(counter, 170.0)
        assert r1["state"] == "STANDING"
        assert r1["reps"] == 0
        assert r1["valid"] is True

        # 2. Bắt đầu hạ người (< 120 độ)
        r2 = self._send_angles(counter, 115.0)
        assert r2["state"] == "DESCENDING"
        assert r2["reps"] == 0

        # 3. Xuống tới đáy Squat (<= 100 độ)
        r3 = self._send_angles(counter, 90.0)
        assert r3["state"] == "BOTTOM"
        assert r3["reps"] == 0

        # 4. Bắt đầu đứng lên (> 100 + 5 = 105 độ)
        r4 = self._send_angles(counter, 130.0)
        assert r4["state"] == "ASCENDING"
        assert r4["reps"] == 0

        # 5. Đứng thẳng hoàn toàn (>= 155 độ) -> cộng 1 rep
        r5 = self._send_angles(counter, 165.0)
        assert r5["state"] == "STANDING"
        assert r5["reps"] == 1
        assert r5["angle"] == 165.0
        assert counter.last_angle == 165.0

    def test_multiple_reps_sequence(self):
        """Thực hiện liên tiếp 3 nhịp Squat hoàn chỉnh."""
        counter = SquatCounter()

        for _ in range(3):
            self._send_angles(counter, 170.0)  # STANDING
            self._send_angles(counter, 110.0)  # DESCENDING
            self._send_angles(counter, 95.0)   # BOTTOM
            self._send_angles(counter, 125.0)  # ASCENDING
            res = self._send_angles(counter, 160.0)  # STANDING (+1)

        assert res["reps"] == 3
        assert res["state"] == "STANDING"

    def test_aborted_squat_not_deep_enough_does_not_count(self):
        """Hạ người chưa tới đáy (chưa <= 100) đã đứng thẳng lại -> về STANDING, không cộng rep."""
        counter = SquatCounter()

        self._send_angles(counter, 115.0)  # DESCENDING
        assert counter.state == "DESCENDING"

        # Đứng thẳng lại ngay từ DESCENDING (>= 155)
        res = self._send_angles(counter, 160.0)
        assert res["state"] == "STANDING"
        assert res["reps"] == 0

    def test_drop_back_to_bottom_during_ascending(self):
        """Đang đứng lên (ASCENDING) nhưng lại hạ người xuống đáy (<= 100) -> quay lại BOTTOM."""
        counter = SquatCounter()

        self._send_angles(counter, 110.0)  # DESCENDING
        self._send_angles(counter, 95.0)   # BOTTOM
        self._send_angles(counter, 120.0)  # ASCENDING
        assert counter.state == "ASCENDING"

        # Hạ xuống lại đáy trước khi đứng thẳng
        res_back = self._send_angles(counter, 98.0)
        assert res_back["state"] == "BOTTOM"
        assert res_back["reps"] == 0

        # Đứng lên lại hoàn chỉnh -> lúc này mới tính 1 rep
        self._send_angles(counter, 130.0)  # ASCENDING
        res_done = self._send_angles(counter, 160.0)  # STANDING
        assert res_done["reps"] == 1

    def test_bottom_hysteresis_buffer(self):
        """Tại BOTTOM, góc phải vượt quá bottom_angle + 5 (105 độ) mới chuyển sang ASCENDING."""
        counter = SquatCounter(bottom_angle=100)

        self._send_angles(counter, 110.0)  # DESCENDING
        self._send_angles(counter, 95.0)   # BOTTOM

        # Góc nhích lên 105 (bằng bottom_angle + 5, chưa lớn hơn hẳn) -> vẫn giữ BOTTOM
        res_hold = self._send_angles(counter, 105.0)
        assert res_hold["state"] == "BOTTOM"

        # Góc vượt 105 (105.1) -> chuyển sang ASCENDING
        res_up = self._send_angles(counter, 105.1)
        assert res_up["state"] == "ASCENDING"

    def test_boundary_angles(self):
        """Kiểm tra chính xác tại các giá trị biên 120, 100 và 155 độ."""
        counter = SquatCounter(standing_angle=155, bottom_angle=100, descent_angle=120)

        # Góc == 120 (không < 120) -> vẫn STANDING
        assert self._send_angles(counter, 120.0)["state"] == "STANDING"
        # Góc == 119.9 (< 120) -> DESCENDING
        assert self._send_angles(counter, 119.9)["state"] == "DESCENDING"
        # Góc == 100 (<= 100) -> BOTTOM
        assert self._send_angles(counter, 100.0)["state"] == "BOTTOM"
        # Góc == 110 (> 105) -> ASCENDING
        assert self._send_angles(counter, 110.0)["state"] == "ASCENDING"
        # Góc == 155 (>= 155) -> STANDING và reps == 1
        res = self._send_angles(counter, 155.0)
        assert res["state"] == "STANDING"
        assert res["reps"] == 1

    def test_single_leg_detected_in_update_output(self):
        """Khi một chân bị che khuất (None), kết quả trả về làm tròn đúng chân còn lại."""
        counter = SquatCounter()
        with patch("analysis.squat.get_joint_angle", side_effect=mock_knee_angles(112.345, None)):
            res = counter.update(landmarks=[])

        assert res["valid"] is True
        assert res["angle"] == 112.34
        assert res["left_angle"] == 112.34
        assert res["right_angle"] is None