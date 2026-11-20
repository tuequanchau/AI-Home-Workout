import os
import sys
import pytest

# Đảm bảo pytest luôn nhận diện đúng thư mục gốc AI-Home-Workout khi import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analysis.feedback import (
    get_squat_feedback,
    get_jumping_jack_feedback,
    get_general_feedback,
)


# =====================================================================
# 1. KIỂM THỬ HÀM get_squat_feedback(angle, state)
# =====================================================================
class TestSquatFeedback:
    def test_angle_is_none(self):
        """Trả về thông báo lỗi khi không đo được góc đầu gối."""
        assert get_squat_feedback(None, "STANDING") == "Không nhận diện được góc đầu gối."
        assert get_squat_feedback(None, "BOTTOM") == "Không nhận diện được góc đầu gối."

    def test_standing_state(self):
        """Trạng thái đứng thẳng chuẩn bị."""
        assert (
            get_squat_feedback(170, "STANDING")
            == "Tư thế đứng ổn định. Tiếp tục thực hiện động tác."
        )

    @pytest.mark.parametrize(
        "angle, expected",
        [
            (150, "Hãy tiếp tục hạ thấp cơ thể."),  # angle > 120
            (120.1, "Hãy tiếp tục hạ thấp cơ thể."),  # Sát ngưỡng trên 120
            (120, "Đang hạ người tốt. Cố gắng giữ lưng ổn định."),  # Giá trị biên == 120
            (95, "Đang hạ người tốt. Cố gắng giữ lưng ổn định."),  # angle < 120
        ],
    )
    def test_descending_state(self, angle, expected):
        """Trạng thái hạ người: kiểm tra ngưỡng góc đầu gối 120 độ."""
        assert get_squat_feedback(angle, "DESCENDING") == expected

    def test_bottom_state(self):
        """Trạng thái ở điểm thấp nhất của động tác Squat."""
        assert (
            get_squat_feedback(85, "BOTTOM")
            == "Đã đạt vị trí Squat. Bây giờ hãy đứng lên."
        )

    def test_ascending_state(self):
        """Trạng thái đứng lên hoàn thành nhịp."""
        assert (
            get_squat_feedback(130, "ASCENDING")
            == "Đang đứng lên. Hãy duỗi chân để hoàn thành động tác."
        )

    def test_unknown_state_fallback(self):
        """Trạng thái không xác định trả về câu nhắc mặc định."""
        assert get_squat_feedback(100, "UNKNOWN") == "Tiếp tục thực hiện Squat."
        assert get_squat_feedback(100, "") == "Tiếp tục thực hiện Squat."


# =====================================================================
# 2. KIỂM THỬ HÀM get_jumping_jack_feedback(arms_up, leg_ratio, state, open_leg_ratio)
# =====================================================================
class TestJumpingJackFeedback:
    def test_leg_ratio_is_none(self):
        """Trả về thông báo lỗi khi không nhận diện được tỷ lệ chân."""
        assert (
            get_jumping_jack_feedback(True, None, "OPEN")
            == "Không nhận diện được vị trí chân."
        )
        assert (
            get_jumping_jack_feedback(False, None, "CLOSED")
            == "Không nhận diện được vị trí chân."
        )

    def test_closed_state_arms_still_up(self):
        """Trạng thái CLOSED nhưng tay vẫn giơ cao (ưu tiên kiểm tra tay trước chân)."""
        assert (
            get_jumping_jack_feedback(arms_up=True, leg_ratio=1.0, state="CLOSED")
            == "Hãy khép chân và đưa hai tay xuống."
        )
        assert (
            get_jumping_jack_feedback(arms_up=True, leg_ratio=1.4, state="CLOSED")
            == "Hãy khép chân và đưa hai tay xuống."
        )

    @pytest.mark.parametrize(
        "leg_ratio, expected",
        [
            (1.3, "Hãy khép hai chân lại."),  # leg_ratio > 1.15
            (1.16, "Hãy khép hai chân lại."),  # Sát ngưỡng trên 1.15
            (1.15, "Tư thế sẵn sàng. Hãy bật nhảy mở tay và chân."),  # Biên == 1.15
            (0.9, "Tư thế sẵn sàng. Hãy bật nhảy mở tay và chân."),  # leg_ratio < 1.15
        ],
    )
    def test_closed_state_leg_thresholds(self, leg_ratio, expected):
        """Trạng thái CLOSED khi tay đã hạ: kiểm tra ngưỡng khép chân 1.15."""
        assert (
            get_jumping_jack_feedback(arms_up=False, leg_ratio=leg_ratio, state="CLOSED")
            == expected
        )

    def test_open_state_arms_not_up(self):
        """Trạng thái OPEN nhưng chưa giơ tay cao hơn vai (ưu tiên kiểm tra tay trước)."""
        assert (
            get_jumping_jack_feedback(arms_up=False, leg_ratio=1.8, state="OPEN")
            == "Hãy giơ hai tay cao hơn vai."
        )
        assert (
            get_jumping_jack_feedback(arms_up=False, leg_ratio=1.2, state="OPEN")
            == "Hãy giơ hai tay cao hơn vai."
        )

    @pytest.mark.parametrize(
        "leg_ratio, open_leg_ratio, expected",
        [
            (1.2, 1.5, "Hãy mở rộng hai chân hơn."),  # Nhỏ hơn mặc định 1.5
            (1.49, 1.5, "Hãy mở rộng hai chân hơn."),  # Sát ngưỡng dưới 1.5
            (1.5, 1.5, "Tư thế mở tốt. Hãy khép tay và chân lại."),  # Biên == 1.5
            (1.8, 1.5, "Tư thế mở tốt. Hãy khép tay và chân lại."),  # Lớn hơn 1.5
            (1.35, 1.3, "Tư thế mở tốt. Hãy khép tay và chân lại."),  # Tùy chỉnh ngưỡng
        ],
    )
    def test_open_state_leg_thresholds(self, leg_ratio, open_leg_ratio, expected):
        """Trạng thái OPEN khi tay đã giơ cao: kiểm tra ngưỡng mở chân."""
        assert (
            get_jumping_jack_feedback(
                arms_up=True,
                leg_ratio=leg_ratio,
                state="OPEN",
                open_leg_ratio=open_leg_ratio,
            )
            == expected
        )

    def test_unknown_state_fallback(self):
        """Trạng thái lạ trả về câu nhắc mặc định."""
        assert (
            get_jumping_jack_feedback(arms_up=True, leg_ratio=1.5, state="JUMPING")
            == "Tiếp tục thực hiện Jumping Jack."
        )


# =====================================================================
# 3. KIỂM THỬ HÀM get_general_feedback(valid)
# =====================================================================
class TestGeneralFeedback:
    def test_invalid_body_detection(self):
        """Khi camera chưa nhận diện rõ toàn thân (valid = False)."""
        assert (
            get_general_feedback(False)
            == "Vui lòng đứng ở vị trí camera có thể nhận diện rõ cơ thể."
        )

    def test_valid_body_detection(self):
        """Khi camera nhận diện tư thế hợp lệ (valid = True)."""
        assert get_general_feedback(True) == "Đang theo dõi chuyển động."