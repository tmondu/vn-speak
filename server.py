import sys
import os

# Tự động nạp site-packages từ virtualenv nếu chạy bằng python3 hệ thống
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
venv_lib_dir = os.path.join(BASE_DIR, "venv", "lib")
if os.path.exists(venv_lib_dir):
    for py_ver in sorted(os.listdir(venv_lib_dir), reverse=True):
        sp = os.path.join(venv_lib_dir, py_ver, "site-packages")
        if os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)

import http.server
import socketserver
import json
import subprocess
import time
import base64
from normalizer import normalize_vietnamese_text

import urllib.request
import urllib.parse
import re

PORT = 8080
PIPER_BIN = os.path.join(BASE_DIR, "piper_bin", "piper", "piper")
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python3")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "static")

VIENEU_ENGINE = None

def get_vieneu_engine():
    global VIENEU_ENGINE
    if VIENEU_ENGINE is None:
        from vieneu import Vieneu
        VIENEU_ENGINE = Vieneu(mode="v3nano")
    return VIENEU_ENGINE

def generate_google_speech_bytes(text: str) -> bytes:
    parts = re.split(r'([.!?,\n;]+)', text)
    chunks = []
    curr = ""
    for part in parts:
        if len(curr) + len(part) < 150:
            curr += part
        else:
            if curr.strip():
                chunks.append(curr.strip())
            curr = part
    if curr.strip():
        chunks.append(curr.strip())
    if not chunks:
        chunks = [text[:150]]

    audio_buffer = bytearray()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for c in chunks:
        url = "https://translate.google.com/translate_tts?ie=UTF-8&tl=vi&client=tw-ob&q=" + urllib.parse.quote(c)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            audio_buffer.extend(resp.read())
    return bytes(audio_buffer)

MODELS = {
    "hoaimy": {
        "name": "🌟 Hoài My Neural (Studio 24kHz) - Chuẩn Vbee / VTV",
        "type": "edge",
        "voice_id": "vi-VN-HoaiMyNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Cao cấp nhất (95-98%) - Cực kỳ truyền cảm"
    },
    "namminh": {
        "name": "🌟 Nam Minh Neural (Studio 24kHz) - Chuẩn MC / Bản tin",
        "type": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Cao cấp nhất (95-98%) - Trầm ấm, chững chạc"
    },
    "chigoogle": {
        "name": "🗣️ Chị Google (Meme Quốc Dân 24kHz)",
        "type": "google",
        "sample_rate": "24.0 kHz",
        "quality": "Huyền thoại meme, phản hồi tức thì"
    },
    "vieneu_aihan": {
        "name": "🔥 VieNeu - Ái Hân (Nữ Miền Nam - Tin Tức 24kHz)",
        "type": "vieneu",
        "voice_id": "Ái Hân",
        "sample_rate": "24.0 kHz",
        "quality": "SOTA AI Mới - Nữ Nam Bộ biểu cảm"
    },
    "vieneu_adam": {
        "name": "🔥 VieNeu - Adam (Nam Miền Nam - Tự Nhiên 24kHz)",
        "type": "vieneu",
        "voice_id": "Adam",
        "sample_rate": "24.0 kHz",
        "quality": "SOTA AI Mới - Nam Nam Bộ tự nhiên"
    },
    "vieneu_myduyen": {
        "name": "🔥 VieNeu - Mỹ Duyên (Nữ Miền Bắc - Đọc Truyện 24kHz)",
        "type": "vieneu",
        "voice_id": "Mỹ Duyên",
        "sample_rate": "24.0 kHz",
        "quality": "SOTA AI Mới - Nữ Bắc Bộ truyền cảm"
    },
    "vieneu_ductri": {
        "name": "🔥 VieNeu - Đức Trí (Nam Miền Bắc - Đọc Truyện 24kHz)",
        "type": "vieneu",
        "voice_id": "Đức Trí",
        "sample_rate": "24.0 kHz",
        "quality": "SOTA AI Mới - Nam Bắc Bộ đọc truyện"
    },
    "vieneu_huuquan": {
        "name": "🔥 VieNeu - Hữu Quân (Nam Miền Bắc - Bản Tin 24kHz)",
        "type": "vieneu",
        "voice_id": "Hữu Quân",
        "sample_rate": "24.0 kHz",
        "quality": "SOTA AI Mới - Phát thanh viên thời sự"
    },
    "nu_phothong": {
        "name": "⚡ Nữ Phổ Thông (Piper 22kHz) - Mới Cập Nhật",
        "type": "piper",
        "file": os.path.join(MODELS_DIR, "vi_VN-giong_nu_pho_thong-medium.onnx"),
        "sample_rate": "22.05 kHz",
        "quality": "Offline CPU - Tự nhiên, 150ms"
    },
    "thanh_nien": {
        "name": "⚡ Thanh Niên Tự Tin (Piper 22kHz) - Mới Cập Nhật",
        "type": "piper",
        "file": os.path.join(MODELS_DIR, "vi_VN-thanh_nien_tu_tin-medium.onnx"),
        "sample_rate": "22.05 kHz",
        "quality": "Offline CPU - Trẻ trung, dứt khoát"
    },
    "vais1000": {
        "name": "⚡ VAIS 1000 (Piper 22kHz) - Mặc định cũ",
        "type": "piper",
        "file": os.path.join(MODELS_DIR, "vi_VN-vais1000-medium.onnx"),
        "sample_rate": "22.05 kHz",
        "quality": "Offline CPU - Chuẩn nghiên cứu"
    }
}

class TTSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()
        elif self.path.startswith("/api/models"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            model_info = {
                k: {"name": v["name"], "sample_rate": v["sample_rate"], "quality": v["quality"], "type": v["type"]}
                for k, v in MODELS.items()
            }
            self.wfile.write(json.dumps(model_info, ensure_ascii=False).encode("utf-8"))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/tts":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                raw_text = data.get("text", "").strip()
                voice_key = data.get("voice", "hoaimy")
                speed = float(data.get("speed", 1.0))
                sentence_silence = float(data.get("silence", 0.2))

                if not raw_text:
                    self.send_error(400, "Văn bản không được để trống")
                    return

                if voice_key not in MODELS:
                    voice_key = "hoaimy"

                model_entry = MODELS[voice_key]

                # 1. Text normalization
                # For Edge TTS neural, raw text often sounds even more natural, but normalized handles abbreviations nicely
                if model_entry["type"] == "edge":
                    normalized_text = normalize_vietnamese_text(raw_text)
                else:
                    normalized_text = normalize_vietnamese_text(raw_text)

                start_infer = time.time()

                if model_entry["type"] == "edge":
                    # Edge Neural TTS
                    out_filename = f"speech_edge_{int(time.time() * 1000)}.mp3"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/mp3"

                    # Calculate rate string: e.g. +10% or -15%
                    rate_pct = int((speed - 1.0) * 100)
                    rate_str = f"{rate_pct:+d}%" if rate_pct != 0 else "+0%"

                    cmd = [
                        VENV_PYTHON,
                        os.path.join(BASE_DIR, "edge_synthesize.py"),
                        "--voice", model_entry["voice_id"],
                        "--text", normalized_text,
                        "--out", out_path,
                        "--rate", rate_str
                    ]

                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate()

                    if process.returncode != 0 or not os.path.exists(out_path):
                        raise RuntimeError(f"Edge TTS error: {stderr}")

                    infer_duration = time.time() - start_infer
                    infer_time_ms = round(infer_duration * 1000, 1)

                    file_size = os.path.getsize(out_path)
                    # Approximate duration for 48kbps / 24kHz mp3: 1 sec ~= 6000 bytes
                    audio_seconds = round(file_size / 6000.0, 2)
                    rtf = round(infer_duration / max(audio_seconds, 0.001), 3)

                elif model_entry["type"] == "google":
                    # Google Translate TTS
                    out_filename = f"speech_google_{int(time.time() * 1000)}.mp3"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/mp3"

                    audio_bytes = generate_google_speech_bytes(normalized_text)
                    with open(out_path, "wb") as f:
                        f.write(audio_bytes)

                    infer_duration = time.time() - start_infer
                    infer_time_ms = round(infer_duration * 1000, 1)

                    file_size = len(audio_bytes)
                    audio_seconds = round(file_size / 6000.0, 2)
                    rtf = round(infer_duration / max(audio_seconds, 0.001), 3)

                elif model_entry["type"] == "vieneu":
                    # VieNeu-TTS v3 Nano (SOTA Local CPU)
                    out_filename = f"speech_vieneu_{int(time.time() * 1000)}.wav"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/wav"

                    try:
                        engine = get_vieneu_engine()
                        audio = engine.infer(text=normalized_text, voice=model_entry["voice_id"])
                        engine.save(audio, out_path)
                    except Exception as e:
                        # Fallback qua subprocess gọi venv python trực tiếp
                        cmd = [
                            VENV_PYTHON,
                            os.path.join(BASE_DIR, "vieneu_synthesize.py"),
                            "--voice", model_entry["voice_id"],
                            "--text", normalized_text,
                            "--out", out_path
                        ]
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        stdout, stderr = process.communicate()
                        if process.returncode != 0 or not os.path.exists(out_path):
                            raise RuntimeError(f"VieNeu synthesis error: {stderr or str(e)}")

                    infer_duration = time.time() - start_infer
                    infer_time_ms = round(infer_duration * 1000, 1)

                    import wave
                    with wave.open(out_path, "rb") as w:
                        frames = w.getnframes()
                        rate = w.getframerate()
                        audio_seconds = round(frames / float(rate), 2)

                    rtf = round(infer_duration / max(audio_seconds, 0.001), 3)

                else:
                    # Piper TTS (Local CPU)
                    out_filename = f"speech_piper_{int(time.time() * 1000)}.wav"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/wav"

                    length_scale = round(1.0 / max(speed, 0.2), 3)

                    cmd = [
                        PIPER_BIN,
                        "--model", model_entry["file"],
                        "--output_file", out_path,
                        "--length_scale", str(length_scale),
                        "--sentence_silence", str(sentence_silence)
                    ]

                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate(input=normalized_text)

                    if process.returncode != 0 or not os.path.exists(out_path):
                        raise RuntimeError(f"Piper error: {stderr}")

                    infer_duration = time.time() - start_infer
                    infer_time_ms = round(infer_duration * 1000, 1)

                    import wave
                    with wave.open(out_path, "rb") as w:
                        frames = w.getnframes()
                        rate = w.getframerate()
                        audio_seconds = round(frames / float(rate), 2)

                    rtf = round(infer_duration / max(audio_seconds, 0.001), 3)

                with open(out_path, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

                # Clean up old audio files
                try:
                    all_files = sorted([
                        os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)
                        if f.endswith(".wav") or f.endswith(".mp3")
                    ], key=os.path.getmtime)
                    if len(all_files) > 25:
                        for old in all_files[:-25]:
                            os.remove(old)
                except Exception:
                    pass

                response_payload = {
                    "success": True,
                    "audio_base64": audio_b64,
                    "mime_type": mime_type,
                    "normalized_text": normalized_text,
                    "infer_time_ms": infer_time_ms,
                    "audio_duration_sec": audio_seconds,
                    "rtf": rtf,
                    "sample_rate": model_entry["sample_rate"],
                    "voice_name": model_entry["name"]
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    server_address = ("0.0.0.0", PORT)
    with socketserver.ThreadingTCPServer(server_address, TTSHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"Server TTS Tiếng Việt đang chạy tại http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nĐang dừng server...")
            httpd.server_close()

if __name__ == "__main__":
    run()
