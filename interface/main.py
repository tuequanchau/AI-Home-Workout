import cv2
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from interface.home import get_home_html
from interface.workout import get_workout_html
from interface.summary import get_summary_html
from camera.camera import Camera
from camera.pose_detection import PoseDetector

app = FastAPI(title="Smurf Fitness", description="Trợ lý tập luyện AI")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

cam = Camera(camera_id=0, width=640, height=480)
detector = PoseDetector(complexity=0)


def generate_frames():
    """Đọc webcam, vẽ khung xương MediaPipe và truyền luồng JPEG lên web."""
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

            # 3. Lấy tọa độ các điểm khớp (dùng để kiểm tra có người trong khung hình không)
            landmarks = detector.get_position(frame)
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


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(get_home_html())


@app.get("/workout", response_class=HTMLResponse)
def workout() -> HTMLResponse:
    return HTMLResponse(get_workout_html())


@app.get("/summary", response_class=HTMLResponse)
def summary() -> HTMLResponse:
    return HTMLResponse(get_summary_html())