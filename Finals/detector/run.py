import multiprocessing as mp
from config import CAMERA_WIDTH, CAMERA_HEIGHT
from main import run_detector
from stream import run_stream

if __name__ == "__main__":
    # Shared memory buffer: one RGB frame (HEIGHT x WIDTH x 3 bytes)
    frame_size   = CAMERA_HEIGHT * CAMERA_WIDTH * 3
    shared_frame = mp.Array("B", frame_size)
    frame_lock   = mp.Lock()

    detector_process = mp.Process(
        target=run_detector,
        args=(shared_frame, frame_lock),
        name="Detector"
    )
    stream_process = mp.Process(
        target=run_stream,
        args=(shared_frame, frame_lock),
        name="Streamer"
    )

    print("Starting detector process...")
    detector_process.start()

    print("Starting stream process...")
    stream_process.start()

    try:
        detector_process.join()
        stream_process.join()
    except KeyboardInterrupt:
        print("\nShutting down...")
        detector_process.terminate()
        stream_process.terminate()
        detector_process.join()
        stream_process.join()
        print("All processes stopped.")