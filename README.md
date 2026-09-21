# ViVoice Studio - Vietnamese Neural TTS (Vercel Ready)

Hệ thống chuyển đổi văn bản thành giọng nói tiếng Việt chất lượng phòng thu cao cấp **24.0 kHz** (chuẩn Vbee / VTV), chạy Serverless hoàn toàn miễn phí trên **Vercel**.

## 🌟 Tính năng nổi bật
- **Đa dạng giọng đọc chất lượng cao (24.0 kHz)**:
  - `🌟 Hoài My Neural (Nữ)`: Phát thanh viên miền Bắc, ngắt nghỉ hơi thở chân thực (Chuẩn Studio Vbee / VTV).
  - `🌟 Nam Minh Neural (Nam)`: Giọng đọc MC thời sự, trầm ấm, chững chạc.
  - `🗣️ Chị Google`: Giọng đọc Google Dịch huyền thoại, chuẩn meme quốc dân, phản hồi tức thì (~250ms).
  - `🔥 VieNeu-TTS v3 (SOTA CPU)`: Mô hình AI thế hệ mới với 11 giọng đọc Bắc - Nam (Ái Hân, Adam, Mỹ Duyên, Đức Trí, Mạnh Dũng...) và khả năng **Instant Voice Cloning** (nhân bản giọng nói bất kỳ từ file mẫu 3-5s).
- **Tự động chuẩn hóa tiếng Việt (Text Normalization)**: Phiên âm tự động số tiền (150k, 1.500.000đ), ngày tháng, giờ giấc, tỷ lệ phần trăm (3.5%), tốc độ (80km/h), nhiệt độ, từ viết tắt (AI, CEO, UBND, CSGT, TP.HCM...).
- **Triển khai 0 VNĐ trên Vercel**: Sử dụng Vercel Python Serverless Function (`api/index.py`), không cần GPU, hoàn toàn miễn phí.

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

## 💻 Trải nghiệm Cục bộ & Voice Cloning với VieNeu-TTS

### 1. Khởi động Web Server cục bộ:
```bash
python3 server.py
# Mở trình duyệt tại http://localhost:8080
```
Giao diện sẽ có đầy đủ các giọng: Hoài My, Nam Minh, Chị Google, Ái Hân, Adam, Mỹ Duyên, Đức Trí...

### 2. Sử dụng CLI VieNeu & Nhân bản giọng nói (Voice Cloning):
- **Xem danh sách 11 giọng đọc preset**:
  ```bash
  python3 demo_vieneu.py --list-voices
  ```
- **Đọc văn bản với giọng preset (ví dụ giọng Nữ miền Nam Ái Hân hoặc Mỹ Duyên)**:
  ```bash
  python3 demo_vieneu.py -v "Ái Hân" -t "Xin kính chào quý thính giả đài phát thanh miền Nam." -o output/aihan.wav
  ```
- **Nhân bản bất kỳ giọng nói nào từ file âm thanh mẫu (3-5 giây)**:
  ```bash
  python3 demo_vieneu.py -c path/to/sample.wav -t "Câu văn bạn muốn đọc bằng giọng nhân bản" -o output/cloned.wav
  ```
