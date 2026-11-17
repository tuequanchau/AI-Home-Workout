
from .angle_calculation import get_joint_angle
from .landmark_utils import get_point_2d
from .feedback import get_squat_feedback


class SquatCounter:
    """
    Nhận diện và đếm số lần Squat.

    Các trạng thái:
    STANDING  : Đứng thẳng.
    DESCENDING: Đang hạ người.
    BOTTOM    : Đã xuống vị trí Squat.
    ASCENDING : Đang đứng lên.
    """

    def __init__(
        self,
        min_visibility=0.5,
        standing_angle=155,
        bottom_angle=100,
        descent_angle=120
    ):
        self.min_visibility = min_visibility

        # Các ngưỡng ban đầu, cần hiệu chỉnh khi thử nghiệm
        self.standing_angle = standing_angle
        self.bottom_angle = bottom_angle
        self.descent_angle = descent_angle

        self.state = "STANDING"
        self.reps = 0

        self.last_angle = None
        self.last_feedback = "Đứng thẳng để bắt đầu tập."

    def reset(self):
        """Đưa bộ đếm về trạng thái ban đầu."""

        self.state = "STANDING"
        self.reps = 0
        self.last_angle = None
        self.last_feedback = "Đứng thẳng để bắt đầu tập."

    def get_knee_angles(self, landmarks):
        """
        Tính góc hai đầu gối:
        Hông - Đầu gối - Mắt cá chân.
        """

        left_angle = get_joint_angle(
            landmarks,
            23, 25, 27,
            self.min_visibility
        )

        right_angle = get_joint_angle(
            landmarks,
            24, 26, 28,
            self.min_visibility
        )

        valid_angles = [
            angle for angle in [left_angle, right_angle]
            if angle is not None
        ]

        if not valid_angles:
            return None, left_angle, right_angle

        average_angle = sum(valid_angles) / len(valid_angles)

        return average_angle, left_angle, right_angle

    def update(self, landmarks):
        """
        Cập nhật trạng thái Squat theo từng khung hình.

        Trả về dictionary gồm:
        reps, state, angle, feedback, valid.
        """

        average_angle, left_angle, right_angle = (
            self.get_knee_angles(landmarks)
        )

        if average_angle is None:
            return {
                "exercise": "Squat",
                "reps": self.reps,
                "state": self.state,
                "angle": None,
                "left_angle": left_angle,
                "right_angle": right_angle,
                "feedback": "Không nhận diện được đầu gối. Hãy đứng rõ trước camera.",
                "valid": False
            }

        self.last_angle = average_angle

        # Giai đoạn 1: Đứng thẳng
        if self.state == "STANDING":

            if average_angle < self.descent_angle:
                self.state = "DESCENDING"

        # Giai đoạn 2: Hạ người
        elif self.state == "DESCENDING":

            if average_angle <= self.bottom_angle:
                self.state = "BOTTOM"

            elif average_angle >= self.standing_angle:
                # Người tập chưa xuống đủ sâu
                self.state = "STANDING"

        # Giai đoạn 3: Ở vị trí thấp
        elif self.state == "BOTTOM":

            if average_angle > self.bottom_angle + 5:
                self.state = "ASCENDING"

        # Giai đoạn 4: Đứng lên
        elif self.state == "ASCENDING":

            if average_angle >= self.standing_angle:
                self.reps += 1
                self.state = "STANDING"

            elif average_angle <= self.bottom_angle:
                self.state = "BOTTOM"

        feedback = get_squat_feedback(
            average_angle,
            self.state
        )

        self.last_feedback = feedback

        return {
            "exercise": "Squat",
            "reps": self.reps,
            "state": self.state,
            "angle": round(average_angle, 2),
            "left_angle": (
                round(left_angle, 2)
                if left_angle is not None else None
            ),
            "right_angle": (
                round(right_angle, 2)
                if right_angle is not None else None
            ),
            "feedback": feedback,
            "valid": True
        }
