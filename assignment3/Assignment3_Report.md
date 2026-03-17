# EEP 522 – Assignment 3: Creative Project
## Bicycle Theft Detection System on Raspberry Pi 4

**Author:** Yu-An Chen  
**Contact:** yuan1230@uw.edu  
**Course:** EEP 522 – Embedded And Real Time Systems  
**Platform:** Raspberry Pi 4 Model B (1GB) + Camera Module 3  
**Date:** March 2026  
**Estimated Time Spent:** ~48 hours  
**GitHub Repository:** https://github.com/CHENYUAN1230/eep522/tree/main/Finals/detector

---

## Abstract

This report documents the design, implementation, and evaluation of a real-time bicycle theft detection system deployed on a Raspberry Pi 4 Model B. Building upon the hardware characterization conducted in Assignments 1 and 2, this project applies YOLOv8 object detection to a continuous camera feed, monitors bicycle displacement and disappearance events, and delivers push notifications with video evidence to the owner via the LINE Messaging API. The system integrates multiprocessing, shared memory IPC, MJPEG live streaming, cloud video upload via Cloudinary, and a webhook-based chat bot for remote monitoring. This assignment reflects on how the Assignment 2 baseline characterization predicted, supported, or fell short of describing the platform's behavior under a real embedded workload.

---

## 1. Project Objective and Goals

### 1.1 Motivation

This project was born from personal experience — two bikes stolen, no warning, no evidence.

- **Incident 1 (Light Rail Station):** Bike parked outside, only the lock was left behind.
- **Incident 2 (Apartment Bike Room):** No cameras, no idea how the thief got in. Only an AirTag led to recovery — after hours of tracking.

Existing commercial solutions (GPS trackers, dedicated cameras) are expensive and require proprietary infrastructure. This project builds a low-cost, real-time alternative on Raspberry Pi 4 that detects theft the moment it happens and alerts the owner via LINE — no AirTag chase needed.

### 1.2 Project Goals

The system was designed to fulfill the following objectives:

1. Continuously monitor a bicycle using a Raspberry Pi Camera Module 3.
2. Detect persons and bicycles in real time using a YOLO neural network model.
3. Identify theft-indicative events: bicycle displacement and bicycle disappearance after person presence.
4. Record a pre-event rolling video buffer and upload it to cloud storage.
5. Push an alert with the video URL to the owner's LINE messaging account.
6. Provide a live MJPEG video stream accessible from any browser on the same network or via a public ngrok tunnel.
7. Accept remote commands via a LINE chatbot (e.g., `camera`, `status`) to retrieve stream URLs.

### 1.3 System Architecture Overview

The system is composed of four modules running as concurrent processes:

| Module | File | Role |
|--------|------|------|
| Detector | `main.py` | Camera capture, YOLO inference, theft logic |
| Streamer | `stream.py` | MJPEG live stream server (Flask, port 5000) |
| Webhook | `webhook.py` | LINE chatbot webhook server (Flask, port 5001) |
| Notifier | `notifier.py` | Cloudinary upload and LINE push notification |

The Detector and Streamer communicate via a shared memory buffer (`multiprocessing.Array`) and a mutex (`multiprocessing.Lock`), implementing a producer–consumer pattern consistent with the synchronization experiments in Assignment 2.



---

## 2. Implementation Details
### 2.1 Hardware and OS Setup

**Hardware:**
- Raspberry Pi 4 Model B (1GB)
- Raspberry Pi Camera Module 3 (Sony IMX708, 75° FOV)
- 3D-printed enclosure (custom shell for RPi 4 + Camera Module 3)

**OS Selection:**
The system initially ran Raspberry Pi OS 32-bit desktop image from Assignment 1. 
Under that configuration, the desktop environment consumed 300–400 MB of RAM at 
boot — leaving insufficient headroom for YOLOv8n (~170 MB) + OpenCV + Flask 
on a 1 GB board.

The OS was reinstalled to **Raspberry Pi OS Lite 64-bit (Bookworm)**, freeing 
~350 MB of RAM. This headless configuration was essential to making the full 
system fit within the 1 GB memory constraint.

### 2.2 Configuration (`config.py`)

All tunable parameters are centralized in `config.py` and loaded from a `.env` file using `python-dotenv`. This keeps API credentials out of source code and allows runtime reconfiguration without recompilation.

