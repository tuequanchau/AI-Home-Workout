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
