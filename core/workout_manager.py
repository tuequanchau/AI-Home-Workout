"""Quản lý buổi tập cho web Smurf Fitness.

Luồng chạy (trên máy đang chạy uvicorn):

    webcam -> PoseDetector (33 điểm) -> bộ đếm của từng bài -> trạng thái (reps, feedback...)
                                     -> ảnh JPEG có khung xương -> /api/video_feed

- Camera chỉ mở khi có trang web đang xem (tự tắt sau IDLE_TIMEOUT giây không ai gọi API).
- Bộ đếm lấy từ package `analysis` của nhóm. Nếu import lỗi hoặc chưa có file
  (plank, high_knees) thì dùng bộ đếm TẠM bên dưới để web vẫn chạy; lỗi được ghi
  trong `manager.import_errors` và hiển thị ở GET /api/health.
- Đổi camera: đặt biến môi trường CAMERA_ID (mặc định 0).
"""
from __future__ import annotations

import importlib
import math
import os
import threading
import time
from typing import Any, Dict, Iterator, Optional, Tuple

# Mở webcam bằng MSMF trên Windows hay mất 5-30 giây vì khởi tạo phần cứng. Tắt đi để mở nhanh.
# Phải đặt TRƯỚC khi import cv2 (đổi lại bằng cách tự đặt biến này = 1 trước khi chạy).
os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

EXERCISES = {
    "squat": "Squat",
    "jumping_jack": "Jumping Jack",
    "plank": "Plank",
    "high_knees": "High Knees",
}

# (module, class) của nhóm Analyst. Làm xong bài nào thì tạo file analysis/<bai>.py
# với class có hàm update(landmarks) -> dict(reps, state, feedback, valid) là tự được dùng.
ANALYSIS_REGISTRY = {
    "squat": ("analysis.squat", "SquatCounter"),
    "jumping_jack": ("analysis.jumping_jack", "JumpingJackCounter"),
    "plank": ("analysis.plank", "PlankCounter"),
    "high_knees": ("analysis.high_knees", "HighKneesCounter"),
}

IDLE_TIMEOUT = 15.0       # giây không có trang web nào gọi API -> tắt camera (vào lại trong thời gian này là có ngay)
NO_FRAME_TIMEOUT = 3.0    # giây không đọc được khung hình -> báo lỗi camera
JPEG_QUALITY = 70


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


CAMERA_ID = _env_int("CAMERA_ID", 0)

_EXERCISE_ALIASES = {"squats": "squat", "jumpingjack": "jumping_jack", "jumping_jacks": "jumping_jack",
                     "highknees": "high_knees", "planks": "plank"}


def normalize_exercise(name: Optional[str]) -> Optional[str]:
    """'Jumping Jack' / 'jumping-jack' / 'JUMPING_JACK' -> 'jumping_jack'. Không hợp lệ -> None."""
    key = str(name or "").strip().lower().replace("-", "_").replace(" ", "_")
    key = _EXERCISE_ALIASES.get(key, key)
    return key if key in EXERCISES else None


# ====================== Bộ đếm TẠM (dùng khi analysis lỗi / chưa có) ======================
# Đầu vào: landmarks = list 33 dict {"x", "y" (pixel), "z", "visibility", ...} từ PoseDetector.

def _pt(lm, i: int, min_vis: float = 0.5):
    try:
        p = lm[i]
        if float(p.get("visibility", 1.0)) < min_vis:
            return None
        return float(p["x"]), float(p["y"])
    except (IndexError, KeyError, TypeError, AttributeError, ValueError):
        return None


def _angle(a, b, c) -> Optional[float]:
    if a is None or b is None or c is None:
        return None
    bax, bay = a[0] - b[0], a[1] - b[1]
    bcx, bcy = c[0] - b[0], c[1] - b[1]
    na, nc = math.hypot(bax, bay), math.hypot(bcx, bcy)
    if na == 0 or nc == 0:
        return None
    cos = max(-1.0, min(1.0, (bax * bcx + bay * bcy) / (na * nc)))
    return math.degrees(math.acos(cos))


def _avg_angle(lm, left: Tuple[int, int, int], right: Tuple[int, int, int]) -> Optional[float]:
    vals = [v for v in (_angle(*(_pt(lm, i) for i in left)),
                        _angle(*(_pt(lm, i) for i in right))) if v is not None]
    return sum(vals) / len(vals) if vals else None


