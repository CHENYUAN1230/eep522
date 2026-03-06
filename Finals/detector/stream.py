from flask import Flask, Response, render_template_string, request, abort
import numpy as np
import cv2
import time
from config import CAMERA_WIDTH, CAMERA_HEIGHT
from webhook import handle_command

app = Flask(__name__)

# Shared memory references (set by run.py before starting)
_shared_frame = None
_frame_lock   = None

def init_stream(shared_frame, frame_lock):
    """Initialize shared memory references for this process."""
    global _shared_frame, _frame_lock
    _shared_frame = shared_frame
    _frame_lock   = frame_lock

def read_shared_frame():
    """Read the latest frame from shared memory and return as JPEG bytes."""
    with _frame_lock:
        arr   = np.frombuffer(_shared_frame.get_obj(), dtype=np.uint8)
        frame = arr.reshape((CAMERA_HEIGHT, CAMERA_WIDTH, 3)).copy()

    _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return jpeg.tobytes()

def generate_frames():
    """Generator that yields MJPEG frames continuously."""
    while True:
        try:
            frame_bytes = read_shared_frame()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame_bytes +
                b"\r\n"
            )
        except Exception as e:
            print(f"[Stream] Frame error: {e}")
        time.sleep(0.1)  # ~10 FPS for stream

# Simple HTML page for live view
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bike Security Camera</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body  { background: #111; display: flex; flex-direction: column;
                align-items: center; justify-content: center; height: 100vh; margin: 0; }
        h2    { color: #fff; font-family: sans-serif; margin-bottom: 12px; }
        img   { max-width: 100%; border: 2px solid #444; border-radius: 8px; }
        p     { color: #888; font-family: sans-serif; font-size: 12px; margin-top: 8px; }
    </style>
</head>
<body>
    <h2>Bike Security Camera — Live View</h2>
    <img src="/video_feed" />
    <p>Refreshes automatically. Close tab when done.</p>
</body>
</html>
"""

@app.route("/")
def index():
    """Serve the live view HTML page."""
    return render_template_string(HTML_PAGE)

@app.route("/video_feed")
def video_feed():
    """MJPEG stream endpoint."""
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive and handle Line webhook events."""
    body = request.get_json()
    if not body:
        abort(400)

    for event in body.get("events", []):
        # Only handle text message events
        if event.get("type") != "message":
            continue
        if event["message"].get("type") != "text":
            continue

        text        = event["message"]["text"]
        reply_token = event["replyToken"]
        user_id = event["source"].get("userId", "")

        print(f"[Webhook] Received: {text}")
        handle_command(text, reply_token, user_id)

    return "OK", 200

def run_stream(shared_frame, frame_lock):
    """Entry point called by run.py to start the Flask server on port 5000."""
    init_stream(shared_frame, frame_lock)
    print("[Stream] Starting server on port 5000...")
    app.run(host="0.0.0.0", port=5000, threaded=True)