Key parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `CAMERA_WIDTH / HEIGHT` | 640 × 480 | Capture resolution |
| `FPS_LIMIT` | 5 | Max inference frames per second |
| `CONFIDENCE_THRESHOLD` | 0.5 | YOLO detection threshold |
| `BIKE_MOVE_THRESHOLD` | 60 px | Displacement to flag movement |
| `BIKE_MOVE_CONFIRM_FRAMES` | 3 | Consecutive frames to confirm move |
| `BIKE_MISSING_FRAMES` | 10 | Absence frames before flagging missing |
| `BIKE_GONE_CONFIRM_FRAMES` | 15 | Frames to confirm bike is truly gone |
| `BUFFER_SECONDS` | 30 | Rolling pre-event recording buffer |
| `COOLDOWN_SECONDS` | 10 | Minimum time between alerts |

### 2.3 Process Launch (`run.py`)

`run.py` creates the shared memory buffer and lock using Python's `multiprocessing` module, then launches the Detector and Streamer as separate OS processes:

```python
frame_size   = CAMERA_HEIGHT * CAMERA_WIDTH * 3   # 640×480×3 = 921,600 bytes
shared_frame = mp.Array("B", frame_size)
frame_lock   = mp.Lock()
```

Using `multiprocessing` rather than `threading` avoids Python's Global Interpreter Lock (GIL), allowing true parallel execution across the Cortex-A72 cores identified in Assignment 2.

### 2.4 Detector (`main.py`)

The detector loop runs at `FPS_LIMIT = 5` frames per second and performs the following steps each cycle:

1. **Capture** – acquire an RGB frame from the Pi Camera Module 3 via `picamera2`.
2. **Write to shared memory** – update the shared buffer under the mutex lock for the streamer to read.
3. **Inference** – run `yolov8n.pt` on the frame using Ultralytics YOLO API.
4. **Parse detections** – extract bounding boxes for `person` and `bicycle` classes above the confidence threshold.
5. **Theft logic** – evaluate two theft scenarios:
   - **Displacement:** If the bicycle's center moves more than `BIKE_MOVE_THRESHOLD` pixels for `BIKE_MOVE_CONFIRM_FRAMES` consecutive frames, flag as stolen.
   - **Disappearance:** If the bicycle is absent for `BIKE_MISSING_FRAMES` frames after a person was present, and then the person also leaves, confirm disappearance after `BIKE_GONE_CONFIRM_FRAMES` additional frames.
6. **Alert** – save the rolling buffer as an `.mp4` video and call `notifier.alert()`.
7. **FPS limiter** – sleep the remaining time in the frame interval.

The rolling pre-event buffer uses `collections.deque(maxlen=max_buffer)` to automatically discard the oldest frames, maintaining a configurable look-back window without unbounded memory growth.

### 2.5 Live Streaming (`stream.py`)

The streamer reads frames from shared memory and encodes them as JPEG using OpenCV, then serves them as a continuous MJPEG stream via Flask at `/video_feed`. An HTML landing page is served at `/` for browser access. The stream runs at approximately 10 FPS, independent of the detector's inference rate.

```python
def read_shared_frame():
    with _frame_lock:
        arr   = np.frombuffer(_shared_frame.get_obj(), dtype=np.uint8)
        frame = arr.reshape((CAMERA_HEIGHT, CAMERA_WIDTH, 3)).copy()
    _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return jpeg.tobytes()
```

### 2.6 Notification System (`notifier.py`)

When a theft event is confirmed, the notifier:

1. Uploads the `.mp4` video to Cloudinary using its Python SDK.
2. Sends a LINE push message to the configured `LINE_USER_ID` containing: timestamp, person count, confidence score, and the Cloudinary video URL.

A `cleanup_images()` function periodically removes files older than 7 days or in excess of 50 files, preventing SD card saturation — a practical concern identified in the Assignment 2 production analysis.

### 2.7 LINE Chatbot (`webhook.py`)

The webhook server handles incoming LINE messages and responds to three commands:

| Command | Response |
|---------|----------|
| `camera` / `live` | Current MJPEG stream URL (via ngrok) |
| `status` / `state` | System status summary |
| (other) | Help message listing available commands |

---

## 3. Self-Assessment of Assignment 2 Characterization

This section evaluates how well the Assignment 2 baseline characterization predicted or described the real behavior observed in this project.

### 3.1 CPU and Memory Bandwidth

**Prediction from A2:**
The 1080p @ 30 FPS memcpy workload produced ~10% CPU utilization and ~178 MB/s memory traffic. DRAM bandwidth measured at ~728 MB/s, well above that demand.

**Observed in A3:**
The system operates at 640×480 @ 5 FPS inference + 10 FPS MJPEG streaming. The actual memory traffic per inference cycle is:

