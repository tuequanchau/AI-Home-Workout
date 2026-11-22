"""
Workout session manager for Smurf Fitness.

This class manages the lifecycle and summary of a workout session.
It deliberately does not access the webcam or process image frames.
"""
from __future__ import annotations

import time
from typing import Any, Optional


class WorkoutManager:
    """Manage exercise selection, reps, elapsed time and session state."""

    SUPPORTED_EXERCISES = {
        "squat": "Squat",
        "jumping_jack": "Jumping Jack",
    }

    def __init__(self) -> None:
        self.exercise: Optional[str] = None
        self.display_name: Optional[str] = None
        self.analyzer: Any = None

        self.status = "idle"  # idle | running | paused | finished
        self.reps = 0
        self._started_at: Optional[float] = None
        self._elapsed_before_pause = 0.0

        self.last_result: Optional[dict] = None
        self.feedback = "Chọn bài tập để bắt đầu."
        self.valid = False
        self.state: Optional[str] = None

    @staticmethod
    def _normalize_exercise(exercise: str) -> str:
        value = (exercise or "").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "jumpingjack": "jumping_jack",
            "jumping_jacks": "jumping_jack",
        }
        return aliases.get(value, value)

    def _create_analyzer(self, exercise: str):
        # Imports are local so importing the web app does not initialize
        # MediaPipe or the webcam.
        if exercise == "squat":
            from analysis.squat import SquatCounter
            return SquatCounter()
        if exercise == "jumping_jack":
            from analysis.jumping_jack import JumpingJackCounter
            return JumpingJackCounter()

        supported = ", ".join(self.SUPPORTED_EXERCISES.values())
        raise ValueError(
            f"Bài tập '{exercise}' chưa có bộ phân tích. "
            f"Hiện tại chỉ hỗ trợ: {supported}."
        )

    def start(self, exercise: str) -> dict:
        if self.status in {"running", "paused"}:
            raise RuntimeError("Đang có một buổi tập chưa kết thúc.")

        normalized = self._normalize_exercise(exercise)
        analyzer = self._create_analyzer(normalized)

        self.exercise = normalized
        self.display_name = self.SUPPORTED_EXERCISES[normalized]
        self.analyzer = analyzer
        self.analyzer.reset()

        self.status = "running"
        self.reps = 0
        self._started_at = time.monotonic()
        self._elapsed_before_pause = 0.0
        self.last_result = None
        self.feedback = "Đang khởi tạo nhận diện. Hãy đứng trọn người trước camera."
        self.valid = False
        self.state = getattr(self.analyzer, "state", None)
        return self.get_status()

    def pause(self) -> dict:
        if self.status != "running":
            raise RuntimeError("Chỉ có thể tạm dừng khi buổi tập đang chạy.")
        now = time.monotonic()
        if self._started_at is not None:
            self._elapsed_before_pause += now - self._started_at
        self._started_at = None
        self.status = "paused"
        self.feedback = "Buổi tập đang tạm dừng."
        return self.get_status()

    def resume(self) -> dict:
        if self.status != "paused":
            raise RuntimeError("Không có buổi tập nào đang tạm dừng.")
        self._started_at = time.monotonic()
        self.status = "running"
        self.feedback = "Tiếp tục tập luyện."
        return self.get_status()

    def finish(self) -> dict:
        if self.status not in {"running", "paused"}:
            raise RuntimeError("Không có buổi tập đang hoạt động để kết thúc.")
        if self.status == "running" and self._started_at is not None:
            self._elapsed_before_pause += time.monotonic() - self._started_at
        self._started_at = None
        self.status = "finished"
        self.feedback = "Buổi tập đã kết thúc."
        return self.get_status()

    def update(self, landmarks) -> dict:
        """Pass one frame's landmarks to the selected exercise analyzer."""
        if self.status != "running" or self.analyzer is None:
            return self.get_status()

        result = self.analyzer.update(landmarks)
        self.last_result = result
        self.reps = int(result.get("reps", self.reps) or 0)
        self.feedback = result.get("feedback") or "Tiếp tục thực hiện động tác."
        self.valid = bool(result.get("valid", False))
        self.state = result.get("state")
        return self.get_status()

    def _elapsed_seconds(self) -> int:
        elapsed = self._elapsed_before_pause
        if self.status == "running" and self._started_at is not None:
            elapsed += time.monotonic() - self._started_at
        return max(0, int(elapsed))

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes, remaining = divmod(max(0, int(seconds)), 60)
        return f"{minutes:02d}:{remaining:02d}"

    def get_status(self) -> dict:
        seconds = self._elapsed_seconds()
        result = {
            "exercise": self.exercise,
            "exercise_name": self.display_name,
            "status": self.status,
            "reps": self.reps,
            "duration_seconds": seconds,
            "duration": self._format_duration(seconds),
            "state": self.state,
            "feedback": self.feedback,
            "valid": self.valid,
            "last_result": self.last_result,
        }
        return result

    def reset(self) -> dict:
        """Reset the manager to an idle state without touching camera resources."""
        self.exercise = None
        self.display_name = None
        self.analyzer = None
        self.status = "idle"
        self.reps = 0
        self._started_at = None
        self._elapsed_before_pause = 0.0
        self.last_result = None
        self.feedback = "Chọn bài tập để bắt đầu."
        self.valid = False
        self.state = None
        return self.get_status()