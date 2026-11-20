import os
import sys
from unittest.mock import patch
import pytest

# Đảm bảo pytest luôn nhận diện đúng thư mục gốc AI-Home-Workout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Tránh lỗi ImportError nếu angle_calculation.py chưa cập nhật hàm get_distance_between
import analysis.angle_calculation as angle_calc
if not hasattr(angle_calc, "get_distance_between"):
    angle_calc.get_distance_between = lambda *args, **kwargs: None

from analysis.jumping_jack import JumpingJackCounter


def mock_pose_environment(arms_up, ankle_dist, hip_dist):
    """
    Hàm hỗ trợ tạo dữ liệu giả lập cho get_point_2d và get_distance_between
    mà không phụ thuộc vào định dạng raw landmarks bên ngoài.
    """
    def fake_get_point_2d(landmarks, idx, min_visibility):
        if arms_up is None:
            return None
        # Vai (11, 12) đặt tại y = 200; cổ tay (15, 16) nhỏ hơn 200 nếu giơ cao
        shoulders = {11: (100, 200), 12: (200, 200)}
        wrists_y = 100 if arms_up else 300
        wrists = {15: (90, wrists_y), 16: (210, wrists_y)}
        points = {**shoulders, **wrists}
        return points.get(idx)

    def fake_get_distance_between(landmarks, p1, p2, min_visibility):
        if (p1, p2) == (27, 28):
            return ankle_dist
        if (p1, p2) == (23, 24):
            return hip_dist
        return None

    return fake_get_point_2d, fake_get_distance_between


# =====================================================================
# 1. KIỂM THỬ KHỞI TẠO VÀ ĐẶT LẠI TRẠNG THÁI (__init__ & reset)
# =====================================================================
class TestJumpingJackInitAndReset:
    def test_default_initialization(self):
        """Kiểm tra các giá trị mặc định khi vừa khởi tạo bộ đếm."""
        counter = JumpingJackCounter()
        assert counter.min_visibility == 0.5
        assert counter.open_leg_ratio == 1.5
        assert counter.closed_leg_ratio == 1.15
        assert counter.stable_frames == 2
        assert counter.state == "CLOSED"
        assert counter.reps == 0
        assert counter.open_frames == 0
        assert counter.closed_frames == 0
        assert counter.last_feedback == "Đứng khép chân, hai tay đặt dọc thân người."

    def test_reset_counter(self):
        """Kiểm tra hàm reset() đưa toàn bộ thông số về trạng thái ban đầu."""
        counter = JumpingJackCounter()
        counter.state = "OPEN"
        counter.reps = 5
        counter.open_frames = 3
        counter.closed_frames = 1

        counter.reset()

        assert counter.state == "CLOSED"
        assert counter.reps == 0
        assert counter.open_frames == 0
        assert counter.closed_frames == 0
        assert counter.last_feedback == "Đứng khép chân để bắt đầu."


