# Smurf Fitness

Ứng dụng tập luyện chạy trên máy tính bằng Python và FastAPI. Làm theo hướng dẫn dưới đây để mở trang web trên Windows.

> **Lưu ý:** Cách chạy này mở website trên chính máy đang chạy ứng dụng. Đây chưa phải website công khai trên Internet; bạn bè không thể truy cập website chỉ bằng cách xem GitHub.

## A. Tải mã nguồn từ GitHub

1. Mở trang kho dự án trên GitHub.
2. Bấm nút **Code** màu xanh, chọn **Download ZIP**.
3. Mở thư mục **Downloads** trên máy tính, bấm chuột phải vào file ZIP vừa tải và chọn **Extract All...** (Giải nén tất cả).
4. Mở thư mục đã giải nén. Tìm thư mục dự án có các file `main.py`, `requirements.txt` và `README.md`.

## B. Cài Python (chỉ cần làm một lần)

1. Cài Python phiên bản **3.10 trở lên** từ [python.org](https://www.python.org/downloads/).
2. Khi cài trên Windows, đánh dấu **Add Python to PATH** nếu trình cài đặt có lựa chọn này.
3. Mở PowerShell và nhập lệnh sau để kiểm tra:

   ```powershell
   python --version
   ```

   Nếu hiện `Python 3.x.x` thì đã sẵn sàng. Nếu Windows báo không tìm thấy `python`, thử `py --version` và dùng `py` thay cho `python` ở các lệnh bên dưới.

## C. Mở Terminal đúng thư mục dự án

1. Trong File Explorer, mở thư mục dự án đã giải nén — chính thư mục có `main.py` và `requirements.txt`.
2. Bấm vào thanh địa chỉ của File Explorer, gõ `powershell`, rồi nhấn **Enter**.
3. Một cửa sổ PowerShell sẽ mở tại đúng thư mục dự án. Có thể kiểm tra bằng lệnh:

   ```powershell
   dir
   ```

   Danh sách cần có `main.py`, `requirements.txt`, thư mục `interface` và thư mục `static`.

## D. Cài thư viện và chạy website

Trong cửa sổ PowerShell vừa mở, chạy lần lượt từng lệnh:

```powershell
python -m pip install -r requirements.txt
```

Chờ cài đặt hoàn tất, sau đó chạy:

```powershell
python -m uvicorn main:app --reload
```

Khi thấy dòng gần giống `Uvicorn running on http://127.0.0.1:8000`, mở Chrome hoặc Edge và truy cập:

**http://127.0.0.1:8000**

Giữ cửa sổ PowerShell mở trong khi dùng website. Để tắt ứng dụng, quay lại cửa sổ đó và nhấn **Ctrl+C**.

## Nếu gặp lỗi

- **`python` không được nhận diện:** đóng rồi mở lại PowerShell sau khi cài Python; thử dùng `py` thay cho `python`.
- **Không tìm thấy `requirements.txt` hoặc `main`:** PowerShell đang ở sai thư mục. Mở lại thư mục chứa `main.py`, rồi gõ `powershell` ở thanh địa chỉ File Explorer.
- **Cổng 8000 đang được sử dụng:** đóng cửa sổ PowerShell đang chạy bản khác, hoặc chạy `python -m uvicorn main:app --reload --port 8001` rồi mở `http://127.0.0.1:8001`.
- **Giao diện thiếu kiểu chữ hoặc màu sắc:** kiểm tra kết nối Internet; một số kiểu giao diện được tải từ CDN.

## Luồng sử dụng

Trang chủ → chọn bài tập → Bắt đầu → Kết thúc → Trang tổng kết → Về trang chủ.
