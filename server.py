import sys
import os
import glob

# Automatically include venv site-packages so python3 server.py always finds all dependencies
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_venv_site_packages = glob.glob(os.path.join(BASE_DIR, "venv", "lib", "python*", "site-packages"))
for _pkg in _venv_site_packages:
    if _pkg not in sys.path:
        sys.path.insert(0, _pkg)

import http.server
import socketserver
import json
import subprocess
import time
import base64
import urllib.request
import urllib.parse
import re

from normalizer import normalize_vietnamese_text

PORT = 8080
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "public")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELS = {
    "adam_kokoro": {
        "name": "⚡ Adam Kokoro-82M (Nam - Miễn Phí 100% Không Cần Key)",
        "type": "kokoro",
        "voice_id": "am_adam",
        "sample_rate": "24.0 kHz Studio",
        "quality": "AI Offline Miễn Phí (Kokoro-82M)",
        "requires_key": False
    },
    "andrew": {
        "name": "🎙️ Andrew Multilingual (Nam Mỹ - Trầm ấm 24kHz)",
        "type": "edge",
        "voice_id": "en-US-AndrewMultilingualNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Tự nhiên, phong cách Podcast / Trợ lý",
        "requires_key": False
    },
    "brian": {
        "name": "🎙️ Brian Multilingual (Nam Mỹ - Truyền cảm 24kHz)",
        "type": "edge",
        "voice_id": "en-US-BrianMultilingualNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Tự nhiên, phong cách Thuyết minh / Kể chuyện",
        "requires_key": False
    },
    "namminh": {
        "name": "🌟 Nam Minh Neural (Nam - Studio 24kHz)",
        "type": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Trầm ấm, thời sự / sách nói (98%)",
        "requires_key": False
    },
    "hoaimy": {
        "name": "🌟 Hoài My Neural (Nữ - Studio 24kHz)",
        "type": "edge",
        "voice_id": "vi-VN-HoaiMyNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Chuẩn Studio Vbee / VTV (98%)",
        "requires_key": False
    },
    "adam_eleven": {
        "name": "💎 Adam ElevenLabs (Nam - Huyền thoại Narration)",
        "type": "elevenlabs",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "sample_rate": "44.1 kHz Ultra",
        "quality": "Siêu thực (ElevenLabs Multilingual v2)",
        "requires_key": True
    },
    "chigoogle": {
        "name": "🗣️ Chị Google (Meme Quốc Dân - 24kHz)",
        "type": "google",
        "sample_rate": "24.0 kHz",
        "quality": "Giọng đọc kinh điển, phản hồi tức thì",
        "requires_key": False
    }
}

_kokoro_instance = None

def get_kokoro_instance():
    global _kokoro_instance
    if _kokoro_instance is None:
        model_path = os.path.join(BASE_DIR, "models", "kokoro", "kokoro-v1.0.onnx")
        voices_path = os.path.join(BASE_DIR, "models", "kokoro", "voices-v1.0.bin")
        if not os.path.exists(model_path) or not os.path.exists(voices_path):
            raise RuntimeError("Mô hình Kokoro chưa sẵn sàng. Hãy đảm bảo các file trong 'models/kokoro/' đã được tải về.")
        from kokoro_onnx import Kokoro
        _kokoro_instance = Kokoro(model_path, voices_path)
    return _kokoro_instance

def generate_kokoro_speech_bytes(text: str, voice_id: str = "am_adam", speed: float = 1.0) -> bytes:
    import io
    import wave
    import numpy as np
    kokoro = get_kokoro_instance()
    samples, sample_rate = kokoro.create(text, voice=voice_id, speed=speed, lang="en-us")
    
    int16_samples = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_samples.tobytes())
    return wav_io.getvalue()

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