# =====================================================================
# 2. KIỂM THỬ NHẬN DIỆN VỊ TRÍ TAY (detect_arm_position)
# =====================================================================
class TestDetectArmPosition:
    def test_both_arms_up(self):
        """Hai cổ tay cao hơn hai vai (tọa độ y nhỏ hơn) -> True."""
        counter = JumpingJackCounter()
        points = {
            11: (100, 200),  # left_shoulder
            12: (200, 200),  # right_shoulder
            15: (90, 120),   # left_wrist < left_shoulder
            16: (210, 130),  # right_wrist < right_shoulder
        }
        with patch("analysis.jumping_jack.get_point_2d", side_effect=lambda lm, i, v: points[i]):
            assert counter.detect_arm_position(landmarks=[]) is True

    def test_both_arms_down(self):
        """Hai cổ tay thấp hơn hoặc ngang vai -> False."""
        counter = JumpingJackCounter()
        points = {
            11: (100, 200),
            12: (200, 200),
            15: (90, 250),
            16: (210, 200),  # Bằng vai vẫn tính là chưa giơ cao (<)
        }
        with patch("analysis.jumping_jack.get_point_2d", side_effect=lambda lm, i, v: points[i]):
            assert counter.detect_arm_position(landmarks=[]) is False

    def test_only_one_arm_up(self):
        """Chỉ giơ một tay -> False."""
        counter = JumpingJackCounter()
        points = {
            11: (100, 200),
            12: (200, 200),
            15: (90, 100),   # Tay trái giơ
            16: (210, 300),  # Tay phải hạ
        }
        with patch("analysis.jumping_jack.get_point_2d", side_effect=lambda lm, i, v: points[i]):
            assert counter.detect_arm_position(landmarks=[]) is False

    @pytest.mark.parametrize("missing_idx", [11, 12, 15, 16])
    def test_missing_any_arm_landmark_returns_none(self, missing_idx):
        """Thiếu bất kỳ điểm vai hoặc cổ tay nào -> trả về None."""
        counter = JumpingJackCounter()
        points = {11: (100, 200), 12: (200, 200), 15: (90, 100), 16: (210, 100)}
        points[missing_idx] = None
        with patch("analysis.jumping_jack.get_point_2d", side_effect=lambda lm, i, v: points[i]):
            assert counter.detect_arm_position(landmarks=[]) is None


# =====================================================================
# 3. KIỂM THỬ TÍNH TỶ LỆ MỞ CHÂN (get_leg_ratio)
# =====================================================================
class TestGetLegRatio:
    def test_valid_leg_ratio(self):
        """Tính đúng tỷ lệ khoảng cách mắt cá chân / khoảng cách hông."""
        counter = JumpingJackCounter()
        _, fake_dist = mock_pose_environment(arms_up=True, ankle_dist=180.0, hip_dist=100.0)
        with patch("analysis.jumping_jack.get_distance_between", side_effect=fake_dist):
            assert counter.get_leg_ratio(landmarks=[]) == pytest.approx(1.8)

    def test_missing_ankle_or_hip_returns_none(self):
        """Trả về None khi không đo được khoảng cách chân hoặc hông."""
        counter = JumpingJackCounter()
        _, fake_dist_no_ankle = mock_pose_environment(True, ankle_dist=None, hip_dist=100.0)
        with patch("analysis.jumping_jack.get_distance_between", side_effect=fake_dist_no_ankle):
            assert counter.get_leg_ratio(landmarks=[]) is None

        _, fake_dist_no_hip = mock_pose_environment(True, ankle_dist=150.0, hip_dist=None)
        with patch("analysis.jumping_jack.get_distance_between", side_effect=fake_dist_no_hip):
            assert counter.get_leg_ratio(landmarks=[]) is None

    def test_zero_hip_distance_prevents_zero_division(self):
        """Khoảng cách hông bằng 0 trả về None thay vì lỗi chia cho 0."""
        counter = JumpingJackCounter()
        _, fake_dist = mock_pose_environment(True, ankle_dist=150.0, hip_dist=0)
        with patch("analysis.jumping_jack.get_distance_between", side_effect=fake_dist):
            assert counter.get_leg_ratio(landmarks=[]) is None