```
640 × 480 × 3 bytes = 921,600 bytes ≈ 0.88 MB per frame
0.88 MB × 5 FPS ≈ 4.4 MB/s for inference path
0.88 MB × 10 FPS ≈ 8.8 MB/s for streaming path
```

This is far below the characterized DRAM bandwidth threshold. The bottleneck in this project is not memory bandwidth at all — it is **inference compute time** for YOLOv8n on the CPU.

**Characterization Gap:**
Assignment 2 focused on `memcpy`-based memory bandwidth, which does not represent neural network inference workloads. A more complete characterization would have included a lightweight YOLO or MobileNet inference benchmark to estimate per-frame latency and achievable FPS on the Cortex-A72 without a hardware accelerator.

**Recommendation:** Add a tflite or ONNX inference microbenchmark to the characterization phase to establish a realistic inference FPS baseline for CV workloads.

### 3.2 Real-Time Scheduling and Jitter

**Prediction from A2:**
Under idle conditions, the 30 FPS periodic task exhibited average jitter of ~78 µs and worst-case jitter of ~568 µs. Under CPU load, worst-case jitter increased to ~3.9 ms.

**Observed in A3:**
The detector loop uses `usleep()`-based FPS limiting at 5 FPS (200 ms target interval). At this low rate, even the worst-case 3.9 ms jitter from A2 represents only ~2% of the target interval:

```
3.9 ms / 200 ms = 1.95%
```

This means scheduling jitter is not a practical concern for the theft detection logic. Theft confirmation requires multiple consecutive frames (3–15 frames), making the system inherently tolerant of single-frame timing deviations.

**Characterization Success:**
The jitter characterization correctly indicated that soft real-time behavior is acceptable for camera-based monitoring workloads. The system does not require PREEMPT_RT or SCHED_FIFO for reliable operation.

### 3.3 Multithreading and Shared Memory

**Prediction from A2:**
Unsynchronized shared memory access between threads causes nondeterministic behavior and data corruption. Mutex protection is mandatory for correct producer–consumer pipelines.

**Observed in A3:**
The shared frame buffer between the Detector and Streamer is protected by `mp.Lock()`. Without this lock, the streamer could read a partially updated frame mid-write, producing a torn image artifact. The A2 experiments directly motivated this design decision. No frame corruption was observed during testing.

**Characterization Success:**
This was the most directly applicable result from A2. The producer–consumer synchronization pattern demonstrated in `camera_multithread_mutex_sim.c` maps exactly to the `main.py` ↔ `stream.py` interaction in A3.

### 3.4 GPIO and Peripheral Control

**Prediction from A2:**
`libgpiod` provides reliable GPIO control at low CPU cost. Polling-based control introduces up to 10 ms worst-case latency.

**Observed in A3:**
This project does not use GPIO. The camera interface uses `picamera2` (CSI-2 lane, not GPIO), and the network interface uses WiFi. The GPIO characterization was not directly applicable here.

**Characterization Gap:**
A more comprehensive peripheral characterization would have included the CSI-2 camera interface and evaluated `picamera2` frame delivery latency and consistency.

### 3.5 Boot Time 

**Prediction from A2:**
Total boot time was ~22 seconds, with variable userspace startup time (~18–19 s).

**Observed in A3:**
The 22-second boot time is acceptable for a stationary security device that remains powered continuously. However, if the device were to reboot due to power interruption, there is a ~22-second window during which the system is unprotected. This aligns with the A2 conclusion that the platform is unsuitable for applications requiring deterministic startup.

**Characterization Success:**
The boot time measurement correctly identified this limitation. In a hardened production deployment, an uninterruptible power supply (UPS) or battery-backed operation would be required.

---

## 4. Results and Demonstration

### 4.1 Theft Detection Behavior

The system correctly identifies two theft scenarios:

**Scenario A – Displacement Detection:**
When a person approaches the bicycle and moves it more than 60 pixels across 3 consecutive frames, the system triggers an alert. The rolling 30-second buffer captures the approach and movement event.

**Scenario B – Disappearance Detection:**
When a person is detected near the bicycle, then both the person and bicycle disappear from frame for 15 or more consecutive frames, the system confirms the bicycle is gone and triggers an alert.

**False positive mitigation:**
- The multi-frame confirmation windows (3 and 15 frames respectively) prevent single-frame detection noise from triggering alerts.
- The `COOLDOWN_SECONDS = 10` parameter prevents alert flooding.
- The bicycle disappearance logic explicitly waits for the person to also leave before starting the gone-confirmation countdown, preventing alerts when a person briefly blocks the camera's view of the bicycle.

