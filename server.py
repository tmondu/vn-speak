import sys
import os
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "public")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELS = {
    "hoaimy": {
        "name": "🌟 Hoài My Neural (Nữ - Studio 24kHz)",
        "type": "edge",
        "voice_id": "vi-VN-HoaiMyNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Chuẩn Studio Vbee / VTV (98%)"
    },
    "namminh": {
        "name": "🌟 Nam Minh Neural (Nam - Studio 24kHz)",
        "type": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Trầm ấm, thời sự / sách nói (98%)"
    },
    "chigoogle": {
        "name": "🗣️ Chị Google (Meme Quốc Dân - 24kHz)",
        "type": "google",
        "sample_rate": "24.0 kHz",
        "quality": "Giọng đọc kinh điển, phản hồi tức thì"
    }
}

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

                if not raw_text:
                    self.send_error(400, "Văn bản không được để trống")
                    return

                if voice_key not in MODELS:
                    voice_key = "hoaimy"

                model_entry = MODELS[voice_key]

                # 1. Text normalization
                normalized_text = normalize_vietnamese_text(raw_text)

                start_infer = time.time()

                if model_entry["type"] == "edge":
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
        print("🎙️ Hỗ trợ 3 giọng đọc Studio 24kHz: Hoài My, Nam Minh, Chị Google")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
