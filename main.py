"""
Entry point for Smurf Fitness.

Run from the project root:
    python main.py

The FastAPI app serves the existing web interface and connects it to the
webcam + MediaPipe exercise analyzers.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Generator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.workout_manager import WorkoutManager
from interface.interface.home import get_home_html
from interface.interface.summary import get_summary_html
from interface.interface.workout import get_workout_html


PROJECT_DIR = Path(__file__).resolve().parent
ASSET_DIR = PROJECT_DIR / "interface" / "gifmophong"

app = FastAPI(
    title="Smurf Fitness",
    description="Trợ lý tập luyện AI tại nhà",
    version="1.0.0",
)

# The GIF/PNG assets in this repository are stored in interface/gifmophong.
if ASSET_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(ASSET_DIR)), name="static")


class StartWorkoutRequest(BaseModel):
    exercise: str = "squat"


class WorkoutRuntime:
    """Owns camera resources and coordinates per-frame inference."""

    def __init__(self) -> None:
        self.manager = WorkoutManager()
        self.camera = None
        self.detector = None
        self.worker: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.state_lock = threading.RLock()
        self.frame_lock = threading.Lock()
        self.latest_jpeg: Optional[bytes] = None
        self.runtime_error: Optional[str] = None

    def start(self, exercise: str) -> dict:
        with self.state_lock:
            current = self.manager.get_status()
            if current["status"] == "running":
                raise RuntimeError("Buổi tập đang chạy.")
            if current["status"] == "paused":
                raise RuntimeError("Buổi tập đang tạm dừng. Hãy tiếp tục hoặc kết thúc.")

            self._release_camera_resources()
            self.runtime_error = None
            self.latest_jpeg = None

            # Import camera dependencies only when the user starts a workout.
            # This lets the web server show the home page even before camera
            # packages have been installed.
            try:
                from camera.camera import Camera
                from camera.pose_detection import PoseDetector

                self.camera = Camera(camera_id=0, width=640, height=480)
                if not self.camera.start():
                    self.camera = None
                    raise RuntimeError(
                        "Không mở được webcam. Hãy kiểm tra camera hoặc quyền truy cập."
                    )

                self.detector = PoseDetector(complexity=0)
                session = self.manager.start(exercise)
            except Exception:
                self._release_camera_resources()
                raise

            self.stop_event.clear()
            self.worker = threading.Thread(
                target=self._process_frames,
                name="smurf-fitness-camera",
                daemon=True,
            )
            self.worker.start()
            return session

    def _process_frames(self) -> None:
        import cv2

        try:
            while not self.stop_event.is_set():
                frame = self.camera.get_frame() if self.camera else None
                if frame is None:
                    time.sleep(0.01)
                    continue

                frame = cv2.flip(frame, 1)
                frame = self.detector.find_pose(frame, draw=True)
                landmarks = self.detector.get_position(frame)

                with self.state_lock:
                    status = self.manager.get_status()
                    if status["status"] == "running":
                        status = self.manager.update(landmarks)

                self._draw_hud(frame, status, cv2)
                success, encoded = cv2.imencode(
                    ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 82]
                )
                if success:
                    with self.frame_lock:
                        self.latest_jpeg = encoded.tobytes()

        except Exception as exc:
            with self.state_lock:
                self.runtime_error = f"Lỗi xử lý camera: {exc}"
                if self.manager.get_status()["status"] == "running":
                    self.manager.pause()
        finally:
            # The API thread performs resource cleanup after joining this
            # worker, avoiding release/read races on the VideoCapture object.
            pass

    @staticmethod
    def _draw_hud(frame, status: dict, cv2) -> None:
        exercise = status.get("exercise") or "Workout"
        reps = status.get("reps", 0)
        duration = status.get("duration", "00:00")
        feedback = status.get("feedback") or ""
        state = status.get("status", "idle")

        cv2.rectangle(frame, (8, 8), (frame.shape[1] - 8, 112), (10, 10, 10), -1)
        cv2.putText(
            frame, f"{exercise.upper()}  |  {state.upper()}",
            (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 220, 255), 2
        )
        cv2.putText(
            frame, f"REPS: {reps}     TIME: {duration}",
            (20, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2
        )
        cv2.putText(
            frame, feedback[:72],
            (20, 91), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (80, 230, 150), 1
        )

    def pause(self) -> dict:
        with self.state_lock:
            return self.manager.pause()

    def resume(self) -> dict:
        with self.state_lock:
            return self.manager.resume()

    def finish(self) -> dict:
        with self.state_lock:
            summary = self.manager.finish()
        self.stop_event.set()
        worker = self.worker
        if worker and worker.is_alive() and worker is not threading.current_thread():
            worker.join(timeout=4.0)
        with self.state_lock:
            self._release_camera_resources()
        return summary

    def status(self) -> dict:
        with self.state_lock:
            result = self.manager.get_status()
            result["camera_error"] = self.runtime_error
            result["camera_ready"] = self.camera is not None
            return result

    def _release_camera_resources(self) -> None:
        if self.detector is not None:
            try:
                self.detector.close()
            except Exception:
                pass
            self.detector = None
        if self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                pass
            self.camera = None
        self.worker = None

    def mjpeg_stream(self) -> Generator[bytes, None, None]:
        boundary = b"--frame\r\n"
        while True:
            with self.frame_lock:
                frame = self.latest_jpeg
            if frame is not None:
                yield boundary + b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            else:
                time.sleep(0.05)
            if self.stop_event.is_set():
                break

    def shutdown(self) -> None:
        self.stop_event.set()
        worker = self.worker
        if worker and worker.is_alive() and worker is not threading.current_thread():
            worker.join(timeout=3.0)
        self._release_camera_resources()


runtime = WorkoutRuntime()


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(get_home_html())


@app.get("/workout", response_class=HTMLResponse)
def workout() -> HTMLResponse:
    html = get_workout_html()

    # The exported HTML originally used a timer-only simulation. Disable that
    # script and bind the existing controls to the real Python workout API.
    html = html.replace(
        '<script data-purpose="workout-timer-simulation">',
        '<script type="text/plain" data-purpose="workout-timer-simulation">',
        1,
    )
    integration_script = r"""
