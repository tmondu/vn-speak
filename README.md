# ViVoice Studio - Vietnamese Neural TTS (Vercel Ready)

Hệ thống chuyển đổi văn bản thành giọng nói tiếng Việt chất lượng cao **24.0 kHz - 44.1 kHz**, chạy Serverless trên **Vercel** hoặc máy cục bộ.

## 🎙️ Danh sách giọng đọc hỗ trợ

### ⚡ Giọng Adam Miễn Phí (Mô hình AI Kokoro-82M Offline)
- `⚡ Adam Kokoro-82M (Nam - 24kHz)`: Giọng đọc Adam chạy bằng mô hình mã nguồn mở Kokoro-82M offline trên máy, **hoàn toàn miễn phí 100% không cần API Key**.

### 🎙️ Giọng Nam Đa Ngôn Ngữ Miễn Phí (Edge-TTS)
- `🎙️ Andrew Multilingual (Nam Mỹ - 24kHz)`: Giọng nam phong thái tự tin, trầm ấm, phong cách podcast / đàm thoại tự nhiên.
- `🎙️ Brian Multilingual (Nam Mỹ - 24kHz)`: Giọng nam ấm áp, truyền cảm, thích hợp kể chuyện và thuyết minh.

### 🌟 Giọng Tiếng Việt Miễn Phí (Edge-TTS)
- `🌟 Hoài My Neural (Nữ - 24kHz)`: Phát thanh viên miền Bắc, ngắt nghỉ hơi thở chân thực (Chuẩn Studio Vbee / VTV 98%).
- `🌟 Nam Minh Neural (Nam - 24kHz)`: Giọng đọc MC thời sự, trầm ấm, chững chạc (Chuẩn MC bản tin / sách nói 98%).

### 💎 Giọng Siêu Thực Cao Cấp (ElevenLabs)
- `💎 Adam ElevenLabs (Nam)`: Giọng nam trung niên huyền thoại của ElevenLabs — trầm ấm, cuốn hút, đỉnh cao cho sách nói (audiobook) và podcast. Hỗ trợ đa ngôn ngữ bao gồm tiếng Việt (*cần nhập API Key trên giao diện hoặc cấu hình `ELEVENLABS_API_KEY`*).

### 🗣️ Meme & Nhanh
- `🗣️ Chị Google`: Giọng đọc Google Dịch huyền thoại, chuẩn meme quốc dân, phản hồi siêu tốc.

## 🚀 Tính năng chính
- **Tự động chuẩn hóa tiếng Việt (Text Normalization)**: Phiên âm tự động số tiền (150k, 1.500.000đ), ngày tháng, giờ giấc, tỷ lệ phần trăm (3.5%), tốc độ (80km/h), nhiệt độ, từ viết tắt (AI, CEO, UBND, CSGT, TP.HCM...).
- **Hỗ trợ cả miễn phí & cao cấp**: Sử dụng Edge-TTS / Google TTS miễn phí 100% không tốn chi phí, đồng thời tích hợp sẵn ElevenLabs cho nhu cầu chất lượng cao nhất.
- **Triển khai 0 VNĐ trên Vercel**: Sử dụng Vercel Python Serverless Function (`api/index.py`), không cần cấu hình server phức tạp, không cần GPU.
- **Chạy cục bộ dễ dàng**: Khởi động web studio ngay trên máy với lệnh `python3 server.py`.

## 💻 Hướng dẫn chạy cục bộ
```bash
python3 server.py
# Mở trình duyệt tại http://localhost:8080
```

*(Tùy chọn) Cấu hình ElevenLabs API Key khi chạy cục bộ:*
```bash
export ELEVENLABS_API_KEY="xi-api-key-cua-ban"
python3 server.py
```

## 🚀 Hướng dẫn Deploy lên Vercel qua GitHub
1. Push mã nguồn lên GitHub:
   ```bash
   git add .
   git commit -m "Update TTS: Added Adam ElevenLabs & Multilingual voices"
   git push origin main
   ```
2. Truy cập [Vercel.com](https://vercel.com) -> Đăng nhập bằng GitHub -> Bấm **Add New...** -> **Project** -> Chọn repository vừa tạo -> Bấm **Deploy**.
3. *(Tùy chọn)* Trong phần **Settings -> Environment Variables** trên Vercel, thêm biến `ELEVENLABS_API_KEY` nếu muốn hệ thống tự nhận diện key cho giọng Adam.
4. Sau khoảng 15-20 giây, website của bạn sẽ hoạt động tại:
   `https://<ten-repo>.vercel.app`
