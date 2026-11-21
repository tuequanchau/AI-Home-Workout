"""Điểm vào của web Smurf Fitness.

Chạy (từ thư mục gốc dự án, nơi có main.py):
    python -m uvicorn main:app --reload      # reload có thể làm webcam mở lại; nếu lỗi dùng lệnh dưới
    python main.py                           # không reload, ổn định hơn khi dùng webcam

Mở: http://127.0.0.1:8000        Kiểm tra nhanh: http://127.0.0.1:8000/api/health
Đổi camera: đặt biến môi trường CAMERA_ID=1 trước khi chạy.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.workout_manager import EXERCISES, WorkoutManager
from interface.interface.home import get_home_html
from interface.interface.summary import get_summary_html
from interface.interface.workout import get_workout_html

BASE_DIR = Path(__file__).resolve().parent
# Các trang gọi /static/Squats.gif, /static/muscle-squat.png... nên trỏ /static vào thư mục chứa ảnh
STATIC_DIR = BASE_DIR / "interface" / "gifmophong"

manager = WorkoutManager()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    manager.shutdown()          # nhả webcam khi tắt server


app = FastAPI(title="Smurf Fitness", description="Trợ lý tập luyện AI", lifespan=lifespan)

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ------------------------------------------------------------------
# JavaScript nối trang /workout với backend. Được chèn vào cuối trang,
# không cần sửa file interface/interface/workout.py.
# ------------------------------------------------------------------
WORKOUT_LIVE_JS = """
<script data-purpose="live-backend">
(() => {
  const exercise = sessionStorage.getItem('smurfExercise') || 'squat';
  const area = document.querySelector('[data-purpose="pose-skeleton-visualization"]');
  const repsEl = document.getElementById('workout-reps');
  const fbEl = document.getElementById('exercise-feedback');
  const fbTitle = document.getElementById('exercise-feedback-title');

  // Thay khung xương mô phỏng bằng video camera thật (có vẽ khung xương)
  if (area) {
    area.style.minHeight = '0';
    area.innerHTML = '<img id="live-feed" alt="Camera AI" src="/api/video_feed?t=' + Date.now() +
      '" style="width:100%;height:100%;object-fit:contain;border-radius:1rem">';
  }

  const post = (url, body) => fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : undefined
  }).catch(() => {});

  // Capture phase: chạy trước các handler cũ (handler cũ chuyển trang ngay khi bấm Kết thúc)
  document.addEventListener('click', (e) => {
    const el = e.target.closest('button, a');
    if (!el) return;
    const label = el.getAttribute('aria-label');
    if (el.id === 'start-workout-button') post('/api/session/start', {exercise});
    else if (label === 'Tạm dừng buổi tập') post('/api/session/pause');
    else if (label === 'Tiếp tục buổi tập') post('/api/session/resume');
    else if (label === 'Kết thúc buổi tập') navigator.sendBeacon('/api/session/stop');
  }, true);

  const show = (title, text) => {
    if (fbTitle) fbTitle.textContent = title;
    if (fbEl) fbEl.textContent = text;
  };

  const poll = async () => {
    try {
      const s = await (await fetch('/api/state', {cache: 'no-store'})).json();
      if (s.camera_error) { show('Lỗi camera', s.camera_error); return; }
      if (!s.session_active) return;
      if (repsEl) repsEl.textContent = s.reps;
      show(s.valid ? 'Hướng dẫn' : 'Chưa nhận diện được', s.feedback);
    } catch (_) { /* server chưa sẵn sàng, thử lại ở lần sau */ }
  };
  setInterval(poll, 300);
  poll();
})();
</script>
"""


# ============================== Trang web ==============================
@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(get_home_html())


@app.get("/workout", response_class=HTMLResponse)
def workout() -> HTMLResponse:
    html = get_workout_html()
    if "</body>" in html:
        html = html.replace("</body>", WORKOUT_LIVE_JS + "</body>", 1)
    else:
        html += WORKOUT_LIVE_JS
    return HTMLResponse(html)


@app.get("/summary", response_class=HTMLResponse)
def summary() -> HTMLResponse:
    return HTMLResponse(get_summary_html())


# ================================ API ================================
class StartRequest(BaseModel):
    exercise: str = "squat"


@app.get("/api/health")
def api_health():
    """Camera đang chạy không, bài nào dùng code của nhóm, bài nào dùng bộ đếm tạm (và lỗi import)."""
    return manager.get_health()


@app.get("/api/exercises")
def api_exercises():
    return EXERCISES


@app.get("/api/state")
@app.get("/api/status")
def api_state():
    return manager.get_status()


@app.post("/api/session/start")
def api_start(req: StartRequest):
    try:
        return manager.start_session(req.exercise)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/session/pause")
def api_pause():
    return manager.pause_session()


@app.post("/api/session/resume")
def api_resume():
    return manager.resume_session()


@app.post("/api/session/stop")
def api_stop():
    return manager.stop_session() or {}


@app.get("/api/summary")
def api_summary():
    return manager.get_last_summary() or {}


@app.get("/api/video_feed")
def api_video_feed():
    return StreamingResponse(
        manager.mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