<script data-purpose="python-workout-integration">
(() => {
  const $ = (id) => document.getElementById(id);
  const startButton = $('start-workout-button');
  const pauseButton = document.querySelector('[aria-label="Tạm dừng buổi tập"]');
  const finishLink = document.querySelector('[aria-label="Kết thúc buổi tập"]');
  const repsNode = $('workout-reps');
  const feedbackNode = $('exercise-feedback');
  const timerNode = document.querySelector('[data-purpose="workout-timer"] .font-mono');
  const posePanel = document.querySelector('[data-purpose="pose-skeleton-visualization"]');

  let currentStatus = 'idle';
  let polling = false;

  const format = (seconds) => {
    const n = Math.max(0, Number(seconds) || 0);
    return String(Math.floor(n / 60)).padStart(2, '0') + ':' +
           String(n % 60).padStart(2, '0');
  };

  if (posePanel) {
    posePanel.innerHTML =
      '<img id="live-camera-feed" alt="Camera tập luyện trực tiếp" ' +
      'style="width:min(100%,640px);height:100%;max-height:440px;object-fit:contain;' +
      'border-radius:16px;background:#050608;border:1px solid rgba(255,255,255,.12)" ' +
      'src="/video_feed">';
  }

  async function api(path, method='POST', body=null) {
    const options = {method, headers: {'Content-Type': 'application/json'}};
    if (body !== null) options.body = JSON.stringify(body);
    const response = await fetch(path, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Không thể kết nối máy chủ.');
    return data;
  }

  function showError(message) {
    if (feedbackNode) feedbackNode.textContent = message;
  }

  function render(data) {
    if (!data) return;
    currentStatus = data.status || currentStatus;
    if (repsNode) repsNode.textContent = String(data.reps ?? 0);
    if (timerNode) timerNode.textContent = data.duration || '00:00';
    if (feedbackNode && data.feedback) feedbackNode.textContent = data.feedback;
    const title = $('exercise-title');
    if (title && data.exercise) title.textContent = data.exercise.toUpperCase().replaceAll('_', ' ');
    if (startButton && pauseButton && finishLink) {
      if (currentStatus === 'running' || currentStatus === 'paused') {
        startButton.style.display = 'none';
        pauseButton.style.display = 'flex';
        finishLink.style.display = 'flex';
        const isPaused = currentStatus === 'paused';
        pauseButton.setAttribute('aria-label', isPaused ? 'Tiếp tục buổi tập' : 'Tạm dừng buổi tập');
        const label = pauseButton.querySelector('span');
        if (label) label.textContent = isPaused ? 'Tiếp tục' : 'Tạm dừng';
        const svg = pauseButton.querySelector('svg');
        if (svg) svg.innerHTML = isPaused
          ? '<path d="M8 5v14l11-7z"></path>'
          : '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"></path>';
      }
    }
    if (data.camera_error) showError(data.camera_error);
  }

  async function poll() {
    if (polling) return;
    polling = true;
    try {
      const data = await api('/api/status', 'GET');
      render(data);
    } catch (_) {
      // The page can still display its guide if the API is temporarily offline.
    } finally {
      polling = false;
    }
  }

  if (startButton) {
    startButton.addEventListener('click', async (event) => {
      event.preventDefault();
      startButton.disabled = true;
      try {
        const exercise = sessionStorage.getItem('smurfExercise') || 'squat';
        const data = await api('/api/workout/start', 'POST', {exercise});
        render(data);
        const feed = $('live-camera-feed');
        if (feed) feed.src = '/video_feed?start=' + Date.now();
      } catch (error) {
        showError(error.message);
        alert(error.message);
      } finally {
        startButton.disabled = false;
      }
    });
  }

  if (pauseButton) {
    pauseButton.addEventListener('click', async (event) => {
      event.preventDefault();
      try {
        const action = currentStatus === 'paused' ? 'resume' : 'pause';
        render(await api('/api/workout/' + action));
      } catch (error) {
        showError(error.message);
      }
    });
  }

  // Capture before the template's original anchor handler so the final
  // summary is saved by Python rather than by the old mock counter.
  document.addEventListener('click', async (event) => {
    const link = event.target.closest && event.target.closest('[aria-label="Kết thúc buổi tập"]');
    if (!link) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    try {
      const result = await api('/api/workout/finish');
      const summary = {
        exercise: result.exercise,
        durationSeconds: result.duration_seconds,
        duration: result.duration,
        reps: result.reps
      };
      sessionStorage.setItem('smurfLastWorkout', JSON.stringify(summary));
      window.location.assign('/summary');
    } catch (error) {
      showError(error.message);
      alert(error.message);
    }
  }, true);

  window.setInterval(poll, 350);
  poll();
})();
</script>
"""
    return HTMLResponse(html.replace("</body>", integration_script + "\n</body>"))


@app.get("/summary", response_class=HTMLResponse)
def summary() -> HTMLResponse:
    return HTMLResponse(get_summary_html())


@app.get("/api/status")
def get_status() -> dict:
    return runtime.status()


@app.post("/api/workout/start")
def start_workout(request: StartWorkoutRequest) -> dict:
    try:
        return runtime.start(request.exercise)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/workout/pause")
def pause_workout() -> dict:
    try:
        return runtime.pause()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/workout/resume")
def resume_workout() -> dict:
    try:
        return runtime.resume()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/workout/finish")
def finish_workout() -> dict:
    try:
        return runtime.finish()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/video_feed")
def video_feed() -> StreamingResponse:
    return StreamingResponse(
        runtime.mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "Smurf Fitness"}


@app.on_event("shutdown")
def on_shutdown() -> None:
    runtime.shutdown()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