# =====================================================================
# 4. KIỂM THỬ CHU TRÌNH CHUYỂN TRẠNG THÁI VÀ ĐẾM REP (update)
# =====================================================================
class TestJumpingJackUpdateAndCounting:
    def _send_frame(self, counter, arms_up, ankle_dist, hip_dist=100.0):
        fake_pt, fake_dist = mock_pose_environment(arms_up, ankle_dist, hip_dist)
        with patch("analysis.jumping_jack.get_point_2d", side_effect=fake_pt), \
             patch("analysis.jumping_jack.get_distance_between", side_effect=fake_dist):
            return counter.update(landmarks=[])

    def test_invalid_frame_resets_stable_counters(self):
        """Khung hình mất dấu tay/chân -> valid=False và reset bộ đếm ổn định."""
        counter = JumpingJackCounter()
        counter.open_frames = 1
        counter.closed_frames = 1

        res = self._send_frame(counter, arms_up=None, ankle_dist=150.0)

        assert res["valid"] is False
        assert res["reps"] == 0
        assert res["state"] == "CLOSED"
        assert "Không nhận diện rõ tay hoặc chân" in res["feedback"]
        assert counter.open_frames == 0
        assert counter.closed_frames == 0

    def test_stable_frames_filtering_prevents_false_count(self):
        """Cần đủ stable_frames=2 khung hình liên tiếp mới đổi trạng thái (chống nhiễu)."""
        counter = JumpingJackCounter(stable_frames=2)

        # Khung 1 mở -> chưa đủ 2 khung nên vẫn ở CLOSED
        res1 = self._send_frame(counter, arms_up=True, ankle_dist=160.0)
        assert res1["state"] == "CLOSED"
        assert counter.open_frames == 1

        # Khung 2 bị nhiễu (chưa mở đủ rộng) -> open_frames bị reset về 0
        res2 = self._send_frame(counter, arms_up=True, ankle_dist=120.0)
        assert res2["state"] == "CLOSED"
        assert counter.open_frames == 0

    def test_complete_one_full_rep(self):
        """Chu trình chuẩn CLOSED -> OPEN (2 frames) -> CLOSED (2 frames) tính 1 rep."""
        counter = JumpingJackCounter(stable_frames=2)

        # Giai đoạn 1: Bật nhảy mở tay & chân (2 khung hình ổn định)
        self._send_frame(counter, arms_up=True, ankle_dist=160.0)
        res_open = self._send_frame(counter, arms_up=True, ankle_dist=165.0)
        assert res_open["state"] == "OPEN"
        assert res_open["reps"] == 0
        assert res_open["valid"] is True
        assert res_open["leg_ratio"] == 1.65

        # Giai đoạn 2: Nhảy khép tay & chân về vị trí ban đầu (2 khung hình ổn định)
        res_closing = self._send_frame(counter, arms_up=False, ankle_dist=100.0)
        assert res_closing["state"] == "OPEN"  # Mới 1 khung khép nên chưa cộng rep
        assert res_closing["reps"] == 0

        res_done = self._send_frame(counter, arms_up=False, ankle_dist=95.0)
        assert res_done["state"] == "CLOSED"
        assert res_done["reps"] == 1
        assert res_done["exercise"] == "Jumping Jack"
        assert res_done["arms_up"] is False
        assert res_done["leg_ratio"] == 0.95

    def test_multiple_reps_sequence(self):
        """Thực hiện liên tiếp 3 lần Jumping Jack hoàn chỉnh."""
        counter = JumpingJackCounter(stable_frames=2)

        for _ in range(3):
            # 2 khung mở
            self._send_frame(counter, arms_up=True, ankle_dist=170.0)
            self._send_frame(counter, arms_up=True, ankle_dist=170.0)
            # 2 khung khép
            self._send_frame(counter, arms_up=False, ankle_dist=100.0)
            res = self._send_frame(counter, arms_up=False, ankle_dist=100.0)

        assert res["reps"] == 3
        assert res["state"] == "CLOSED"

    def test_boundary_thresholds_open_and_closed(self):
        """Kiểm tra chính xác tại giá trị biên open_leg_ratio=1.5 và closed_leg_ratio=1.15."""
        counter = JumpingJackCounter(open_leg_ratio=1.5, closed_leg_ratio=1.15, stable_frames=1)

        # Biên dưới của OPEN: leg_ratio == 1.5 (>= 1.5) -> chuyển sang OPEN
        res_open = self._send_frame(counter, arms_up=True, ankle_dist=150.0, hip_dist=100.0)
        assert res_open["state"] == "OPEN"

        # Biên trên của CLOSED: leg_ratio == 1.15 (<= 1.15) -> quay về CLOSED và cộng 1 rep
        res_closed = self._send_frame(counter, arms_up=False, ankle_dist=115.0, hip_dist=100.0)
        assert res_closed["state"] == "CLOSED"
        assert res_closed["reps"] == 1