def _dist(a, b) -> Optional[float]:
    if a is None or b is None:
        return None
    return math.hypot(a[0] - b[0], a[1] - b[1])


class _FallbackBase:
    def __init__(self):
        self.reps = 0
        self.state = "READY"

    def _out(self, feedback: str, valid: bool) -> Dict[str, Any]:
        return {"reps": self.reps, "state": self.state, "feedback": feedback, "valid": valid}


class _FallbackSquat(_FallbackBase):
    def __init__(self):
        super().__init__()
        self.state = "STANDING"

    def update(self, lm):
        ang = _avg_angle(lm, (23, 25, 27), (24, 26, 28))
        if ang is None:
            return self._out("Không nhận diện được đầu gối. Hãy đứng rõ trước camera.", False)
        if self.state == "STANDING" and ang <= 100:
            self.state = "BOTTOM"
        elif self.state == "BOTTOM" and ang >= 155:
            self.reps += 1
            self.state = "STANDING"
        if self.state == "BOTTOM":
            fb = "Đã xuống đủ sâu. Hãy đứng lên." if ang <= 110 else "Đang đứng lên, hãy duỗi thẳng chân."
        elif ang < 155:
            fb = "Hãy tiếp tục hạ thấp cơ thể."
        else:
            fb = "Tư thế đứng ổn định. Bắt đầu hạ người."
        return self._out(fb, True)


class _FallbackJumpingJack(_FallbackBase):
    def __init__(self):
        super().__init__()
        self.state = "CLOSED"
        self._open_frames = 0
        self._closed_frames = 0

    def update(self, lm):
        ls, rs, lw, rw = _pt(lm, 11), _pt(lm, 12), _pt(lm, 15), _pt(lm, 16)
        ankle, hip = _dist(_pt(lm, 27), _pt(lm, 28)), _dist(_pt(lm, 23), _pt(lm, 24))
        if None in (ls, rs, lw, rw) or not ankle or not hip:
            self._open_frames = self._closed_frames = 0
            return self._out("Không nhận diện rõ tay hoặc chân. Hãy đứng trọn người trước camera.", False)
        arms_up = lw[1] < ls[1] and rw[1] < rs[1]
        ratio = ankle / hip
        is_open = arms_up and ratio >= 1.5
        is_closed = (not arms_up) and ratio <= 1.15
        self._open_frames = self._open_frames + 1 if is_open else 0
        self._closed_frames = self._closed_frames + 1 if is_closed else 0
        if self.state == "CLOSED" and self._open_frames >= 2:
            self.state = "OPEN"
            self._closed_frames = 0
        elif self.state == "OPEN" and self._closed_frames >= 2:
            self.reps += 1
            self.state = "CLOSED"
            self._open_frames = 0
        if self.state == "CLOSED":
            fb = "Tư thế sẵn sàng. Hãy bật nhảy mở tay và chân." if not arms_up else "Hãy khép chân và đưa hai tay xuống."
        else:
            fb = "Tư thế mở tốt. Hãy khép tay và chân lại." if (arms_up and ratio >= 1.5) \
                else "Hãy giơ tay cao hơn vai và mở rộng chân."
        return self._out(fb, True)


class _FallbackPlank(_FallbackBase):
    """reps = số giây giữ đúng tư thế (UI hiển thị chung ở ô 'Số lần đúng')."""

    def __init__(self):
        super().__init__()
        self.state = "WAITING"
        self.hold = 0.0
        self._last = None

    def update(self, lm):
        now = time.monotonic()
        dt = 0.0 if self._last is None else min(now - self._last, 0.5)
        self._last = now
        ang = _avg_angle(lm, (11, 23, 27), (12, 24, 28))   # vai - hông - mắt cá chân
        if ang is None:
            self.state = "LOST"
            return self._out("Không nhận diện được thân người. Hãy xoay người sang một bên.", False)
        if 160 <= ang <= 185:
            self.hold += dt
            self.state = "HOLDING"
            self.reps = int(self.hold)
            return self._out(f"Giữ vững tư thế. Đã giữ {self.reps} giây.", True)
        self.state = "BAD_FORM"
        return self._out("Hãy giữ thân người thẳng từ vai đến gót chân (không võng hông, không nhô mông).", True)


