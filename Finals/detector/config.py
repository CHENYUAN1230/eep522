from dotenv import load_dotenv
import os

load_dotenv()

# Line Messaging API
LINE_TOKEN   = os.getenv("LINE_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Model
MODEL_PATH = "yolov8n.pt"

# Camera
CAMERA_WIDTH  = 640
CAMERA_HEIGHT = 480

# Detection
CONFIDENCE_THRESHOLD = 0.5   # Minimum confidence score to accept a detection
FPS_LIMIT            = 5     # Maximum frames processed per second

# Notification
COOLDOWN_SECONDS = 10        # Minimum seconds between consecutive alerts

# Image storage
IMAGE_DIR = "detected_images"

# Bicycle displacement detection
BIKE_MOVE_THRESHOLD      = 60  # Pixel displacement threshold to consider the bicycle moved
BIKE_MISSING_FRAMES      = 10  # Frames the bicycle must be absent before flagging as missing
BIKE_MOVE_CONFIRM_FRAMES = 3   # Consecutive frames exceeding threshold to confirm movement
BIKE_GONE_CONFIRM_FRAMES = 15  # Frames after person leaves to confirm bicycle is truly gone

# Video recording buffer
BUFFER_SECONDS = 30  # Duration of the rolling pre-event frame buffer in seconds