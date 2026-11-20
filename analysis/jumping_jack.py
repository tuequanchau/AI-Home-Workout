
from .angle_calculation import get_distance_between
from .landmark_utils import get_point_2d
from .feedback import get_jumping_jack_feedback


class JumpingJackCounter:
    """
    Nhận diện và đếm số lần Jumping Jack.

    Một lần tập hoàn chỉnh:
    CLOSED -> OPEN -> CLOSED
    """

    def __init__(
        self,
        min_visibility=0.5,
        open_leg_ratio=1.5,
        closed_leg_ratio=1.15,
        stable_frames=2
    ):
        self.min_visibility = min_visibility

        # Các ngưỡng ban đầu để thử nghiệm
        self.open_leg_ratio = open_leg_ratio
        self.closed_leg_ratio = closed_leg_ratio

        self.stable_frames = stable_frames

        self.state = "CLOSED"
        self.reps = 0

        self.open_frames = 0
        self.closed_frames = 0

        self.last_feedback = "Đứng khép chân, hai tay đặt dọc thân người."

    def reset(self):
        """Đặt lại bộ đếm."""

        self.state = "CLOSED"
        self.reps = 0

        self.open_frames = 0
        self.closed_frames = 0

        self.last_feedback = "Đứng khép chân để bắt đầu."

    def detect_arm_position(self, landmarks):
        """
        Kiểm tra hai tay đã giơ cao hơn vai hay chưa.
        Trong ảnh camera, tọa độ y nhỏ hơn tương ứng vị trí cao hơn.
        """

        left_shoulder = get_point_2d(
            landmarks, 11, self.min_visibility
        )

        right_shoulder = get_point_2d(
            landmarks, 12, self.min_visibility
        )

        left_wrist = get_point_2d(
            landmarks, 15, self.min_visibility
        )

        right_wrist = get_point_2d(
            landmarks, 16, self.min_visibility
        )

        if any(point is None for point in [
            left_shoulder,
            right_shoulder,
            left_wrist,
            right_wrist
        ]):
            return None

        left_arm_up = (
            left_wrist[1] < left_shoulder[1]
        )

        right_arm_up = (
            right_wrist[1] < right_shoulder[1]
        )

        return left_arm_up and right_arm_up

    def get_leg_ratio(self, landmarks):
        """
        Tỷ lệ khoảng cách hai mắt cá chân
        so với khoảng cách hai hông.
        """

        ankle_distance = get_distance_between(
            landmarks, 27, 28, self.min_visibility
        )

        hip_distance = get_distance_between(
            landmarks, 23, 24, self.min_visibility
        )

        if (
            ankle_distance is None
            or hip_distance is None
            or hip_distance == 0
        ):
            return None

        return ankle_distance / hip_distance

    def update(self, landmarks):
        """
        Cập nhật trạng thái và số lần Jumping Jack.
        """

        arms_up = self.detect_arm_position(landmarks)
        leg_ratio = self.get_leg_ratio(landmarks)

        if arms_up is None or leg_ratio is None:
            self.open_frames = 0
            self.closed_frames = 0

            return {
                "exercise": "Jumping Jack",
                "reps": self.reps,
                "state": self.state,
                "leg_ratio": leg_ratio,
                "feedback": "Không nhận diện rõ tay hoặc chân. Hãy đứng trọn người trước camera.",
                "valid": False
            }

        is_open = (
            arms_up
            and leg_ratio >= self.open_leg_ratio
        )

        is_closed = (
            not arms_up
            and leg_ratio <= self.closed_leg_ratio
        )

        # Đếm số khung hình ổn định
        if is_open:
            self.open_frames += 1
        else:
            self.open_frames = 0

        if is_closed:
            self.closed_frames += 1
        else:
            self.closed_frames = 0

        # Trạng thái khép: chờ mở tay và chân
        if self.state == "CLOSED":

            if self.open_frames >= self.stable_frames:
                self.state = "OPEN"
                self.closed_frames = 0

        # Trạng thái mở: chờ khép tay và chân
        elif self.state == "OPEN":

            if self.closed_frames >= self.stable_frames:
                self.reps += 1
                self.state = "CLOSED"
                self.open_frames = 0

        feedback = get_jumping_jack_feedback(
            arms_up,
            leg_ratio,
            self.state,
            self.open_leg_ratio
        )

        self.last_feedback = feedback

        return {
            "exercise": "Jumping Jack",
            "reps": self.reps,
            "state": self.state,
            "arms_up": arms_up,
            "leg_ratio": round(leg_ratio, 2),
            "feedback": feedback,
            "valid": True
        }
