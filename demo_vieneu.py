#!/usr/bin/env python3
"""
VieNeu-TTS Demo & Voice Cloning CLI
Hệ thống chuyển đổi văn bản thành giọng nói tiếng Việt thế hệ mới (SOTA).
Hỗ trợ 11 giọng đọc đa vùng miền (Bắc, Nam) và nhân bản giọng nói (Instant Voice Cloning).
"""
import argparse
import os
import sys
import time

# Tự động nạp site-packages từ virtualenv nếu chạy bằng python3 hệ thống
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
venv_lib_dir = os.path.join(BASE_DIR, "venv", "lib")
if os.path.exists(venv_lib_dir):
    for py_ver in sorted(os.listdir(venv_lib_dir), reverse=True):
        sp = os.path.join(venv_lib_dir, py_ver, "site-packages")
        if os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)

def main():
    parser = argparse.ArgumentParser(description="VieNeu-TTS Vietnamese Voice Synthesis & Cloning")
    parser.add_argument("--text", "-t", default="Xin chào, đây là giọng đọc AI thế hệ mới từ VieNeu Studio.", help="Văn bản tiếng Việt cần đọc")
    parser.add_argument("--voice", "-v", default="Ái Hân", help="Tên giọng preset: Ái Hân, Adam, Mỹ Duyên, Đức Trí, Hữu Quân, Mạnh Dũng...")
    parser.add_argument("--clone-ref", "-c", default=None, help="Đường dẫn file .wav mẫu (3-10 giây) để clone giọng nói")
    parser.add_argument("--out", "-o", default="output/vieneu_demo.wav", help="File wav đầu ra")
    parser.add_argument("--list-voices", action="store_true", help="Hiển thị danh sách các giọng preset có sẵn")
    args = parser.parse_args()

    from vieneu import Vieneu

    print("⏳ Khởi tạo engine VieNeu-TTS v3 Nano (24kHz ONNX CPU)...")
    tts = Vieneu(mode="v3nano")

    if args.list_voices:
        print("\n📢 Danh sách các giọng preset:")
        for desc, name in tts.list_preset_voices():
            print(f"  • {desc}")
        return

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    t0 = time.time()
    if args.clone_ref:
        if not os.path.exists(args.clone_ref):
            print(f"❌ Không tìm thấy file âm thanh mẫu: {args.clone_ref}")
            sys.exit(1)
        print(f"🎙️ Đang trích xuất đặc trưng giọng từ: {args.clone_ref}...")
        ref_voice = tts.encode_reference(args.clone_ref)
        print(f"⚡ Đang tổng hợp giọng nói nhân bản cho: \"{args.text}\"")
        audio = tts.infer(text=args.text, voice=ref_voice)
    else:
        print(f"⚡ Đang đọc với giọng \"{args.voice}\": \"{args.text}\"")
        audio = tts.infer(text=args.text, voice=args.voice)

    tts.save(audio, args.out)
    duration = time.time() - t0
    print(f"✅ Hoàn tất trong {duration:.2f} giây!")
    print(f"📁 File âm thanh đã lưu: {args.out}")

if __name__ == "__main__":
    main()