class _FallbackHighKnees(_FallbackBase):
    def __init__(self):
        super().__init__()
        self.state = "DOWN"
        self._up = {"L": False, "R": False}
        self._last_side = None

    def update(self, lm):
        ls, rs, lh, rh = _pt(lm, 11), _pt(lm, 12), _pt(lm, 23), _pt(lm, 24)
        if None in (ls, rs, lh, rh):
            return self._out("Không nhận diện rõ thân người. Hãy đứng trọn người trước camera.", False)
        torso = abs((lh[1] + rh[1]) / 2 - (ls[1] + rs[1]) / 2)
        if torso < 1:
            return self._out("Không nhận diện rõ thân người.", False)
        seen = False
        for side, knee_id, hip in (("L", 25, lh), ("R", 26, rh)):
            knee = _pt(lm, knee_id)
            if knee is None:
                continue
            seen = True
            lifted = knee[1] <= hip[1] + 0.2 * torso          # gối nâng ngang hông
            if lifted and not self._up[side] and side != self._last_side:
                self.reps += 1                                # mỗi lần nâng gối, luân phiên trái/phải
                self._last_side = side
            self._up[side] = lifted
        if not seen:
            return self._out("Không nhận diện được đầu gối.", False)
        self.state = "UP" if any(self._up.values()) else "DOWN"
        return self._out("Nâng gối cao ngang hông, luân phiên hai chân." if self.state == "DOWN"
                         else "Tốt! Tiếp tục đổi chân.", True)


FALLBACKS = {
    "squat": _FallbackSquat,
    "jumping_jack": _FallbackJumpingJack,
    "plank": _FallbackPlank,
    "high_knees": _FallbackHighKnees,
}


