"""
Flask + WebSocket server for real-time movie dubbing.

Serves the video player UI and manages the audio processing pipeline:
  1. Client sends audio chunks via WebSocket
  2. Server transcribes with Whisper, translates, generates Finnish TTS
  3. Streams back dubbed audio + English subtitle cues
"""
import os
import asyncio
import tempfile
import threading
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sock import Sock

from audio_pipeline import AudioPipeline

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
sock = Sock(app)

pipeline = AudioPipeline()


@app.route("/")
def index():
    return render_template("player.html")


from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".mp3", ".wav", ".m4a"}

@app.route("/upload", methods=["POST"])
def upload_video():
    """Accept a video file upload safely and return its local URL."""
    video = request.files.get("video")
    if not video or not video.filename:
        return jsonify({"error": "No video file provided"}), 400

    raw_filename = secure_filename(video.filename)
    if not raw_filename:
        return jsonify({"error": "Invalid filename"}), 400

    ext = Path(raw_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file extension '{ext}'"}), 400

    save_path = UPLOAD_DIR / raw_filename
    video.save(str(save_path))
    return jsonify({"url": f"/video/{raw_filename}", "filename": raw_filename})


@app.route("/video/<path:filename>")
def serve_video(filename):
    safe_name = secure_filename(filename)
    return send_from_directory(str(UPLOAD_DIR), safe_name)


@sock.route("/ws/dub")
def dub_stream(ws):
    """
    WebSocket endpoint for real-time dubbing.

    Protocol (JSON messages):
      Client -> Server:
        {"type": "audio_chunk", "data": "<base64 PCM>", "timestamp": 0.0}
        {"type": "config", "source_lang": "en", "target_lang": "fi"}
      Server -> Client:
        {"type": "subtitle", "text": "...", "start": 0.0, "end": 2.5}
        {"type": "dubbed_audio", "data": "<base64 MP3>", "timestamp": 0.0}
        {"type": "status", "message": "..."}
    """
    import json
    import base64

    ws.send(json.dumps({"type": "status", "message": "Pipeline ready"}))

    while True:
        raw = ws.receive()
        if raw is None:
            break

        try:
            msg = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue

        msg_type = msg.get("type")

        if msg_type == "config":
            pipeline.configure(
                source_lang=msg.get("source_lang", "auto"),
                target_lang=msg.get("target_lang", "fi"),
            )
            ws.send(json.dumps({"type": "status", "message": "Configured"}))

        elif msg_type == "start_preprocess":
            filename = msg.get("filename", "")
            video_path = UPLOAD_DIR / filename
            if not video_path.exists():
                ws.send(json.dumps({"type": "error", "message": f"File {filename} not found"}))
                continue

            def on_progress(data):
                try:
                    ws.send(json.dumps(data))
                except Exception:
                    pass

            def run_batch():
                try:
                    # Stage 1: Extract Speaker Voice Profile & Pitch
                    def voice_cb(percent, msg):
                        on_progress({
                            "type": "voice_analysis_progress",
                            "percent": percent,
                            "message": msg,
                        })

                    profile = pipeline.speaker_extractor.extract_speaker_profile(
                        str(video_path),
                        progress_cb=voice_cb,
                    )
                    pipeline.speaker_profile = profile

                    on_progress({
                        "type": "speaker_profile_ready",
                        "profile": profile,
                    })

                    # Stage 2: Fast-Start Buffer (initial 2 minutes = 120 seconds)
                    pipeline.process_video_batch(
                        str(video_path),
                        start_time=0.0,
                        max_duration=120.0,
                        progress_cb=on_progress,
                    )
                    try:
                        ws.send(json.dumps({"type": "preprocess_fast_start_ready", "duration": 120.0}))
                    except Exception:
                        pass

                    # Stage 3: Background Continuous Streaming (5-minute chunks = 300s)
                    audio = pipeline.get_or_load_video_audio(str(video_path))
                    total_duration = len(audio) / 16000
                    current_start = 120.0

                    while current_start < total_duration:
                        pipeline.process_video_batch(
                            str(video_path),
                            start_time=current_start,
                            max_duration=300.0,
                            progress_cb=on_progress,
                        )
                        current_start += 300.0

                    try:
                        ws.send(json.dumps({"type": "preprocess_all_complete"}))
                    except Exception:
                        pass

                except Exception as exc:
                    try:
                        ws.send(json.dumps({"type": "error", "message": str(exc)}))
                    except Exception:
                        pass

            threading.Thread(target=run_batch, daemon=True).start()

        elif msg_type == "audio_chunk":
            audio_b64 = msg.get("data", "")
            timestamp = msg.get("timestamp", 0.0)

            try:
                pcm_bytes = base64.b64decode(audio_b64)

                def send_status(step, detail):
                    try:
                        ws.send(json.dumps({
                            "type": "progress",
                            "step": step,
                            "message": detail,
                        }))
                    except Exception:
                        pass

                result = pipeline.process_chunk(pcm_bytes, timestamp, status_cb=send_status)

                if result.get("subtitle"):
                    ws.send(json.dumps({
                        "type": "subtitle",
                        "text": result["subtitle"],
                        "start": result["sub_start"],
                        "end": result["sub_end"],
                    }))

                if result.get("dubbed_audio"):
                    ws.send(json.dumps({
                        "type": "dubbed_audio",
                        "data": base64.b64encode(result["dubbed_audio"]).decode(),
                        "timestamp": timestamp,
                    }))
            except Exception as exc:
                ws.send(json.dumps({
                    "type": "error",
                    "message": str(exc),
                }))


if __name__ == "__main__":
    print("Starting DubStream on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
