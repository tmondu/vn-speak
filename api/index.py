from http.server import BaseHTTPRequestHandler
import json
import asyncio
import base64
import time
import os
import sys
import edge_tts

# Add current directory to path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from normalizer import normalize_vietnamese_text

VOICES = {
    "hoaimy": {
        "id": "vi-VN-HoaiMyNeural",
        "name": "🌟 Hoài My Neural (Nữ - Studio 24kHz)",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Chuẩn Studio Vbee / VTV (98%)"
    },
    "namminh": {
        "id": "vi-VN-NamMinhNeural",
        "name": "🌟 Nam Minh Neural (Nam - Studio 24kHz)",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Trầm ấm, thời sự / sách nói (98%)"
    }
}

async def generate_speech_bytes(text: str, voice_id: str, rate_str: str = None, retries: int = 3) -> bytes:
    kwargs = {}
    if rate_str and rate_str != "+0%":
        kwargs["rate"] = rate_str

    last_err = None
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text, voice_id, **kwargs)
            audio_buffer = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.extend(chunk["data"])
            if len(audio_buffer) > 0:
                return bytes(audio_buffer)
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            else:
                raise last_err
    raise RuntimeError(f"Không thể tạo âm thanh: {last_err}")

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(VOICES, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        
        try:
            req_json = json.loads(post_data) if post_data else {}
            raw_text = req_json.get("text", "").strip()
            voice_key = req_json.get("voice", "hoaimy")
            speed = float(req_json.get("speed", 1.0))

            if not raw_text:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Văn bản không được để trống"}).encode("utf-8"))
                return

            if voice_key not in VOICES:
                voice_key = "hoaimy"

            selected_voice = VOICES[voice_key]

            # 1. Normalize text
            normalized_text = normalize_vietnamese_text(raw_text)

            # 2. Rate format (e.g. +10%, -15%)
            rate_pct = int((speed - 1.0) * 100)
            rate_str = f"{rate_pct:+d}%" if rate_pct != 0 else "+0%"

            # 3. Synthesize speech in memory
            start_time = time.time()
            audio_bytes = asyncio.run(
                generate_speech_bytes(normalized_text, selected_voice["id"], rate_str=rate_str)
            )
            infer_duration_ms = round((time.time() - start_time) * 1000, 1)

            # 4. Approximate duration
            audio_seconds = round(len(audio_bytes) / 6000.0, 2)

            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

            response_data = {
                "success": True,
                "audio_base64": audio_b64,
                "mime_type": "audio/mp3",
                "normalized_text": normalized_text,
                "infer_time_ms": infer_duration_ms,
                "audio_duration_sec": audio_seconds,
                "sample_rate": selected_voice["sample_rate"],
                "voice_name": selected_voice["name"]
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

        except Exception as err:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(err)}, ensure_ascii=False).encode("utf-8"))