def _normalize(raw: Any, previous: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Đưa kết quả của mọi bộ đếm về cùng một dạng."""
    if not isinstance(raw, dict):
        raw = {}
    prev_reps = previous["reps"] if previous else 0
    try:
        reps = int(raw.get("reps", prev_reps) or 0)
    except (TypeError, ValueError):
        reps = prev_reps
    return {
        "reps": reps,
        "state": str(raw.get("state", "")),
        "feedback": str(raw.get("feedback", "")),
        "valid": bool(raw.get("valid", True)),
    }


# ============================== Buổi tập và Manager ==============================

class _Session:
    def __init__(self, exercise: str, counter: Any, engine: str):
        self.exercise = exercise
        self.counter = counter
        self.engine = engine            # "analysis" (code của nhóm) | "fallback" (bộ đếm tạm)
        self.started = time.monotonic()
        self.paused = False
        self._paused_at: Optional[float] = None
        self._paused_total = 0.0
        self.result = {"reps": 0, "state": "READY",
                       "feedback": "Đứng vào khung hình để bắt đầu.", "valid": False}

    def elapsed(self) -> float:
        end = self._paused_at if self.paused and self._paused_at else time.monotonic()
        return max(0.0, end - self.started - self._paused_total)

    def pause(self):
        if not self.paused:
            self.paused, self._paused_at = True, time.monotonic()

    def resume(self):
        if self.paused:
            self._paused_total += time.monotonic() - (self._paused_at or time.monotonic())
            self.paused, self._paused_at = False, None


class WorkoutManager:
    def __init__(self, camera_id: int = CAMERA_ID, exercise: Optional[str] = "squat"):
        self.camera_id = camera_id
        self.exercise = normalize_exercise(exercise) or "squat"   # bài mặc định khi start() không truyền tên
        self.import_errors: Dict[str, str] = {}

        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._closing = False

        self._camera_status = "stopped"      # stopped | starting | running | error
        self._camera_error: Optional[str] = None
        self._jpeg: Optional[bytes] = None
        self._jpeg_seq = 0
        self._fps = 0.0
        self._person = False
        self._last_touch = time.monotonic()
        self._last_idx = -1

        self._detector = None                # PoseDetector dùng chung, nạp sẵn ở warmup()
        self._warm_thread: Optional[threading.Thread] = None
        self._warm_error: Optional[str] = None
        self._timings: Dict[str, float] = {}  # thời gian từng bước khởi động camera (xem /api/health)

        self._session: Optional[_Session] = None
        self._last_summary: Optional[Dict[str, Any]] = None

    # ----------------------------- camera -----------------------------
    def touch(self) -> None:
        """Đánh dấu có trang web đang dùng (giữ camera mở)."""
        self._last_touch = time.monotonic()

    def ensure_camera(self) -> None:
        with self._lock:
            if self._closing or (self._thread is not None and self._thread.is_alive()):
                return
            self._stop_evt.clear()
            self._camera_status, self._camera_error = "starting", None
            self.touch()
            self._thread = threading.Thread(target=self._camera_loop, name="camera-loop", daemon=True)
            self._thread.start()

    # ---- nạp trước thư viện + model để khi chọn bài chỉ còn việc mở webcam ----
    def warmup(self) -> None:
        """Nạp sẵn OpenCV, MediaPipe và model nhận diện ở luồng nền. Gọi 1 lần khi server khởi động."""
        with self._lock:
            if self._detector is not None or (self._warm_thread is not None and self._warm_thread.is_alive()):
                return
            self._warm_thread = threading.Thread(target=self._warm, name="warmup", daemon=True)
            self._warm_thread.start()

    def _warm(self) -> None:
        t0 = time.perf_counter()
        try:
            import cv2                                          # noqa: F401
            from camera.camera import Camera                    # noqa: F401
            from camera.pose_detection import PoseDetector
            self._detector = PoseDetector(complexity=0)
            self._timings["warmup_s"] = round(time.perf_counter() - t0, 2)
            self._warm_error = None
        except Exception as e:                                  # noqa: BLE001 - vòng camera sẽ báo lỗi cụ thể
            self._warm_error = f"{type(e).__name__}: {e}"

    def _get_detector(self):
        t = self._warm_thread
        if t is not None and t.is_alive():
            t.join()                                            # đang nạp nền -> đợi cho xong, không nạp hai lần
        if self._detector is None:
            from camera.pose_detection import PoseDetector
            self._detector = PoseDetector(complexity=0)
        return self._detector

    def _set_camera(self, status: str, error: Optional[str] = None) -> None:
        with self._lock:
            self._camera_status, self._camera_error = status, error

    @staticmethod
    def _grab(cam):
        """Khung mới của camera, hoặc None nếu chưa có.
        Ưu tiên get_new_frame() (không trả lại khung cũ); camera bản cũ chỉ có get_frame() thì dùng tạm."""
        getter = getattr(cam, "get_new_frame", None) or cam.get_frame
        return getter()

    def _camera_loop(self) -> None:
        cam = None
        idle = False
        t_begin = time.perf_counter()
        t_first = None
        tm: Dict[str, float] = {}
        try:
            import cv2                                   # import muộn: server vẫn lên được nếu thiếu thư viện
            from camera.camera import Camera
            tm["import_s"] = round(time.perf_counter() - t_begin, 2)

            cam = Camera(camera_id=self.camera_id)
            if not cam.start():                          # bước chậm nhất; warmup() đang chạy song song
                raise RuntimeError(
                    "Không mở được webcam. Đóng ứng dụng đang dùng camera (Zoom, Meet, trình duyệt) "
                    "hoặc đổi biến môi trường CAMERA_ID (0, 1, 2).")
            tm["camera_open_s"] = round(time.perf_counter() - t_begin, 2)

            detector = self._get_detector()              # đã nạp sẵn nên thường tức thì
            tm["detector_ready_s"] = round(time.perf_counter() - t_begin, 2)
            self._last_idx = -1
            self._set_camera("running")

            t_prev = time.perf_counter()
            last_frame = time.monotonic()
            while not self._stop_evt.is_set():
                if time.monotonic() - self._last_touch > IDLE_TIMEOUT:
                    idle = True
                    break
                frame = self._grab(cam)
                if frame is None:
                    if time.monotonic() - last_frame > NO_FRAME_TIMEOUT:
                        raise RuntimeError("Không đọc được hình ảnh từ webcam.")
                    time.sleep(0.005)
                    continue
                last_frame = time.monotonic()
                if t_first is None:                      # khung hình đầu tiên: ghi lại thời gian khởi động
                    tm["first_frame_s"] = round(time.perf_counter() - t_begin, 2)
                    self._timings.update(tm)
                    print("[camera] khởi động: " + " | ".join(f"{k}={v}" for k, v in tm.items()), flush=True)
                    t_first = tm["first_frame_s"]

                detector.find_pose(frame, draw=True)
                landmarks = detector.get_position(frame)
                self._feed(landmarks)

                frame = cv2.flip(frame, 1)               # lật gương chỉ để hiển thị
                ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                now = time.perf_counter()
                inst = 1.0 / max(now - t_prev, 1e-6)
                t_prev = now
                with self._lock:
                    self._fps = inst if self._fps == 0 else 0.9 * self._fps + 0.1 * inst
                    if ok:
                        self._jpeg, self._jpeg_seq = buf.tobytes(), self._jpeg_seq + 1
        except Exception as e:                           # noqa: BLE001 - báo lỗi lên giao diện
            self._set_camera("error", f"{type(e).__name__}: {e}")
        finally:
            for obj, fn in ((cam, "release"),):          # detector giữ lại cho lần mở camera sau
                try:
                    if obj is not None:
                        getattr(obj, fn)()
                except Exception:                        # noqa: BLE001
                    pass
            with self._lock:
                self._jpeg, self._fps, self._person = None, 0.0, False
                if self._camera_status != "error":
                    self._camera_status = "stopped"
                if idle:                                 # bỏ trang giữa chừng -> chốt buổi tập
                    self._finalize_session_locked()

    # --------------------------- bộ đếm / buổi tập ---------------------------
    def _make_counter(self, exercise: str):
        mod_name, cls_name = ANALYSIS_REGISTRY[exercise]
        try:
            counter = getattr(importlib.import_module(mod_name), cls_name)()
            self.import_errors.pop(exercise, None)
            return counter, "analysis"
        except ModuleNotFoundError as e:
            if e.name == mod_name:
                self.import_errors[exercise] = f"Chưa có {mod_name}.py (đang dùng bộ đếm tạm)"
            else:
                self.import_errors[exercise] = f"ModuleNotFoundError: {e}"
        except Exception as e:                           # noqa: BLE001 - SyntaxError, ImportError, ...
            self.import_errors[exercise] = f"{type(e).__name__}: {e}"
        return FALLBACKS[exercise](), "fallback"

    def _feed(self, landmarks) -> None:
        """Đưa landmarks của 1 khung vào bộ đếm của buổi tập đang chạy."""
        with self._lock:
            self._person = bool(landmarks)
            s = self._session
            if s is None or s.paused:
                return
            try:
                s.result = _normalize(s.counter.update(landmarks or []), s.result)
            except Exception as e:                       # noqa: BLE001 - lỗi bộ đếm không được làm sập camera
                s.result = {**s.result, "valid": False,
                            "feedback": f"Lỗi bộ đếm ({type(e).__name__}). Xem GET /api/health."}
                self.import_errors[s.exercise] = f"Runtime {type(e).__name__}: {e}"

    def start_session(self, exercise: Optional[str] = None) -> Dict[str, Any]:
        key = normalize_exercise(exercise if exercise is not None else self.exercise)
        if key is None:
            raise ValueError(f"Bài tập không hợp lệ: {exercise!r}. Hợp lệ: {', '.join(EXERCISES)}")
        exercise = self.exercise = key
        self.touch()
        self.ensure_camera()
        counter, engine = self._make_counter(exercise)
        with self._lock:
            if self._session is not None:
                self._finalize_session_locked()
            self._session = _Session(exercise, counter, engine)
        return self.get_state()

    def pause_session(self) -> Dict[str, Any]:
        with self._lock:
            if self._session:
                self._session.pause()
        return self.get_state()

    def resume_session(self) -> Dict[str, Any]:
        with self._lock:
            if self._session:
                self._session.resume()
        return self.get_state()

    def stop_session(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._finalize_session_locked()

    def _finalize_session_locked(self) -> Optional[Dict[str, Any]]:
        s = self._session
        if s is None:
            return self._last_summary
        seconds = int(s.elapsed())
        self._last_summary = {
            "exercise": s.exercise,
            "exercise_name": EXERCISES.get(s.exercise, s.exercise),
            "reps": s.result["reps"],
            "duration_seconds": seconds,
            "duration": f"{seconds // 60:02d}:{seconds % 60:02d}",
            "engine": s.engine,
            "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._session = None
        return self._last_summary

    # ------------------------------- đọc dữ liệu -------------------------------
    def get_status(self) -> Dict[str, Any]:
        """Trạng thái hiện tại (an toàn gọi liên tục, vd mỗi 300 ms). Luôn trả về dict đủ khoá.

        Một số khoá có tên thay thế để giao diện dùng tên nào cũng được:
          reps = rep_count = count | elapsed_seconds = elapsed = duration_seconds
          running = is_running (đang tập, không tạm dừng) | paused = is_paused
        """
        self.touch()
        with self._lock:
            s = self._session
            r = s.result if s else None
            active = s is not None
            paused = bool(s and s.paused)
            reps = r["reps"] if r else 0
            elapsed = round(s.elapsed(), 1) if s else 0.0
            return {
                # camera
                "camera": self._camera_status,
                "camera_error": self._camera_error,
                "fps": round(self._fps, 1),
                "person_detected": self._person,
                # buổi tập
                "session_active": active,
                "running": active and not paused,
                "is_running": active and not paused,
                "paused": paused,
                "is_paused": paused,
                "exercise": s.exercise if s else self.exercise,
                "exercise_name": EXERCISES.get(s.exercise if s else self.exercise),
                "engine": s.engine if s else None,
                # số liệu
                "reps": reps,
                "rep_count": reps,
                "count": reps,
                "elapsed_seconds": elapsed,
                "elapsed": elapsed,
                "duration_seconds": elapsed,
                # nhận xét
                "state": r["state"] if r else "IDLE",
                "feedback": r["feedback"] if r else "Chọn bài tập và bấm Bắt đầu.",
                "valid": r["valid"] if r else False,
            }

    def get_last_summary(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._last_summary

    def set_exercise(self, exercise: str) -> Dict[str, Any]:
        """Chọn bài tập. Đang tập thì chuyển sang bài mới (bắt đầu lại từ 0)."""
        key = normalize_exercise(exercise)
        if key is None:
            raise ValueError(f"Bài tập không hợp lệ: {exercise!r}. Hợp lệ: {', '.join(EXERCISES)}")
        self.exercise = key
        with self._lock:
            active = self._session is not None
        return self.start_session(key) if active else self.get_status()

    def reset_session(self) -> Dict[str, Any]:
        """Bỏ buổi tập hiện tại, KHÔNG lưu tổng kết."""
        with self._lock:
            self._session = None
        return self.get_status()

    # Tên thay thế (alias) cho cùng chức năng, để giao diện gọi tên nào cũng chạy
    get_state = get_status
    start = start_workout = start_session
    pause = pause_workout = pause_session
    resume = resume_workout = resume_session
    stop = stop_workout = stop_session
    reset = reset_session
    select_exercise = set_exercise
    get_summary = get_last_summary

    def get_health(self) -> Dict[str, Any]:
        """Bài nào đang dùng code của nhóm, bài nào dùng bộ đếm tạm (và vì sao)."""
        engines = {ex: self._make_counter(ex)[1] for ex in EXERCISES}
        with self._lock:
            return {
                "camera": self._camera_status,
                "camera_error": self._camera_error,
                "camera_id": self.camera_id,
                "engines": engines,
                "import_errors": dict(self.import_errors),
                "startup_timings": dict(self._timings),
                "warmup_error": self._warm_error,
            }

    def mjpeg_stream(self) -> Iterator[bytes]:
        """Luồng MJPEG cho thẻ <img src="/api/video_feed">."""
        self.ensure_camera()
        last_seq = -1
        while not self._closing:
            self.touch()
            with self._lock:
                seq, jpeg, status = self._jpeg_seq, self._jpeg, self._camera_status
            if status == "error":
                return
            if status == "stopped":
                self.ensure_camera()
            if jpeg is not None and seq != last_seq:
                last_seq = seq
                yield (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                       + str(len(jpeg)).encode() + b"\r\n\r\n" + jpeg + b"\r\n")
            else:
                time.sleep(0.02)

    def shutdown(self) -> None:
        self._closing = True
        self._stop_evt.set()
        t = self._thread
        if t is not None and t.is_alive():
            t.join(timeout=3.0)
        try:
            if self._detector is not None:
                self._detector.close()
        except Exception:                                # noqa: BLE001
            pass
