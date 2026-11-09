 giao-dien-ui-1
# Smurf Fitness

Ứng dụng web Python dùng FastAPI với ba màn hình HTML xuất từ Stitch.

## Chạy trên Windows

1. Cài Python 3.10 trở lên.
2. Mở Terminal trong thư mục `smurf_fitness`.
3. Chạy `py -m pip install -r requirements.txt`.
4. Chạy `py -m uvicorn main:app --reload`.
5. Mở `http://127.0.0.1:8000` trong trình duyệt.

Trang chủ → Bắt đầu ngay → Tập luyện → Kết thúc → Tổng kết → Về trang chủ.
Tailwind CSS và phông chữ của bản Stitch được tải từ CDN, vì vậy cần kết nối Internet để hiển thị giao diện giống bản mẫu.


HEAD
# AI Home Workout Assistant

## 1. Introduction
A desktop application that uses computer vision
to support home workouts through a webcam.

## 2. Main Features
- Real-time webcam capture
- Human pose estimation
- Joint angle calculation
- Squat repetition counting
- Jumping Jack repetition counting
- Basic posture feedback
- Workout summary

## 3. Technology Stack
- Python
- OpenCV
- MediaPipe
- NumPy
- CustomTkinter
- PyInstaller

## 4. Project Structure
- camera/: Camera and pose detection
- analysis/: Movement analysis
- interface/: User interface
- core/: Application management
- assets/: Images and models
- tests/: Automated tests
- docs/: Technical documentation

## 5. Installation
Install dependencies:

pip install -r requirements.txt

Run application:

python main.py

 4baf0b693d1dde64c96990ea6559b7224847bc6f
 main