def generate_elevenlabs_speech_bytes(text: str, voice_id: str, api_key: str = None, model_id: str = "eleven_multilingual_v2") -> bytes:
    key = (api_key or os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVEN_API_KEY") or "").strip()
    if not key:
        raise ValueError("Vui lòng nhập ElevenLabs API Key để sử dụng giọng Adam (hoặc cấu hình biến môi trường ELEVENLABS_API_KEY).")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_body)
            detail = err_json.get("detail", {})
            if isinstance(detail, dict):
                msg = detail.get("message", err_body)
            else:
                msg = str(detail) or err_body
        except Exception:
            msg = err_body
        if e.code == 401:
            raise RuntimeError(f"ElevenLabs API Key không hợp lệ hoặc sai (HTTP 401): {msg}")
        elif e.code == 429:
            raise RuntimeError(f"ElevenLabs vượt hạn mức ký tự / tốc độ (HTTP 429): {msg}")
        else:
            raise RuntimeError(f"ElevenLabs API Error ({e.code}): {msg}")
    except Exception as e:
        raise RuntimeError(f"Không thể kết nối đến ElevenLabs: {str(e)}")

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
                k: {
                    "name": v["name"],
                    "sample_rate": v["sample_rate"],
                    "quality": v["quality"],
                    "type": v["type"],
                    "requires_key": v.get("requires_key", False)
                }
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
                api_key = data.get("api_key", "").strip()

                if not raw_text:
                    self.send_error(400, "Văn bản không được để trống")
                    return

                if voice_key not in MODELS:
                    voice_key = "hoaimy"

                model_entry = MODELS[voice_key]

                # 1. Text normalization
                normalized_text = normalize_vietnamese_text(raw_text)

                start_infer = time.time()

                if model_entry["type"] == "kokoro":
                    out_filename = f"speech_kokoro_{int(time.time() * 1000)}.wav"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/wav"

                    audio_bytes = generate_kokoro_speech_bytes(
                        normalized_text,
                        voice_id=model_entry["voice_id"],
                        speed=speed
                    )
                    with open(out_path, "wb") as f:
                        f.write(audio_bytes)

                    infer_duration = time.time() - start_infer
                    infer_time_ms = round(infer_duration * 1000, 1)

                    file_size = len(audio_bytes)
                    audio_seconds = round(max(0, file_size - 44) / 48000.0, 2)

                elif model_entry["type"] == "elevenlabs":
                    out_filename = f"speech_eleven_{int(time.time() * 1000)}.mp3"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/mp3"

                    audio_bytes = generate_elevenlabs_speech_bytes(
                        normalized_text,
                        model_entry["voice_id"],
                        api_key=api_key
                    )
                    with open(out_path, "wb") as f:
                        f.write(audio_bytes)

                    infer_duration = time.time() - start_infer
                    infer_time_ms = round(infer_duration * 1000, 1)

                    file_size = len(audio_bytes)
                    audio_seconds = round(file_size / 6000.0, 2)

                elif model_entry["type"] == "edge":
                    out_filename = f"speech_edge_{int(time.time() * 1000)}.mp3"
                    out_path = os.path.join(OUTPUT_DIR, out_filename)
                    mime_type = "audio/mp3"

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
                    audio_seconds = round(file_size / 6000.0, 2)

                elif model_entry["type"] == "google":
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

                with open(out_path, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

                # Clean up old audio files
                try:
                    for old_f in os.listdir(OUTPUT_DIR):
                        fp = os.path.join(OUTPUT_DIR, old_f)
                        if os.path.isfile(fp) and time.time() - os.path.getmtime(fp) > 3600:
                            os.remove(fp)
                except Exception:
                    pass

                response_data = {
                    "success": True,
                    "audio_base64": audio_b64,
                    "mime_type": mime_type,
                    "normalized_text": normalized_text,
                    "infer_time_ms": infer_time_ms,
                    "audio_duration_sec": audio_seconds,
                    "sample_rate": model_entry["sample_rate"],
                    "voice_name": model_entry["name"]
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint not found")

def run(port=PORT):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), TTSHandler) as httpd:
        print(f"🚀 ViVoice Studio running at http://localhost:{port}")
        print("🎙️ Hỗ trợ các giọng đọc Studio 24kHz - 44.1kHz: Adam ElevenLabs, Andrew, Brian, Nam Minh, Hoài My, Chị Google")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