### 4.2 Live Stream

The MJPEG stream at `http://<rpi-ip>:5000/` delivers approximately 10 FPS with JPEG quality set to 70, producing a smooth and identifiable live view suitable for remote monitoring. The public stream URL is distributed via ngrok and returned by the `camera` chatbot command.

### 4.3 LINE Notifications

Alert messages sent to LINE include:
- Timestamp of the event
- Person count and confidence score at time of detection
- Cloudinary video URL for immediate playback

### 4.4 System Resource Usage

Measured during steady-state operation at 640×480 @ 5 FPS inference:

| Resource | Usage |
|----------|-------|
| CPU utilization | ~60–75% (dominated by YOLOv8n inference) |
| RAM usage | ~380 MB (model + buffers + Flask) |
| Disk write rate | Minimal (only on alert events) |
| Network bandwidth (stream) | ~200–400 KB/s for MJPEG at 10 FPS |

> RAM headroom was only available after switching from the 32-bit desktop OS 
> to RPi OS Lite 64-bit — a direct consequence of the 1 GB memory constraint 
> identified during hardware setup.

The CPU utilization is significantly higher than predicted by the `memcpy`-based A2 benchmarks, confirming the gap noted in Section 3.1.

---

## 5. Successes and Failures

### 5.1 Successes

- Multiprocessing architecture correctly decouples inference and streaming latency.
- Shared memory IPC with mutex produces no frame corruption across extended test periods.
- Multi-frame confirmation logic effectively suppresses false positives from brief occlusions and detection noise.
- Rolling pre-event buffer captures the approach event without requiring continuous video recording to disk.
- LINE chatbot provides convenient remote access without opening a separate monitoring application.
- Cloud upload via Cloudinary eliminates dependency on local storage for evidence preservation.

### 5.2 Failures and Limitations

- **Inference FPS bottleneck:** YOLOv8n on the CPU achieves approximately 3–5 FPS at 640×480, leaving little headroom for higher resolution or more complex models. This was not predictable from the A2 memory bandwidth benchmarks.
- **No hardware acceleration:** The Raspberry Pi 4 lacks a dedicated NPU or GPU. A Raspberry Pi 5 with Hailo-8L AI HAT would significantly increase inference throughput.
- **Single-class bicycle tracking:** The current implementation tracks only the most recently seen bicycle center. In scenes with multiple bicycles, the tracking logic may produce false positives.
- **WiFi dependency:** The system requires a stable WiFi connection for LINE notifications. A cellular HAT (e.g., SIM7600) would improve reliability in outdoor deployments.
- **No authentication on stream:** The MJPEG stream at port 5000 is unauthenticated. In a production deployment, HTTPS and token-based access would be required.
- **SD card wear:** Continuous operation writes logs and detection frames to the microSD card. Long-term wear was identified as a concern in A2's production analysis and remains relevant here.

---

## 6. Recommended Enhancements to Characterization

Based on the gap analysis in Section 3, the following additions are recommended for a more complete embedded characterization in future assignments:

1. **Inference latency benchmark:** Measure per-frame YOLO or tflite inference time on the target board across model sizes (n, s, m). This directly predicts achievable FPS for computer vision workloads.

2. **CSI-2 camera interface characterization:** Measure `picamera2` frame delivery jitter and latency, as this is the actual camera interface used in embedded CV applications on the Raspberry Pi, not a synthetic `memcpy`.

3. **Thermal throttling under sustained CV load:** Run inference continuously for 30+ minutes and log CPU frequency via `/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq`. The Cortex-A72 throttles at 80°C, which can reduce effective FPS during sustained outdoor deployment.

4. **DRAM bandwidth under mixed workload:** Measure memory bandwidth while inference, streaming, and file I/O are running concurrently — not just in isolated memcpy benchmarks — to identify contention effects.

5. **Power consumption measurement:** Characterize current draw under idle, inference-only, and full-system workloads. This is essential for battery-backed deployments and thermal design in an enclosure.

---

## 7. Production Considerations

### 7.1 Limited Production (~1,000 units)

For a small-scale deployment (e.g., campus bike racks, parking facilities):

- The Raspberry Pi 4 is acceptable. Unit cost is manageable at this scale.
- A cooling case with passive heatsink is required for outdoor use.
- SD cards should be replaced with high-endurance industrial microSD (e.g., SanDisk Max Endurance) to mitigate write wear from video buffering.
- Each unit requires individual WiFi and LINE API credential configuration — manageable at 1,000 units with scripted provisioning.
- The 22-second boot time and non-deterministic startup are acceptable for a continuously powered security device.

