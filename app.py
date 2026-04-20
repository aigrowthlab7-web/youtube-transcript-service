from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

def extract_video_id(value):
    if not value:
        return None

    value = value.strip()

    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
        r"(?:shorts/)([a-zA-Z0-9_-]{11})",
        r"\b([a-zA-Z0-9_-]{11})\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)

    return None

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "YouTube transcript microservice is running"
    })

@app.route("/transcript", methods=["POST"])
def transcript():
    data = request.get_json(silent=True) or {}

    raw_input = data.get("video_id") or data.get("youtube_url")
    video_id = extract_video_id(raw_input)

    if not video_id:
        return jsonify({
            "success": False,
            "error": "Invalid or missing YouTube URL / video_id"
        }), 400

    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)

        chunks = []
        full_text_parts = []

        for item in fetched:
            text = getattr(item, "text", "")
            start = getattr(item, "start", 0)
            duration = getattr(item, "duration", 0)

            chunks.append({
                "text": text,
                "start": start,
                "duration": duration
            })

            if text:
                full_text_parts.append(text)

        full_text = " ".join(full_text_parts).strip()

        return jsonify({
            "success": True,
            "video_id": video_id,
            "transcript_text": full_text,
            "chunks": chunks,
            "chunk_count": len(chunks)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "video_id": video_id,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
