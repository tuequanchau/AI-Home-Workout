"""Pose-based counters for the additional exercises in the web interface.

Landmarks use the MediaPipe Pose indices and pixel coordinates supplied by
PoseDetector.get_position(). Counters require several stable frames before
changing state to reduce duplicate counts from noisy camera detections.
"""
from __future__ import annotations

from analysis.angle_calculation import get_joint_angle
from analysis.landmark_utils import get_point_2d


def _avg(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def _pair_angle(lm, a, b, c):
    return _avg((get_joint_angle(lm, a[0], b[0], c[0]),
                 get_joint_angle(lm, a[1], b[1], c[1])))


class _CycleCounter:
    label = "bài tập"

    def __init__(self):
        self.reps = 0
        self.state = "READY"
        self._stable = 0

    def _result(self, feedback, valid=True):
        return {"reps": self.reps, "state": self.state,
                "feedback": feedback, "valid": valid}

    def _cycle(self, active, valid, ready_text, active_text, missing_text,
               active_state="ACTIVE", ready_state="READY"):
        if not valid:
            self._stable = 0
            return self._result(missing_text, False)
        self._stable = self._stable + 1 if active else 0
        if self.state == ready_state and self._stable >= 2:
            self.state, self._stable = active_state, 0
        elif self.state == active_state and not active:
            self.reps += 1
            self.state, self._stable = ready_state, 0
        return self._result(active_text if self.state == active_state else ready_text)


class PushUpCounter(_CycleCounter):
    label = "Push up"

    def __init__(self):
        super().__init__()
        self.state = "TOP"

    def update(self, lm):
        elbows = _pair_angle(lm, (11, 12), (13, 14), (15, 16))
        body = _pair_angle(lm, (11, 12), (23, 24), (27, 28))
        if elbows is None or body is None:
            return self._result("Xoay người sang bên và đưa vai, hông, cổ chân vào khung hình.", False)
        if body < 150:
            return self._result("Giữ thân người thẳng từ đầu đến gót chân.")
        if self.state == "TOP" and elbows < 100:
            self.state = "DOWN"
        elif self.state == "DOWN" and elbows > 150:
            self.reps += 1
            self.state = "TOP"
        return self._result("Đẩy người lên, duỗi tay để hoàn thành lần tập." if self.state == "DOWN"
                            else "Tư thế tốt. Hạ người bằng cách gập khuỷu tay.")


class LegRaiseCounter(_CycleCounter):
    label = "Leg raise"

    def __init__(self):
        super().__init__()
        self.state = "LOW"

    def update(self, lm):
        shoulder = get_point_2d(lm, 11) or get_point_2d(lm, 12)
        hip = get_point_2d(lm, 23) or get_point_2d(lm, 24)
        knees = [get_point_2d(lm, i) for i in (25, 26)]
        ankles = [get_point_2d(lm, i) for i in (27, 28)]
        pairs = [(k, a) for k, a in zip(knees, ankles) if k and a]
        if not shoulder or not hip or not pairs:
            return self._result("Nằm nghiêng với vai, hông và mắt cá chân hướng về camera.", False)
        torso = max(abs(hip[1] - shoulder[1]), 1.0)
        straight = any(get_joint_angle(lm, hi, ki, ai) and get_joint_angle(lm, hi, ki, ai) > 135
                       for hi, ki, ai in ((23, 25, 27), (24, 26, 28)))
        raised = any(a[1] < hip[1] - 0.15 * torso for _, a in pairs)
        lowered = any(a[1] > hip[1] - 0.05 * torso for _, a in pairs)
        if not straight:
            return self._result("Giữ chân duỗi thẳng trong khi nâng và hạ.")
        if self.state == "LOW" and raised:
            self.state = "RAISED"
        elif self.state == "RAISED" and lowered:
            self.reps += 1
            self.state = "LOW"
        return self._result("Từ từ hạ chân về gần sàn." if self.state == "RAISED"
                            else "Siết bụng và nâng chân lên có kiểm soát.")


class StandSideLegRaisesCounter(_CycleCounter):
    label = "Stand Side Leg Raises"

    def __init__(self):
        super().__init__()
        self.state = "CENTER"

    def update(self, lm):
        hips = [get_point_2d(lm, i) for i in (23, 24)]
        ankles = [get_point_2d(lm, i) for i in (27, 28)]
        shoulders = [get_point_2d(lm, i) for i in (11, 12)]
        if not all(hips) or not all(ankles) or not all(shoulders):
            return self._result("Đứng đối diện camera, để vai, hông và hai chân trong khung hình.", False)
        hip_x = sum(p[0] for p in hips) / 2
        shoulder_width = max(abs(shoulders[0][0] - shoulders[1][0]), 1.0)
        leg_out = any(abs(a[0] - hip_x) > 0.85 * shoulder_width for a in ankles)
        if self.state == "CENTER" and leg_out:
            self.state = "OUT"
        elif self.state == "OUT" and not leg_out:
            self.reps += 1
            self.state = "CENTER"
        return self._result("Hạ chân về giữa một cách có kiểm soát." if self.state == "OUT"
                            else "Nâng một chân sang ngang, giữ thân người ổn định.")


class SingleLegRomanianDeadliftCounter(_CycleCounter):
    label = "Single-Leg Romanian Deadlift"

    def __init__(self):
        super().__init__()
        self.state = "UPRIGHT"

    def update(self, lm):
        # Use torso-to-thigh hinge angle; the knee angle is a secondary visibility check.
        hinge = _pair_angle(lm, (11, 12), (23, 24), (25, 26))
        knee = _avg([get_joint_angle(lm, 23, 25, 27), get_joint_angle(lm, 24, 26, 28)])
        if hinge is None or knee is None:
            return self._result("Xoay người sang bên để camera thấy vai, hông và chân trụ.", False)
        if knee < 125:
            return self._result("Giữ đầu gối chân trụ hơi chùng, không ngồi xổm.")
        if self.state == "UPRIGHT" and hinge < 135:
            self.state = "HINGE"
        elif self.state == "HINGE" and hinge > 155:
            self.reps += 1
            self.state = "UPRIGHT"
        return self._result("Siết mông và đưa thân người đứng thẳng." if self.state == "HINGE"
                            else "Đẩy hông ra sau, giữ lưng thẳng và duỗi chân kia ra sau.")


class SkaterSquatCounter(_CycleCounter):
    label = "Skater Squat"

    def __init__(self):
        super().__init__()
        self.state = "UPRIGHT"

    def update(self, lm):
        knee = _avg([get_joint_angle(lm, 23, 25, 27), get_joint_angle(lm, 24, 26, 28)])
        if knee is None:
            return self._result("Xoay người sang bên để camera thấy hông, gối và mắt cá chân.", False)
        if self.state == "UPRIGHT" and knee < 110:
            self.state = "LOW"
        elif self.state == "LOW" and knee > 150:
            self.reps += 1
            self.state = "UPRIGHT"
        return self._result("Đẩy qua gót chân trụ để đứng lên." if self.state == "LOW"
                            else "Đưa chân còn lại ra sau, hạ người có kiểm soát.")


class ReverseLungeCounter(_CycleCounter):
    label = "Reverse Lunge"

    def __init__(self):
        super().__init__()
        self.state = "UPRIGHT"

    def update(self, lm):
        knees = [get_joint_angle(lm, 23, 25, 27), get_joint_angle(lm, 24, 26, 28)]
        knees = [v for v in knees if v is not None]
        if not knees:
            return self._result("Xoay người sang bên để camera thấy đầy đủ hai chân.", False)
        bent = min(knees)
        if self.state == "UPRIGHT" and bent < 110:
            self.state = "LUNGE"
        elif self.state == "LUNGE" and bent > 150:
            self.reps += 1
            self.state = "UPRIGHT"
        return self._result("Đạp gót chân trước để trở về tư thế đứng." if self.state == "LUNGE"
                            else "Bước một chân ra sau, hạ thấp người có kiểm soát.")
