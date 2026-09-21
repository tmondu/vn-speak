# ViVoice Studio - Vietnamese Neural TTS (Vercel Ready)

Hệ thống chuyển đổi văn bản thành giọng nói tiếng Việt chất lượng cao **24.0 kHz**, chạy Serverless hoàn toàn miễn phí trên **Vercel** hoặc máy cục bộ.

## 🌟 3 Giọng đọc nổi bật (24.0 kHz)
- `🌟 Hoài My Neural (Nữ)`: Phát thanh viên miền Bắc, ngắt nghỉ hơi thở chân thực (Chuẩn Studio Vbee / VTV 98%).
- `🌟 Nam Minh Neural (Nam)`: Giọng đọc MC thời sự, trầm ấm, chững chạc (Chuẩn MC bản tin / sách nói 98%).
- `🗣️ Chị Google`: Giọng đọc Google Dịch huyền thoại, chuẩn meme quốc dân, phản hồi siêu tốc (~250ms).

## 🚀 Tính năng chính
- **Tự động chuẩn hóa tiếng Việt (Text Normalization)**: Phiên âm tự động số tiền (150k, 1.500.000đ), ngày tháng, giờ giấc, tỷ lệ phần trăm (3.5%), tốc độ (80km/h), nhiệt độ, từ viết tắt (AI, CEO, UBND, CSGT, TP.HCM...).
- **Triển khai 0 VNĐ trên Vercel**: Sử dụng Vercel Python Serverless Function (`api/index.py`), không cần cấu hình server, không cần GPU.
- **Chạy cục bộ dễ dàng**: Khởi động web studio ngay trên máy với lệnh `python3 server.py`.

## 💻 Hướng dẫn chạy cục bộ
```bash
python3 server.py
# Mở trình duyệt tại http://localhost:8080
```

## 🚀 Hướng dẫn Deploy lên Vercel qua GitHub
1. Push mã nguồn lên GitHub:
   ```bash
   git add .
   git commit -m "Update TTS: 3 voices (Hoài My, Nam Minh, Chị Google)"
   git push origin main
   ```
2. Truy cập [Vercel.com](https://vercel.com) -> Đăng nhập bằng GitHub -> Bấm **Add New...** -> **Project** -> Chọn repository vừa tạo -> Bấm **Deploy**.
3. Sau khoảng 15-20 giây, website của bạn sẽ hoạt động hoàn toàn miễn phí dạng:
   `https://<ten-repo>.vercel.app`
