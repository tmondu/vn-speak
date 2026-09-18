# ViVoice Studio - Vietnamese Neural TTS (Vercel Ready)

Hệ thống chuyển đổi văn bản thành giọng nói tiếng Việt chất lượng phòng thu cao cấp **24.0 kHz** (chuẩn Vbee / VTV), chạy Serverless hoàn toàn miễn phí trên **Vercel**.

## 🌟 Tính năng nổi bật
- **Chất lượng Studio 24kHz (98%)**: Tích hợp 2 giọng đọc Neural truyền cảm:
  - `Hoài My Neural (Nữ)`: Phát thanh viên miền Bắc, ngắt nghỉ hơi thở chân thực.
  - `Nam Minh Neural (Nam)`: Giọng đọc MC thời sự, trầm ấm, chững chạc.
- **Tự động chuẩn hóa tiếng Việt (Text Normalization)**: Phiên âm tự động số tiền (150k, 1.500.000đ), ngày tháng, giờ giấc, tỷ lệ phần trăm (3.5%), tốc độ (80km/h), nhiệt độ, từ viết tắt (AI, CEO, UBND, CSGT, TP.HCM...).
- **Triển khai 0 VNĐ trên Vercel**: Sử dụng Vercel Python Serverless Function (`api/index.py`), không cần cấu hình server.

## 🚀 Hướng dẫn Deploy lên Vercel qua GitHub

1. Tạo một repository mới trên GitHub (ví dụ: `vits-vietnamese-tts`).
2. Push mã nguồn lên GitHub:
   ```bash
   git add .
   git commit -m "Deploy ViVoice Studio to Vercel"
   git branch -M main
   git remote add origin https://github.com/<tai-khoan-cua-ban>/<ten-repo>.git
   git push -u origin main
   ```
3. Truy cập [Vercel.com](https://vercel.com) -> Đăng nhập bằng GitHub -> Bấm **Add New...** -> **Project** -> Chọn repository vừa tạo -> Bấm **Deploy**.
4. Sau khoảng 20-30 giây, trang web của bạn sẽ hoạt động với tên miền miễn phí dạng:
   `https://<ten-repo>.vercel.app`
