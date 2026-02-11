## CPU and Memory Bandwidth Characterization

### Objective

The objective of this experiment was to evaluate how image resolution and frame rate affect CPU utilization and memory bandwidth on the Raspberry Pi platform. The experiment simulates a camera workload by copying frame-sized memory buffers at a controlled frame rate.

This exploration aims to understand whether the system is compute-bound or memory-bound when processing image-like data streams.

---

### Experimental Setup

A C program was developed to simulate camera frame processing. The program:

- Allocates two frame-sized memory buffers
- Copies one buffer into another using `memcpy`
- Controls execution rate using `usleep()` to simulate FPS
- Runs for a fixed duration of 5 seconds
- Measures execution time using `clock_gettime()`
- CPU utilization measured using the Linux `time` utility

Frame size calculation:

- RGB888 format (3 bytes per pixel)
- Frame size = width × height × 3

Test configurations:

| Resolution | FPS | Frame Size |
|------------|-----|------------|
| 1280 × 720 | 15  | 2.64 MB |
| 1920 × 1080 | 30 | 5.93 MB |

---

### Results

#### 720p @ 15 FPS

## CPU and Memory Bandwidth Characterization

### Objective

The objective of this experiment was to evaluate how image resolution and frame rate affect CPU utilization and memory bandwidth on the Raspberry Pi platform. The experiment simulates a camera workload by copying frame-sized memory buffers at a controlled frame rate.

This exploration aims to understand whether the system is compute-bound or memory-bound when processing image-like data streams.

---

### Experimental Setup

A C program was developed to simulate camera frame processing. The program:

- Allocates two frame-sized memory buffers
- Copies one buffer into another using `memcpy`
- Controls execution rate using `usleep()` to simulate FPS
- Runs for a fixed duration of 5 seconds
- Measures execution time using `clock_gettime()`
- CPU utilization measured using the Linux `time` utility

Frame size calculation:

- RGB888 format (3 bytes per pixel)
- Frame size = width × height × 3

Test configurations:

| Resolution | FPS | Frame Size |
|------------|-----|------------|
| 1280 × 720 | 15  | 2.64 MB |
| 1920 × 1080 | 30 | 5.93 MB |

---

### Results

#### 720p @ 15 FPS
```
real ≈ 5.05 s
user ≈ 0.109 s
sys ≈ 0.004 s
```
Estimated CPU utilization:

CPU ≈ (user + sys) / real  
CPU ≈ (0.109 + 0.004) / 5.05 ≈ 2.2%

Theoretical memory traffic:

2.64 MB × 15 FPS ≈ 39.6 MB/s

---

#### 1080p @ 30 FPS
```
real ≈ 5.03 s
user ≈ 0.369 s
sys ≈ 0.025 s
```
Estimated CPU utilization:

CPU ≈ (0.369 + 0.025) / 5.03 ≈ 7.8%

Theoretical memory traffic:

5.93 MB × 30 FPS ≈ 177.9 MB/s

---

### Analysis

The experimental results show approximately a 4× increase in CPU utilization when increasing both resolution and frame rate.

This aligns with the theoretical scaling of memory traffic:

- Resolution increase ≈ 2.2×
- FPS increase ≈ 2×
- Total memory traffic ≈ 4.4×

The measured CPU increase closely matches the expected increase in memory bandwidth demand.

This indicates that the workload is primarily **memory-bandwidth bound**, rather than compute-bound.

---

### Observations

- CPU utilization remains relatively low (<10%) even at 1080p @ 30 FPS.
- The Raspberry Pi platform has significant headroom for additional processing.
- Frame processing workload scales approximately linearly with memory traffic.
- System behavior appears deterministic under controlled frame rates.

---

### Insight

In image-processing workloads, memory bandwidth can become the dominant bottleneck rather than arithmetic computation. Resolution and frame rate directly affect memory traffic, which in turn determines CPU utilization.

This experiment provides a baseline understanding of system capacity before introducing additional processing such as image analysis or multithreading.

---