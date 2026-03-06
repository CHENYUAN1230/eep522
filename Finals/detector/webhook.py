from flask import Flask, request, abort
import requests
import time
import os
from config import LINE_TOKEN, LINE_USER_ID

app = Flask(__name__)

# Ngrok public URL - update this every time ngrok restarts
NGROK_URL = os.getenv("NGROK_URL", "")

def reply_message(reply_token: str, messages: list):
    """Send a reply message using Line reply API."""
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "replyToken": reply_token,
            "messages": messages,
        },
        timeout=10,
    )

ALLOWED_USERS = {LINE_USER_ID}
def handle_command(text: str, reply_token: str, user_id: str):
    """Parse incoming text and respond with appropriate action."""
    
    if user_id not in ALLOWED_USERS:
        reply_message(reply_token, [
            {"type": "text", "text": "No Authorization"}
        ])
        return
    
    text = text.strip().lower()

    if text in ["camera", "live", "stream", "看"]:
        # Return live stream URL
        if NGROK_URL:
            msg = (
                f"📹 Live Stream\n"
                f"Open in browser:\n"
                f"{NGROK_URL}\n\n"
                f"🕐 {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            msg = "⚠️ Stream URL not configured. Set NGROK_URL in .env file."

        reply_message(reply_token, [
            {"type": "text", "text": msg}
        ])

    elif text in ["status", "state"]:
        # Return current system status
        msg = (
            f"✅ System Status\n"
            f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔍 Detection: Running\n"
            f"📡 Stream: {'Online' if NGROK_URL else 'Offline'}"
        )
        reply_message(reply_token, [
            {"type": "text", "text": msg}
        ])

    else:
        # Return help message for unknown commands
        msg = (
            f"🤖 Bike Security Bot\n\n"
            f"Available commands:\n"
            f"  camera — Get live stream URL\n"
            f"  status — Check system status"
        )
        reply_message(reply_token, [
            {"type": "text", "text": msg}
        ])

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

def run_webhook():
    """Entry point to start the webhook server."""
    print("[Webhook] Starting webhook server on port 5001...")
    app.run(host="0.0.0.0", port=5001, threaded=True)
