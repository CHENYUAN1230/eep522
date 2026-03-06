from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import time
import os
import numpy as np
import multiprocessing as mp
from collections import deque
from config import (
    MODEL_PATH, CAMERA_WIDTH, CAMERA_HEIGHT,
    CONFIDENCE_THRESHOLD, FPS_LIMIT, COOLDOWN_SECONDS,
    IMAGE_DIR, BIKE_MOVE_THRESHOLD, BIKE_MISSING_FRAMES,
    BIKE_MOVE_CONFIRM_FRAMES, BIKE_GONE_CONFIRM_FRAMES, BUFFER_SECONDS
)
from notifier import alert, cleanup_images

def get_center(x1, y1, x2, y2):
    """Return the center point of a bounding box."""
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** 0.5

def save_buffer_video(frames):
    """Save buffered frames as an mp4 video file."""
    timestamp  = time.strftime("%Y%m%d_%H%M%S")
    video_path = f"{IMAGE_DIR}/{timestamp}.mp4"
    fourcc     = cv2.VideoWriter_fourcc(*"mp4v")
    out        = cv2.VideoWriter(video_path, fourcc, FPS_LIMIT, (CAMERA_WIDTH, CAMERA_HEIGHT))
    for f in frames:
        out.write(f)
    out.release()
    print(f"Video saved: {video_path}")
    return video_path

def run_detector(shared_frame, frame_lock):
    """Main detection loop. Runs YOLO inference and writes frames to shared memory."""

    os.makedirs(IMAGE_DIR, exist_ok=True)

    print("Loading model...")
    model = YOLO(MODEL_PATH)
    print("Model loaded")

    # Initialize camera
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT)}
        )
    )
    picam2.start()
    time.sleep(2)
    print("Camera started")

    # Detection state variables
    last_alert        = 0
    frame_delay       = 1.0 / FPS_LIMIT
    last_bike_center  = None
    bike_missing      = 0
    bike_move_count   = 0
    bike_gone_count   = 0
    last_person_count = 0    # Last known person count for alert message
    last_person_conf  = 0.0  # Last known confidence for alert message

    # Rolling frame buffer: store last BUFFER_SECONDS * FPS_LIMIT frames
    max_buffer   = BUFFER_SECONDS * FPS_LIMIT
    frame_buffer = deque(maxlen=max_buffer)

    while True:
        start_time = time.time()
        cleanup_images(IMAGE_DIR)

        # 1. Capture frame from camera
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 2. Write annotated frame to shared memory for streaming
        with frame_lock:
            shared_arr = np.frombuffer(shared_frame.get_obj(), dtype=np.uint8)
            shared_arr[:] = frame.flatten()

        # 3. Run YOLO inference
        results = model(frame, verbose=False)

        detected_persons    = []
        current_bike_center = None

        for box in results[0].boxes:
            cls   = int(box.cls[0])
            label = model.names[cls]
            conf  = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw person bounding box
            if label == "person" and conf > CONFIDENCE_THRESHOLD:
                detected_persons.append(conf)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"person {conf:.2f}",
                    (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Draw bicycle bounding box
            if label == "bicycle" and conf > CONFIDENCE_THRESHOLD:
                current_bike_center = get_center(x1, y1, x2, y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 165, 0), 2)
                cv2.putText(frame, f"bicycle {conf:.2f}",
                    (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)

        # 4. Update last known person info when persons are visible
        if detected_persons:
            last_person_count = len(detected_persons)
            last_person_conf  = max(detected_persons)
            frame_buffer.append(frame.copy())

        # 5. Check bicycle status
        bike_stolen = False

        if current_bike_center is not None:
            # Bicycle is visible - check for displacement
            bike_missing    = 0
            bike_gone_count = 0
            if last_bike_center is not None:
                moved = distance(current_bike_center, last_bike_center)
                if moved > BIKE_MOVE_THRESHOLD:
                    bike_move_count += 1
                    print(f"Bicycle moving... ({bike_move_count}/{BIKE_MOVE_CONFIRM_FRAMES}) displacement: {moved:.1f}px")
                    if bike_move_count >= BIKE_MOVE_CONFIRM_FRAMES:
                        bike_stolen = True
                else:
                    bike_move_count = 0
            last_bike_center = current_bike_center
        else:
            # Bicycle not visible - check if truly gone
            if last_bike_center is not None:
                bike_missing += 1
                if bike_missing >= BIKE_MISSING_FRAMES:
                    if not detected_persons:
                        # No person in frame - start confirming bicycle is gone
                        bike_gone_count += 1
                        print(f"Confirming bicycle gone... ({bike_gone_count}/{BIKE_GONE_CONFIRM_FRAMES})")
                        if bike_gone_count >= BIKE_GONE_CONFIRM_FRAMES:
                            bike_stolen = True
                            bike_gone_count = 0
                            print("Bicycle confirmed missing! Sending alert!")
                    else:
                        # Person is blocking the bicycle - reset gone counter
                        bike_gone_count = 0
                        print("Bicycle occluded by person, continuing to record...")

        # 6. Trigger alert - save video and notify
        if bike_stolen and (time.time() - last_alert > COOLDOWN_SECONDS):
            if len(frame_buffer) > 0:
                video_path = save_buffer_video(list(frame_buffer))
                frame_buffer.clear()
                alert(video_path, last_person_conf, last_person_count)
            last_alert = time.time()

        # 7. FPS limiter
        elapsed = time.time() - start_time
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)

    picam2.stop()
