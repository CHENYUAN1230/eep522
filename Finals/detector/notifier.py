import requests
import time
import os
import glob
import cloudinary
import cloudinary.uploader
from datetime import datetime, timedelta
from config import LINE_TOKEN, LINE_USER_ID
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

# Configure Cloudinary
cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
)

def upload_file(file_path: str) -> str:
    """Upload image or video to Cloudinary, return public URL."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".mp4":
        result = cloudinary.uploader.upload(
            file_path,
            resource_type = "video"
        )
    else:
        result = cloudinary.uploader.upload(file_path)
    return result["secure_url"]

def send_line_message(text: str):
    """Send a text message via Line Messaging API."""
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "to": LINE_USER_ID,
            "messages": [{"type": "text", "text": text}],
        },
        timeout=10,
    )

def alert(file_path: str, conf: float, count: int):
    """Upload video/image and send Line notification."""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    ext = os.path.splitext(file_path)[1].lower()
    kind = "Video" if ext == ".mp4" else "Image"

    try:
        print(f"[Cloudinary] Uploading {kind.lower()}...")
        url = upload_file(file_path)
        print(f"[Cloudinary] Upload successful: {url}")

        msg = (
            f"🚨 Bicycle Theft Alert!\n"
            f"🕐 Time: {now}\n"
            f"👤 Person count: {count}\n"
            f"🎥 {kind}: {url}"
        )
        send_line_message(msg)
        print("[Line] Notification sent.")

    except Exception as e:
        msg = (
            f"🚨 Bicycle Theft Alert!\n"
            f"🕐 Time: {now}\n"
            f"👤 Person count: {count}\n"
            f"⚠️ Upload failed: {e}"
        )
        send_line_message(msg)
        print(f"[Line] Upload failed, sent text only: {e}")

def cleanup_images(image_dir: str, max_files: int = 50, max_days: int = 7):
    """Delete old files exceeding max count or age limit."""
    files = sorted(glob.glob(f"{image_dir}/*.jpg") + glob.glob(f"{image_dir}/*.mp4"))

    while len(files) > max_files:
        os.remove(files[0])
        print(f"[Cleanup] Deleted old file: {files[0]}")
        files.pop(0)

    cutoff = datetime.now() - timedelta(days=max_days)
    for f in files:
        modified = datetime.fromtimestamp(os.path.getmtime(f))
        if modified < cutoff:
            os.remove(f)
            print(f"[Cleanup] Deleted expired file: {f}")