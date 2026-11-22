import cv2
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from interface.home import get_home_html
from interface.workout import get_workout_html
from interface.summary import get_summary_html
from camera.camera import Camera
from camera.pose_detection import PoseDetector
from core.workout_manager import WorkoutManager

app = FastAPI(title="Smurf Fitness", description="Trợ lý tập luyện AI")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

cam = Camera(camera_id=0, width=640, height=480)
detector = PoseDetector(complexity=0)
manager = WorkoutManager()


class StartWorkoutRequest(BaseModel):
    exercise: str = "squat"


def generate_frames():
    """Đọc webcam, vẽ khung xương MediaPipe, cập nhật bộ đếm và phát lên web."""
    cam.start()
    try:
        while True:
            frame = cam.get_frame()
            if frame is None:
                continue

            # 1. Lật ngang khung hình như soi gương
            frame = cv2.flip(frame, 1)

            # 2. Nhận diện tư thế và vẽ 33 điểm khớp + đường nối xương
            frame = detector.find_pose(frame, draw=True)

            # 3. Lấy tọa độ các điểm khớp và đẩy sang WorkoutManager nếu đang tập
            landmarks = detector.get_position(frame)
            if manager.status == "running":
                manager.update(landmarks)

            if not landmarks:
                cv2.putText(
                    frame,
                    "KHONG TIM THAY NGUOI!",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

            # 4. Mã hóa khung hình sang JPEG để phát lên trình duyệt
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
    finally:
        cam.release()


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/api/workout/status")
def workout_status():
    return manager.get_status()


@app.post("/api/workout/start")
def start_workout(payload: StartWorkoutRequest):
    try:
        manager.reset()
        return manager.start(payload.exercise)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/workout/pause")
def pause_workout():
    try:
        return manager.pause()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/workout/resume")
def resume_workout():
    try:
        return manager.resume()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/workout/finish")
def finish_workout():
    try:
        return manager.finish()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(get_home_html())


@app.get("/workout", response_class=HTMLResponse)
def workout() -> HTMLResponse:
    return HTMLResponse(get_workout_html())


@app.get("/summary", response_class=HTMLResponse)
def summary() -> HTMLResponse:
    return HTMLResponse(get_summary_html())