### 7.2 Mass Production (>10,000 units)

At mass scale, the Raspberry Pi 4's limitations become significant:

- **Cost and availability:** The Raspberry Pi 4 is a consumer SBC not designed for mass production supply chains. Component availability is volatile.
- **Storage reliability:** SD card-based storage will require systematic replacement schedules. eMMC storage on a custom carrier board would be preferable.
- **Inference performance:** A custom board with an NPU (e.g., Rockchip RK3588 with 6 TOPS NPU, or Amlogic S905X4 with edge AI capability) would provide 5–10× the inference throughput at similar or lower cost per unit.
- **Software stack:** A hardened Linux image (Yocto or Buildroot) with read-only rootfs would improve reliability and boot time.
- **Thermal design:** Enclosure and thermal management must be validated for the target deployment environment (outdoor, -10°C to 50°C).

**Recommendation:** The current system is suitable for limited production and field prototyping. Mass production would require a custom PCB design around a more production-oriented SoC with integrated NPU and eMMC storage.

---

## 8. Conclusion

This project demonstrated a complete embedded system for bicycle theft detection, implemented entirely on the Raspberry Pi 4 Model B. The system integrates computer vision inference, shared memory IPC, web streaming, cloud storage, and push notification into a cohesive real-time monitoring pipeline.

The Assignment 2 characterization provided accurate and useful predictions in three areas: memory bandwidth capacity (confirming the system would not be memory-bandwidth-limited at the chosen resolution), scheduling jitter behavior (confirming soft real-time operation is sufficient), and shared memory synchronization requirements (directly motivating the mutex-protected producer–consumer design).

The characterization fell short in one key area: it did not include an inference latency benchmark, leading to an underestimate of CPU utilization under the actual YOLOv8n workload. Adding an inference-focused microbenchmark to the characterization stage would have better predicted the CPU bottleneck and might have motivated selecting a higher-performance model deployment strategy (e.g., ONNX Runtime, quantized tflite, or hardware acceleration) earlier in the design process.

Overall, the Raspberry Pi 4 proved to be a capable and cost-effective platform for this soft real-time embedded computer vision application. The project achieved all primary objectives and produced a functional, deployable prototype.

---

## 9. References

1. Ultralytics YOLOv8 Documentation
   https://docs.ultralytics.com/

2. Picamera2 Library Documentation
   https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf

3. LINE Messaging API Documentation
   https://developers.line.biz/en/docs/messaging-api/

4. Cloudinary Python SDK Documentation
   https://cloudinary.com/documentation/python_integration

5. Flask Documentation
   https://flask.palletsprojects.com/

6. Python multiprocessing — Process-based parallelism
   https://docs.python.org/3/library/multiprocessing.html

7. Raspberry Pi Ltd., "Raspberry Pi 4 Model B Documentation"
   https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

8. ARM Ltd., "ARM Cortex-A72 Technical Reference Manual"
   https://developer.arm.com/documentation/100095/latest/

9. ngrok Documentation
   https://ngrok.com/docs

10. OpenCV Documentation
    https://docs.opencv.org/

11. Molloy, Derek. *Exploring Raspberry Pi*. Wiley, 2016.

12. ChatGPT (OpenAI) — Used as an auxiliary tool for clarifying Python multiprocessing patterns, Flask MJPEG streaming implementation, and reviewing technical writing structure. 

---

## Appendix A: Source Code Overview

### A.1 Directory Structure

```
Finals/detector
├── run.py                  # Process launcher
├── main.py                 # Detector and theft logic
├── stream.py               # MJPEG stream server
├── webhook.py              # LINE chatbot webhook
├── notifier.py             # Alert and cloud upload
├── config.py               # Centralized configuration
├── .env                    # API credentials (not committed)
├── detected_images/        # Saved alert videos
└── yolov8n.pt              # YOLOv8 nano model weights
```

### A.2 Key Dependencies

```
ultralytics
picamera2
opencv-python
flask
requests
python-dotenv
cloudinary
numpy
```

### A.3 Running the System

```bash
# Install dependencies
pip install ultralytics picamera2 flask requests python-dotenv cloudinary numpy opencv-python

# Configure credentials
cp .env.example .env
# Edit .env with LINE_TOKEN, LINE_USER_ID, CLOUDINARY credentials

# Start ngrok tunnel (separate terminal)
ngrok http 5000

# Set ngrok URL
export NGROK_URL="https://xxxx.ngrok.io"

# Launch system
python run.py
```
