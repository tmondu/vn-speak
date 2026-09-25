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

import urllib.request
import urllib.parse
import re

VOICES = {
    "adam_eleven": {
        "id": "pNInz6obpgDQGcFmaJgB",
        "name": "💎 Adam ElevenLabs (Nam - Huyền thoại Narration)",
        "sample_rate": "44.1 kHz Ultra",
        "quality": "Siêu thực (ElevenLabs Multilingual v2)",
        "engine": "elevenlabs",
        "requires_key": True
    },
    "andrew": {
        "id": "en-US-AndrewMultilingualNeural",
        "name": "🎙️ Andrew Multilingual (Nam Mỹ - Trầm ấm 24kHz)",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Tự nhiên, phong cách Podcast / Trợ lý",
        "engine": "edge",
        "requires_key": False
    },
    "brian": {
        "id": "en-US-BrianMultilingualNeural",
        "name": "🎙️ Brian Multilingual (Nam Mỹ - Truyền cảm 24kHz)",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Tự nhiên, phong cách Thuyết minh / Kể chuyện",
        "engine": "edge",
        "requires_key": False
    },
    "namminh": {
        "id": "vi-VN-NamMinhNeural",
        "name": "🌟 Nam Minh Neural (Nam - Studio 24kHz)",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Trầm ấm, thời sự / sách nói (98%)",
        "engine": "edge",
        "requires_key": False
    },
    "hoaimy": {
        "id": "vi-VN-HoaiMyNeural",
        "name": "🌟 Hoài My Neural (Nữ - Studio 24kHz)",
        "sample_rate": "24.0 kHz Studio",
        "quality": "Chuẩn Studio Vbee / VTV (98%)",
        "engine": "edge",
        "requires_key": False
    },
    "chigoogle": {
        "id": "chigoogle",
        "name": "🗣️ Chị Google (Meme Quốc Dân - 24kHz)",
        "sample_rate": "24.0 kHz",
        "quality": "Giọng đọc kinh điển, phản hồi tức thì",
        "engine": "google",
        "requires_key": False
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
            raise RuntimeError(f"ElevenLabs API Key không hợp lệ (HTTP 401): {msg}")
        elif e.code == 429:
            raise RuntimeError(f"ElevenLabs vượt hạn mức ký tự / tốc độ (HTTP 429): {msg}")
        else:
            raise RuntimeError(f"ElevenLabs API Error ({e.code}): {msg}")
    except Exception as e:
        raise RuntimeError(f"Không thể kết nối đến ElevenLabs: {str(e)}")

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
            api_key = req_json.get("api_key", "").strip()

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
            if selected_voice.get("engine") == "elevenlabs":
                audio_bytes = generate_elevenlabs_speech_bytes(
                    normalized_text,
                    selected_voice["id"],
                    api_key=api_key
                )
            elif selected_voice.get("engine") == "google":
                audio_bytes = generate_google_speech_bytes(normalized_text)
            else:
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
